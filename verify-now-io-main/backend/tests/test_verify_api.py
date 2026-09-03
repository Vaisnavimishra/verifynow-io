import pytest

from app.schemas.verification import EvidenceItem, VerificationOutcome


def _outcome_verified():
    return VerificationOutcome(
        verdict="VERIFIED",
        confidence=88,
        reasoning="Multiple independent outlets confirm this event occurred.",
        evidence=[
            EvidenceItem(
                claim="The event happened as described.",
                stance="supports",
                source_name="Reuters",
                source_url="https://www.reuters.com/example-article",
                published_date="2026-08-20",
                excerpt="Independent reporting corroborates the timeline.",
            )
        ],
        limitations="Only two independent sources were found.",
    )


def _outcome_uncertain():
    return VerificationOutcome(
        verdict="UNCERTAIN",
        confidence=None,
        reasoning="No reliable independent sources could be found for this claim.",
        evidence=[],
        limitations="Insufficient evidence retrieved via web search.",
    )


@pytest.mark.asyncio
async def test_submit_text_returns_verified(client, monkeypatch):
    async def fake_verify_content(content_type, subject, context=""):
        return _outcome_verified()

    monkeypatch.setattr("app.services.pipeline.verify_content", fake_verify_content)

    resp = await client.post(
        "/api/verify",
        data={"content_type": "text", "text": "A real news event happened yesterday."},
    )
    assert resp.status_code == 202
    request_id = resp.json()["request_id"]

    result = await client.get(f"/api/verify/{request_id}")
    body = result.json()
    assert body["status"] == "completed"
    assert body["verdict"] == "VERIFIED"
    assert body["confidence"] == 88
    assert len(body["evidence"]) == 1
    assert body["evidence"][0]["source_url"] == "https://www.reuters.com/example-article"


@pytest.mark.asyncio
async def test_insufficient_evidence_returns_uncertain(client, monkeypatch):
    async def fake_verify_content(content_type, subject, context=""):
        return _outcome_uncertain()

    monkeypatch.setattr("app.services.pipeline.verify_content", fake_verify_content)

    resp = await client.post(
        "/api/verify",
        data={"content_type": "text", "text": "Some obscure unverifiable claim."},
    )
    request_id = resp.json()["request_id"]

    result = await client.get(f"/api/verify/{request_id}")
    body = result.json()
    assert body["verdict"] == "UNCERTAIN"
    assert body["confidence"] is None
    assert body["evidence"] == []


@pytest.mark.asyncio
async def test_missing_text_field_returns_400(client):
    resp = await client.post("/api/verify", data={"content_type": "text"})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_url_requires_scheme(client):
    resp = await client.post(
        "/api/verify", data={"content_type": "url", "text": "example.com"}
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_url_fetch_failure_returns_uncertain(client, monkeypatch):
    from app.services.web_fetch import FetchedPage

    async def fake_fetch_url(url, max_chars=6000):
        return FetchedPage(
            url=url,
            domain="doesnotexist.example",
            final_url=url,
            status_code=None,
            title=None,
            meta_description=None,
            site_name=None,
            published_time=None,
            text_excerpt="",
            fetch_error="Could not fetch URL: ConnectError",
        )

    monkeypatch.setattr("app.services.pipeline.fetch_url", fake_fetch_url)

    resp = await client.post(
        "/api/verify",
        data={"content_type": "url", "text": "https://doesnotexist.example/page"},
    )
    request_id = resp.json()["request_id"]

    result = await client.get(f"/api/verify/{request_id}")
    body = result.json()
    assert body["verdict"] == "UNCERTAIN"
    assert "Could not retrieve the page" in body["limitations"]


@pytest.mark.asyncio
async def test_document_upload_txt_is_verified(client, monkeypatch):
    async def fake_verify_content(content_type, subject, context=""):
        assert content_type == "document"
        assert "quarterly revenue" in subject.lower()
        return _outcome_verified()

    monkeypatch.setattr("app.services.pipeline.verify_content", fake_verify_content)

    files = {"file": ("claim.txt", b"Our quarterly revenue grew by 40%.", "text/plain")}
    resp = await client.post(
        "/api/verify", data={"content_type": "document"}, files=files
    )
    assert resp.status_code == 202
    request_id = resp.json()["request_id"]

    result = await client.get(f"/api/verify/{request_id}")
    assert result.json()["verdict"] == "VERIFIED"


@pytest.mark.asyncio
async def test_document_upload_unsupported_type_returns_400(client):
    files = {"file": ("claim.xyz", b"not a real doc", "application/octet-stream")}
    resp = await client.post(
        "/api/verify", data={"content_type": "document"}, files=files
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_get_unknown_request_returns_404(client):
    resp = await client.get("/api/verify/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_history_lists_submitted_requests(client, monkeypatch):
    async def fake_verify_content(content_type, subject, context=""):
        return _outcome_verified()

    monkeypatch.setattr("app.services.pipeline.verify_content", fake_verify_content)

    await client.post(
        "/api/verify", data={"content_type": "text", "text": "Some claim to check."}
    )
    resp = await client.get("/api/history")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 1
    assert items[0]["content_type"] == "text"
