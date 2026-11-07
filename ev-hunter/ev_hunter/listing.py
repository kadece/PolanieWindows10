from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


@dataclass
class Listing:
    portal: str
    url: str
    title: str
    price_pln: int | None
    year: int | None
    mileage_km: int | None
    fuel: str
    damaged: bool = False
    location: str = ""
    first_seen: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )

    @property
    def key(self) -> str:
        return f"{self.portal}:{self.url}"

    def to_dict(self) -> dict:
        return asdict(self)
