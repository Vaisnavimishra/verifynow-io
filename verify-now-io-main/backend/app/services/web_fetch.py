"""
Server-side fetching of submitted URLs.

This retrieves the ACTUAL page so the LLM verification layer has real,
grounded content to reason over (the site's own text/claims), separate from
whatever independent sources it finds via web search. We never fabricate
page content -- if the fetch fails, we say so and let the verdict be
UNCERTAIN rather than inventing anything.
"""
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

USER_AGENT = "VerifyNowBot/1.0 (+https://example.com/bot) content-verification-fetch"


@dataclass
class FetchedPage:
    url: str
    domain: str
    final_url: str
    status_code: int | None
    title: str | None
    meta_description: str | None
    site_name: str | None
    published_time: str | None
    text_excerpt: str
    fetch_error: str | None = None


def _first_meta(soup: BeautifulSoup, *names: str) -> str | None:
    for name in names:
        tag = soup.find("meta", attrs={"property": name}) or soup.find(
            "meta", attrs={"name": name}
        )
        if tag and tag.get("content"):
            return tag["content"].strip()
    return None


async def fetch_url(url: str, max_chars: int = 6000) -> FetchedPage:
    domain = urlparse(url).netloc

    try:
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=15.0, headers={"User-Agent": USER_AGENT}
        ) as client:
            resp = await client.get(url)
    except httpx.HTTPError as exc:
        return FetchedPage(
            url=url,
            domain=domain,
            final_url=url,
            status_code=None,
            title=None,
            meta_description=None,
            site_name=None,
            published_time=None,
            text_excerpt="",
            fetch_error=f"Could not fetch URL: {exc.__class__.__name__}: {exc}",
        )

    final_url = str(resp.url)
    final_domain = urlparse(final_url).netloc

    content_type = resp.headers.get("content-type", "")
    if "text/html" not in content_type and "application/xhtml" not in content_type:
        return FetchedPage(
            url=url,
            domain=final_domain or domain,
            final_url=final_url,
            status_code=resp.status_code,
            title=None,
            meta_description=None,
            site_name=None,
            published_time=None,
            text_excerpt="",
            fetch_error=f"Non-HTML content-type: {content_type or 'unknown'}",
        )

    soup = BeautifulSoup(resp.text, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else None
    meta_description = _first_meta(soup, "og:description", "description")
    site_name = _first_meta(soup, "og:site_name")
    published_time = _first_meta(
        soup, "article:published_time", "og:published_time", "datePublished"
    )

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = " ".join(soup.get_text(separator=" ").split())
    text_excerpt = text[:max_chars]

    return FetchedPage(
        url=url,
        domain=final_domain or domain,
        final_url=final_url,
        status_code=resp.status_code,
        title=title,
        meta_description=meta_description,
        site_name=site_name,
        published_time=published_time,
        text_excerpt=text_excerpt,
        fetch_error=None if resp.status_code < 400 else f"HTTP {resp.status_code}",
    )
