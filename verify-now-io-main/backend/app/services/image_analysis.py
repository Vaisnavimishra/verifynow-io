"""
Image handling: extract the actual visible text/claim from an image using
OpenAI's multimodal input, so it can be run through the same evidence-based
verification pipeline as text. We never guess what an image "probably" says.
"""
import base64
import logging

from openai import OpenAIError

from app.config import get_settings
from app.services.openai_verification import get_client

logger = logging.getLogger(__name__)
settings = get_settings()

EXTRACTION_PROMPT = """Describe exactly what is visible in this image and
transcribe any text/captions shown verbatim if present. Then state, in one
sentence, the single main factual claim (if any) that this image appears to
be making. If there is no discernible factual claim, say so explicitly.
Do not speculate about anything not visibly present in the image."""


class ImageAnalysisError(Exception):
    pass


async def extract_claim_from_image(image_bytes: bytes, mime_type: str) -> str:
    if not settings.OPENAI_API_KEY:
        raise ImageAnalysisError("No OpenAI API key configured for image analysis.")

    b64 = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64}"

    client = get_client()
    try:
        response = await client.responses.create(
            model=settings.OPENAI_MODEL,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": EXTRACTION_PROMPT},
                        {"type": "input_image", "image_url": data_url},
                    ],
                }
            ],
        )
    except OpenAIError as exc:
        raise ImageAnalysisError(f"Image analysis failed: {exc}") from exc

    text = getattr(response, "output_text", None)
    if not text:
        raise ImageAnalysisError("Image analysis returned no content.")
    return text
