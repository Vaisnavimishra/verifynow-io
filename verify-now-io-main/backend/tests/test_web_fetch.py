import httpx
import pytest
import respx

from app.services.web_fetch import fetch_url

HTML = """
<html>
<head>
  <title>Example Article</title>
  <meta property="og:site_name" content="Example News" />
  <meta property="og:description" content="A short description." />
  <meta property="article:published_time" content="2026-08-15T00:00:00Z" />
</head>
<body><p>This is the article body text.</p></body>
</html>
"""


@pytest.mark.asyncio
@respx.mock
async def test_fetch_url_extracts_metadata():
    respx.get("https://example.com/article").mock(
        return_value=httpx.Response(200, text=HTML, headers={"content-type": "text/html"})
    )

    page = await fetch_url("https://example.com/article")
    assert page.title == "Example Article"
    assert page.site_name == "Example News"
    assert page.meta_description == "A short description."
    assert page.published_time == "2026-08-15T00:00:00Z"
    assert "article body text" in page.text_excerpt
    assert page.fetch_error is None


@pytest.mark.asyncio
@respx.mock
async def test_fetch_url_handles_connection_error():
    respx.get("https://unreachable.example/page").mock(
        side_effect=httpx.ConnectError("boom")
    )

    page = await fetch_url("https://unreachable.example/page")
    assert page.fetch_error is not None
    assert page.text_excerpt == ""
