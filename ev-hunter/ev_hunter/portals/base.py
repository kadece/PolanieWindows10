from __future__ import annotations

import re
import time
from abc import ABC, abstractmethod
from datetime import datetime

from ..criteria import Criteria
from ..http import fetch
from ..listing import Listing
from ..parsing import card_text, parse_mileages_km, parse_prices_pln, pick_year, strip_tags

ARTICLE_RE = re.compile(r"<article\b.*?</article>", re.IGNORECASE | re.DOTALL)
HEADING_RE = re.compile(r"<h[1-4][^>]*>(.*?)</h[1-4]>", re.IGNORECASE | re.DOTALL)


def _href_re(link_pattern: str) -> re.Pattern:
    return re.compile(
        r'<a\b[^>]*href="([^"]*' + link_pattern + r'[^"]*)"', re.IGNORECASE
    )


class Portal(ABC):
    name = "portal"
    base_url = ""
    link_pattern = r"/oferta/"
    fuel_marker = "elektrycz"

    @abstractmethod
    def search_url(self, criteria: Criteria, page: int = 1) -> str:
        raise NotImplementedError

    def parse(self, html_text: str, reference_year: int | None = None) -> list[Listing]:
        reference_year = reference_year or datetime.now().year
        listings = []
        for chunk in self._chunks(html_text):
            listing = self._parse_chunk(chunk, reference_year)
            if listing is not None:
                listings.append(listing)
        return listings

    def scan(self, criteria: Criteria, pages: int = 1, delay: float = 2.0) -> list[Listing]:
        found: list[Listing] = []
        for page in range(1, pages + 1):
            html_text = fetch(self.search_url(criteria, page))
            found.extend(self.parse(html_text, criteria.reference_year))
            if page < pages:
                time.sleep(delay)
        return found

    def _chunks(self, html_text: str) -> list[str]:
        articles = ARTICLE_RE.findall(html_text)
        if articles:
            return articles
        href_re = _href_re(self.link_pattern)
        matches = list(href_re.finditer(html_text))
        chunks = []
        for i, match in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(html_text)
            chunks.append(html_text[match.start() : end])
        return chunks

    def _parse_chunk(self, chunk: str, reference_year: int) -> Listing | None:
        href_re = _href_re(self.link_pattern)
        match = href_re.search(chunk)
        if not match:
            return None
        url = match.group(1)
        if url.startswith("/"):
            url = self.base_url.rstrip("/") + url
        text = card_text(chunk)
        heading = HEADING_RE.search(chunk)
        title = strip_tags(heading.group(1)) if heading else url
        prices = parse_prices_pln(text)
        mileages = parse_mileages_km(text)
        fuel = "electric" if self.fuel_marker in text.lower() else ""
        return Listing(
            portal=self.name,
            url=url,
            title=title or url,
            price_pln=max(prices) if prices else None,
            year=pick_year(text, reference_year),
            mileage_km=mileages[-1] if mileages else None,
            fuel=fuel,
            damaged=Criteria.text_looks_damaged(text),
        )
