import asyncio
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import rate_limit_dependency
from app.config import get_settings
from app.db.models import AnalysisRequest, ContentType, RequestStatus
from app.db.session import AsyncSessionLocal, get_db
from app.schemas.verification import (
    ContentTypeEnum,
    VerificationResultOut,
    VerifyRequestStatus,
    VerifySubmitResponse,
)
from app.services import kafka_bus
from app.services.document_parser import DocumentParseError, extract_text_from_bytes
from app.services.hashing import normalize_and_hash
from app.services.image_analysis import ImageAnalysisError, extract_claim_from_image
from app.services.pipeline import process_verification_request

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api", tags=["verification"])

MAX_UPLOAD_BYTES = settings.MAX_UPLOAD_MB * 1024 * 1024


async def _run_in_process(request_id: str) -> None:
    async with AsyncSessionLocal() as session:
        await process_verification_request(request_id, session)


@router.post("/verify", response_model=VerifySubmitResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_verification(
    content_type: ContentTypeEnum = Form(...),
    text: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    _rl: None = Depends(rate_limit_dependency),
):
    ct = ContentType(content_type.value)
    extracted_text: str | None = None

    if ct in (ContentType.TEXT, ContentType.URL, ContentType.VIDEO_URL):
        if not text or not text.strip():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "`text` is required for this content type.")
        input_summary = text.strip()
        if ct == ContentType.URL and not (
            input_summary.startswith("http://") or input_summary.startswith("https://")
        ):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "URL must start with http:// or https://")
        hash_value = input_summary

    elif ct == ContentType.DOCUMENT:
        if file is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "A file upload is required for `document`.")
        content = await file.read()
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "File too large.")
        try:
            extracted_text = extract_text_from_bytes(file.filename or "upload", content)
        except DocumentParseError as exc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
        input_summary = file.filename or "uploaded document"
        hash_value = extracted_text

    elif ct == ContentType.IMAGE:
        if file is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "A file upload is required for `image`.")
        content = await file.read()
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "File too large.")
        mime_type = file.content_type or "image/jpeg"
        try:
            extracted_text = await extract_claim_from_image(content, mime_type)
        except ImageAnalysisError as exc:
            logger.warning("Image claim extraction failed: %s", exc)
            extracted_text = None
        input_summary = file.filename or "uploaded image"
        hash_value = extracted_text or (file.filename or "uploaded image")

    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unsupported content type.")

    request = AnalysisRequest(
        content_type=ct,
        input_summary=input_summary[:2000],
        normalized_hash=normalize_and_hash(ct.value, hash_value),
        extracted_text=extracted_text,
        status=RequestStatus.PENDING,
    )
    db.add(request)
    await db.commit()
    await db.refresh(request)

    if settings.KAFKA_ENABLED:
        try:
            await kafka_bus.publish_verification_task(request.id)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to publish to Kafka, falling back to in-process processing")
            asyncio.create_task(_run_in_process(request.id))
    else:
        asyncio.create_task(_run_in_process(request.id))

    return VerifySubmitResponse(request_id=request.id, status=VerifyRequestStatus.pending)


@router.get("/verify/{request_id}", response_model=VerificationResultOut)
async def get_verification_result(request_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AnalysisRequest).where(AnalysisRequest.id == request_id)
    )
    request = result.scalar_one_or_none()
    if request is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Verification request not found.")

    await db.refresh(request, attribute_names=["sources"])

    return VerificationResultOut(
        request_id=request.id,
        content_type=request.content_type.value,
        status=request.status.value,
        input_summary=request.input_summary,
        verdict=request.verdict.value if request.verdict else None,
        confidence=request.confidence,
        reasoning=request.reasoning,
        content_published_date=request.content_published_date,
        website_metadata=request.website_metadata,
        ai_generated_signal=request.ai_generated_signal,
        evidence=[
            {
                "claim": s.claim,
                "stance": s.stance.value,
                "source_name": s.source_name,
                "source_url": s.source_url,
                "published_date": s.published_date,
                "excerpt": s.excerpt,
            }
            for s in request.sources
        ],
        limitations=request.limitations,
        error_message=request.error_message,
        from_cache=request.from_cache,
        created_at=request.created_at,
        updated_at=request.updated_at,
    )
