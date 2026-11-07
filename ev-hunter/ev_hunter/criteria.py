from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime

from .listing import Listing

DAMAGE_PATTERNS = (
    re.compile(r"(?<!nie)uszkodzon", re.IGNORECASE),
    re.compile(r"(?<!bez)powypadkow", re.IGNORECASE),
    re.compile(
        r"po wypadku|po kolizji|po stłuczce|szkoda całkowita|do naprawy|na części"
        r"|damaged|accident|collision|salvage",
        re.IGNORECASE,
    ),
)

ELECTRIC_MARKERS = ("elektrycz", "electric", "bev")


@dataclass
class Criteria:
    max_price_pln: int = 150_000
    max_age_years: int = 5
    require_electric: bool = True
    exclude_damaged: bool = True
    max_mileage_km: int | None = None
    reference_year: int = field(default_factory=lambda: datetime.now().year)

    @property
    def min_year(self) -> int:
        return self.reference_year - self.max_age_years

    @staticmethod
    def text_looks_damaged(text: str) -> bool:
        return any(p.search(text) for p in DAMAGE_PATTERNS)

    def check(self, listing: Listing) -> list[str]:
        reasons: list[str] = []
        if listing.price_pln is None or listing.price_pln > self.max_price_pln:
            reasons.append(f"cena {listing.price_pln} PLN poza limitem {self.max_price_pln} PLN")
        if listing.year is None or listing.year < self.min_year:
            reasons.append(f"rocznik {listing.year} starszy niż {self.min_year}")
        if self.require_electric and not any(
            m in listing.fuel.lower() for m in ELECTRIC_MARKERS
        ):
            reasons.append(f"napęd '{listing.fuel or 'nieznany'}' nie jest elektryczny")
        if self.exclude_damaged and (
            listing.damaged or self.text_looks_damaged(listing.title)
        ):
            reasons.append("wykryto oznaki uszkodzenia pojazdu")
        if self.max_mileage_km is not None and (
            listing.mileage_km is None or listing.mileage_km > self.max_mileage_km
        ):
            reasons.append(f"przebieg {listing.mileage_km} km poza limitem {self.max_mileage_km} km")
        return reasons

    def matches(self, listing: Listing) -> bool:
        return not self.check(listing)
