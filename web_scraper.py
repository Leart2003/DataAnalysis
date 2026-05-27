from __future__ import annotations

from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from models import ScrapedAdvisory


class AdvisoryLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.current_href = ""
        self.capture_text = False
        self.current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attributes = dict(attrs)
        href = attributes.get("href") or ""
        if "/news-events/cybersecurity-advisories/" in href or "/news-events/alerts/" in href:
            self.current_href = href
            self.capture_text = True
            self.current_text = []

    def handle_data(self, data: str) -> None:
        if self.capture_text:
            self.current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or not self.capture_text:
            return
        title = " ".join("".join(self.current_text).split())
        if title:
            self.links.append((self.current_href, title))
        self.capture_text = False
        self.current_href = ""
        self.current_text = []


class CybersecurityWebScraper:
    def __init__(self) -> None:
        self.last_error: str | None = None

    def scrape_cisa_advisories(self, limit: int = 10) -> list[ScrapedAdvisory]:
        url = "https://www.cisa.gov/news-events/cybersecurity-advisories"
        request = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; DataAnalysisProject/1.0)"
            },
        )
        try:
            with urlopen(request, timeout=20) as response:
                html = response.read().decode("utf-8", errors="ignore")
        except Exception as error:  # pragma: no cover - depends on network
            self.last_error = str(error)
            return []

        parser = AdvisoryLinkParser()
        parser.feed(html)
        results: list[ScrapedAdvisory] = []
        seen: set[str] = set()
        for href, title in parser.links:
            full_url = urljoin(url, href)
            if full_url in seen or len(title) < 12:
                continue
            seen.add(full_url)
            results.append(ScrapedAdvisory(title=title, url=full_url))
            if len(results) >= limit:
                break
        return results

