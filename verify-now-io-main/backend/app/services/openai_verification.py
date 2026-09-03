"""
The verification/reasoning layer.

Design: the LLM is used ONLY as a reasoning layer over evidence it actually
retrieves via OpenAI's server-side web_search tool -- never as a standalone
source of truth. This is done in two passes:

  1. RESEARCH pass: model + web_search tool. It is instructed to search for
     independent sources, gather real URLs/dates/quotes, and think out loud.
  2. STRUCTURE pass: same research context, tools disabled, model is forced
     to emit strict JSON matching VerificationOutcome, using ONLY what it
     found in pass 1. Anything it could not find must be null, not guessed.

If either pass fails (network/API error, unparseable JSON, missing API key),
we surface an UNCERTAIN outcome with an honest limitation message -- we never
fall back to fabricated content.
"""
import json
import logging

from openai import AsyncOpenAI, OpenAIError
from pydantic import ValidationError

from app.config import get_settings
from app.schemas.verification import VerificationOutcome

logger = logging.getLogger(__name__)
settings = get_settings()

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


RESEARCH_SYSTEM_PROMPT = """You are a fact-verification research assistant.

Your job: investigate the submitted content using real web search and report
what you actually find. Rules you must follow strictly:

- Only report facts you found via search results you were actually given.
  Never state a fact you are not able to trace to a specific retrieved source.
- For every factual claim you evaluate, note the source name, source URL,
  and the source's publication date if shown.
- If you cannot find reliable independent evidence for a claim, say so
  explicitly rather than guessing.
- If sources disagree, describe the disagreement instead of picking a side.
- Being unable to verify something is a valid, common outcome -- report it
  as such rather than forcing a verdict.
- Do not use "the writing sounds natural/robotic" or similar stylistic
  observations as evidence of truth or falsehood -- that is a separate,
  much weaker signal about writing style, not about facts.
- If this is a website, separately track: (a) what the website itself
  claims about its own identity/history/founders, versus (b) what
  independent sources actually confirm. Do not blend the two.
"""

STRUCTURE_SYSTEM_PROMPT = """Convert the research notes below into a single
strict JSON object -- and NOTHING else, no markdown fences, no commentary.

Schema:
{
  "verdict": "VERIFIED" | "FALSE" | "MISLEADING" | "UNCERTAIN",
  "confidence": integer 0-100 or null (null unless the research genuinely
      supports a specific confidence level -- do not invent a number),
  "reasoning": string explaining how the verdict follows from the evidence,
  "content_published_date": string or null,
  "evidence": [
     {"claim": string, "stance": "supports"|"refutes"|"context",
      "source_name": string, "source_url": string,
      "published_date": string or null, "excerpt": string or null}
  ],
  "website_metadata": null OR {
     "domain": string or null, "site_name": string or null,
     "about": string or null, "founding_or_launch_date": string or null,
     "founder_or_organization": string or null, "company_info": string or null,
     "claims_made_by_site": [string], "independently_verified_claims": [string]
  },
  "ai_generated_signal": null OR {"likely_ai_generated": bool or null, "note": string or null},
  "limitations": string describing what could NOT be verified or checked
}

Rules:
- verdict must be UNCERTAIN if the research did not find sufficient
  independent evidence -- never guess VERIFIED/FALSE without real evidence.
- Every evidence[] item's source_url MUST be a URL that literally appeared
  in the research notes. Never invent a URL.
- website_metadata should only be non-null if the submitted content was a
  website/URL.
- excerpt must be a short paraphrase in your own words, never a long verbatim
  quotation.
"""


def _extract_output_text(response) -> str:
    """Handle both the convenience `.output_text` and raw `.output` shapes."""
    text = getattr(response, "output_text", None)
    if text:
        return text
    # Fallback: walk output items for message text (SDK version differences).
    chunks: list[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            value = getattr(content, "text", None)
            if value:
                chunks.append(value)
    return "\n".join(chunks)


async def _run_research_pass(content_type: str, subject: str, context: str) -> str:
    client = get_client()
    tools = [{"type": "web_search"}] if settings.OPENAI_WEB_SEARCH_ENABLED else []

    user_prompt = (
        f"Content type: {content_type}\n\n"
        f"Submitted content / claim to verify:\n{subject}\n\n"
        f"Additional context (page text, extracted document text, etc.):\n{context}\n\n"
        "Research this using web search and report your findings, including "
        "every source name, URL, and date you found."
    )

    response = await client.responses.create(
        model=settings.OPENAI_MODEL,
        instructions=RESEARCH_SYSTEM_PROMPT,
        input=user_prompt,
        tools=tools,
    )
    return _extract_output_text(response)


async def _run_structure_pass(research_notes: str) -> VerificationOutcome:
    client = get_client()

    response = await client.responses.create(
        model=settings.OPENAI_MODEL,
        instructions=STRUCTURE_SYSTEM_PROMPT,
        input=f"Research notes:\n{research_notes}",
    )
    raw_text = _extract_output_text(response).strip()

    # Defensive: strip accidental code fences.
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.lower().startswith("json"):
            raw_text = raw_text[4:]

    data = json.loads(raw_text)
    return VerificationOutcome.model_validate(data)


async def verify_content(content_type: str, subject: str, context: str = "") -> VerificationOutcome:
    """
    Full two-pass verification. Returns UNCERTAIN with a clear limitation
    message on any failure -- never raises to the caller for expected
    external-service failures.
    """
    if not settings.OPENAI_API_KEY:
        return VerificationOutcome(
            verdict="UNCERTAIN",
            confidence=None,
            reasoning="Verification could not run because no OpenAI API key is configured.",
            evidence=[],
            limitations=(
                "OPENAI_API_KEY is not set on the backend, so no web-search-grounded "
                "verification could be performed."
            ),
        )

    try:
        research_notes = await _run_research_pass(content_type, subject, context)
        outcome = await _run_structure_pass(research_notes)
        return outcome
    except OpenAIError as exc:
        logger.exception("OpenAI API error during verification")
        return VerificationOutcome(
            verdict="UNCERTAIN",
            confidence=None,
            reasoning="Verification service returned an error while researching this content.",
            evidence=[],
            limitations=f"Upstream verification API error: {exc.__class__.__name__}.",
        )
    except (json.JSONDecodeError, ValidationError) as exc:
        logger.exception("Failed to parse structured verification output")
        return VerificationOutcome(
            verdict="UNCERTAIN",
            confidence=None,
            reasoning="Verification research completed, but the result could not be structured reliably.",
            evidence=[],
            limitations=f"Could not parse a structured result from the model: {exc}",
        )
