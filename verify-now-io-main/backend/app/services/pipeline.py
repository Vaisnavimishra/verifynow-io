"""
The actual verification pipeline. This is the single place that turns a
stored AnalysisRequest into a completed result. Called from:
  - the Kafka worker (production path), or
  - an in-process asyncio background task (KAFKA_ENABLED=false, local dev).

Either way this is real processing -- fetch/parse the real content, call the
real (web-search-grounded) verification service, and persist real results.
"""
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AnalysisRequest, ContentType, EvidenceSource, RequestStatus, Verdict
from app.services import ai_text_detector
from app.services.cache import get_cached_result, set_cached_result
from app.services.openai_verification import verify_content
from app.services.web_fetch import fetch_url

logger = logging.getLogger(__name__)

CACHEABLE_TYPES = {ContentType.TEXT, ContentType.URL}


async def _build_subject_and_context(request: AnalysisRequest) -> tuple[str, str, str | None]:
    """
    Returns (subject, context, hard_error).
    hard_error, if set, means we should short-circuit to UNCERTAIN without
    calling the LLM (e.g. the URL could not be fetched at all).
    """
    if request.content_type == ContentType.TEXT:
        return request.input_summary, "", None

    if request.content_type == ContentType.URL:
        page = await fetch_url(request.input_summary)
        if page.fetch_error and not page.text_excerpt:
            return (
                request.input_summary,
                "",
                f"Could not retrieve the page: {page.fetch_error}",
            )
        context = (
            f"Domain: {page.domain}\n"
            f"Site name (from page metadata): {page.site_name or 'unknown'}\n"
            f"Title: {page.title or 'unknown'}\n"
            f"Meta description: {page.meta_description or 'unknown'}\n"
            f"Published time (from page metadata, if any): {page.published_time or 'unknown'}\n"
            f"Page text excerpt:\n{page.text_excerpt}"
        )
        return request.input_summary, context, None

    if request.content_type in (ContentType.DOCUMENT, ContentType.IMAGE):
        if not request.extracted_text:
            return (
                request.input_summary,
                "",
                "No extractable text was available for this submission.",
            )
        return request.extracted_text, "", None

    if request.content_type == ContentType.VIDEO_URL:
        page = await fetch_url(request.input_summary)
        context = (
            f"Video URL metadata only (full video/transcript analysis is not implemented):\n"
            f"Title: {page.title or 'unknown'}\n"
            f"Description: {page.meta_description or 'unknown'}\n"
            f"{('Fetch error: ' + page.fetch_error) if page.fetch_error else ''}"
        )
        return request.input_summary, context, None

    return request.input_summary, "", "Unsupported content type."


async def process_verification_request(request_id: str, session: AsyncSession) -> None:
    result = await session.execute(
        select(AnalysisRequest).where(AnalysisRequest.id == request_id)
    )
    request = result.scalar_one_or_none()
    if request is None:
        logger.error("process_verification_request: request %s not found", request_id)
        return

    request.status = RequestStatus.PROCESSING
    await session.commit()

    try:
        # Cache check (text/url only -- documents/images are per-upload).
        if request.content_type in CACHEABLE_TYPES:
            cached = await get_cached_result(request.normalized_hash)
            if cached is not None:
                _apply_outcome_dict(request, cached)
                request.from_cache = True
                request.status = RequestStatus.COMPLETED
                await session.execute(
                    EvidenceSource.__table__.delete().where(
                        EvidenceSource.analysis_request_id == request.id
                    )
                )
                for ev in cached.get("evidence", []):
                    session.add(
                        EvidenceSource(
                            analysis_request_id=request.id,
                            claim=ev["claim"],
                            stance=ev["stance"],
                            source_name=ev["source_name"],
                            source_url=ev["source_url"],
                            published_date=ev.get("published_date"),
                            excerpt=ev.get("excerpt"),
                        )
                    )
                await session.commit()
                return

        subject, context, hard_error = await _build_subject_and_context(request)

        if hard_error:
            request.verdict = Verdict.UNCERTAIN
            request.confidence = None
            request.reasoning = "Verification could not be completed."
            request.limitations = hard_error
            request.status = RequestStatus.COMPLETED
            await session.commit()
            return

        outcome = await verify_content(request.content_type.value, subject, context)

        # Secondary, clearly-separate AI-generated-text signal (best effort, optional).
        if outcome.ai_generated_signal is None and request.content_type in (
            ContentType.TEXT,
            ContentType.DOCUMENT,
        ):
            outcome.ai_generated_signal = ai_text_detector.detect(subject)

        outcome_dict = outcome.model_dump(mode="json")
        _apply_outcome_dict(request, outcome_dict)
        request.status = RequestStatus.COMPLETED

        for ev in outcome.evidence:
            session.add(
                EvidenceSource(
                    analysis_request_id=request.id,
                    claim=ev.claim,
                    stance=ev.stance.value,
                    source_name=ev.source_name,
                    source_url=ev.source_url,
                    published_date=ev.published_date,
                    excerpt=ev.excerpt,
                )
            )

        await session.commit()

        if request.content_type in CACHEABLE_TYPES:
            await set_cached_result(request.normalized_hash, outcome_dict)

    except Exception as exc:  # noqa: BLE001
        logger.exception("Verification pipeline failed for request %s", request_id)
        request.status = RequestStatus.FAILED
        request.error_message = f"{exc.__class__.__name__}: {exc}"
        await session.commit()


def _apply_outcome_dict(request: AnalysisRequest, outcome: dict) -> None:
    request.verdict = outcome["verdict"]
    request.confidence = outcome.get("confidence")
    request.reasoning = outcome.get("reasoning")
    request.content_published_date = outcome.get("content_published_date")
    request.website_metadata = outcome.get("website_metadata")
    request.ai_generated_signal = outcome.get("ai_generated_signal")
    request.limitations = outcome.get("limitations")
