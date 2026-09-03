import json
from types import SimpleNamespace

import pytest

from app.services import openai_verification


class FakeResponses:
    def __init__(self, texts):
        self._texts = texts
        self._call = 0

    async def create(self, **kwargs):
        text = self._texts[self._call]
        self._call += 1
        return SimpleNamespace(output_text=text)


class FakeClient:
    def __init__(self, texts):
        self.responses = FakeResponses(texts)


@pytest.mark.asyncio
async def test_verify_content_no_api_key_returns_uncertain(monkeypatch):
    monkeypatch.setattr(openai_verification.settings, "OPENAI_API_KEY", "")
    outcome = await openai_verification.verify_content("text", "some claim")
    assert outcome.verdict.value == "UNCERTAIN"
    assert outcome.confidence is None
    assert "OPENAI_API_KEY" in outcome.limitations


@pytest.mark.asyncio
async def test_verify_content_happy_path(monkeypatch):
    monkeypatch.setattr(openai_verification.settings, "OPENAI_API_KEY", "sk-test")

    research_text = "Found on Reuters (https://reuters.com/x, 2026-08-01): event confirmed."
    structured_json = json.dumps(
        {
            "verdict": "VERIFIED",
            "confidence": 90,
            "reasoning": "Confirmed by an independent outlet.",
            "content_published_date": None,
            "evidence": [
                {
                    "claim": "Event occurred",
                    "stance": "supports",
                    "source_name": "Reuters",
                    "source_url": "https://reuters.com/x",
                    "published_date": "2026-08-01",
                    "excerpt": "Independent confirmation of the event.",
                }
            ],
            "website_metadata": None,
            "ai_generated_signal": None,
            "limitations": "None.",
        }
    )

    fake_client = FakeClient([research_text, structured_json])
    monkeypatch.setattr(openai_verification, "get_client", lambda: fake_client)

    outcome = await openai_verification.verify_content("text", "some claim")
    assert outcome.verdict.value == "VERIFIED"
    assert outcome.confidence == 90
    assert outcome.evidence[0].source_url == "https://reuters.com/x"


@pytest.mark.asyncio
async def test_verify_content_bad_json_returns_uncertain(monkeypatch):
    monkeypatch.setattr(openai_verification.settings, "OPENAI_API_KEY", "sk-test")

    fake_client = FakeClient(["some research notes", "not valid json {{"])
    monkeypatch.setattr(openai_verification, "get_client", lambda: fake_client)

    outcome = await openai_verification.verify_content("text", "some claim")
    assert outcome.verdict.value == "UNCERTAIN"
    assert "could not be structured" in outcome.reasoning.lower()
