from __future__ import annotations

import html as html_lib
import re

NBSP = "\u00a0"
NARROW_NBSP = "\u202f"

_NUMBER = r"\d[\d\s" + NBSP + NARROW_NBSP + r"]*?"

PRICE_RE = re.compile("(" + _NUMBER + r")\s*PLN", re.IGNORECASE)
MILEAGE_RE = re.compile("(" + _NUMBER + r")\s*km(?![a-zA-Z/])", re.IGNORECASE)
YEAR_RE = re.compile(r"\b((?:19|20)\d{2})\b")
TAG_RE = re.compile(r"<[^>]+>")


def strip_tags(fragment: str) -> str:
    return re.sub(r"\s+", " ", html_lib.unescape(TAG_RE.sub(" ", fragment))).strip()


def card_text(fragment: str) -> str:
    return html_lib.unescape(TAG_RE.sub("|", fragment))


def _to_int(raw: str) -> int:
    return int(re.sub(r"\D", "", raw))


def parse_prices_pln(text: str) -> list[int]:
    return [_to_int(m.group(1)) for m in PRICE_RE.finditer(text)]


def parse_mileages_km(text: str) -> list[int]:
    return [_to_int(m.group(1)) for m in MILEAGE_RE.finditer(text)]


def parse_years(text: str) -> list[int]:
    return [int(y) for y in YEAR_RE.findall(text)]


def pick_year(text: str, current_year: int) -> int | None:
    valid = [y for y in parse_years(text) if 1990 <= y <= current_year + 1]
    return valid[-1] if valid else None
