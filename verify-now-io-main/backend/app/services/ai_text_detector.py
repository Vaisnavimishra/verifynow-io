"""
Optional secondary signal: does this text look AI-generated?

This is DELIBERATELY never used to produce or influence the factual verdict
(VERIFIED/FALSE/MISLEADING/UNCERTAIN) -- per spec, AI-generated-style is not
evidence of truth or falsehood. It is surfaced to the user only as a
separate, clearly-labeled signal.

Disabled by default. Set AI_TEXT_DETECTOR_MODEL to a HuggingFace text-
classification model id (e.g. "roberta-base-openai-detector") to enable it.
Loaded lazily so the backend can start and verify content without this
dependency ever having to download model weights.
"""
import logging

from app.config import get_settings
from app.schemas.verification import AIGeneratedSignal

logger = logging.getLogger(__name__)
settings = get_settings()

_pipeline = None
_load_failed = False


def _get_pipeline():
    global _pipeline, _load_failed
    if _pipeline is not None or _load_failed:
        return _pipeline
    if not settings.AI_TEXT_DETECTOR_MODEL:
        return None
    try:
        from transformers import pipeline  # local import: optional heavy dependency

        _pipeline = pipeline("text-classification", model=settings.AI_TEXT_DETECTOR_MODEL)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to load AI text detector model; disabling this signal")
        _load_failed = True
        _pipeline = None
    return _pipeline


def detect(text: str) -> AIGeneratedSignal | None:
    pipe = _get_pipeline()
    if pipe is None or not text.strip():
        return None
    try:
        result = pipe(text[:2000])[0]
        label = str(result.get("label", "")).lower()
        score = float(result.get("score", 0.0))
        likely_ai = "fake" in label or "ai" in label or "gpt" in label
        return AIGeneratedSignal(
            likely_ai_generated=likely_ai if score >= 0.6 else None,
            note=(
                f"Secondary stylistic signal only (model={settings.AI_TEXT_DETECTOR_MODEL}, "
                f"label={label}, score={score:.2f}). Not used as factual evidence."
            ),
        )
    except Exception:  # noqa: BLE001
        logger.exception("AI text detector inference failed")
        return None
