from __future__ import annotations

import json
import time
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .criteria import Criteria
from .listing import Listing
from .portals import build_portals
from .store import Store


@dataclass
class ScanResult:
    scanned: int = 0
    matched: list[Listing] = field(default_factory=list)
    new: list[Listing] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class EvHunterAgent:
    def __init__(
        self,
        criteria: Criteria | None = None,
        portals=None,
        store: Store | None = None,
        pages: int = 1,
        delay: float = 2.0,
        webhook: str | None = None,
    ):
        self.criteria = criteria or Criteria()
        self.portals = portals if portals is not None else build_portals()
        self.store = store or Store()
        self.pages = pages
        self.delay = delay
        self.webhook = webhook

    def scan_once(self) -> ScanResult:
        result = ScanResult()
        for portal in self.portals:
            try:
                listings = portal.scan(self.criteria, pages=self.pages, delay=self.delay)
            except Exception as exc:
                result.errors.append(f"{portal.name}: {exc}")
                continue
            result.scanned += len(listings)
            matched = [l for l in listings if self.criteria.matches(l)]
            result.matched.extend(matched)
            result.new.extend(self.store.filter_new(matched))
        for listing in result.matched:
            self.store.mark(listing)
        if result.new and self.webhook:
            self._notify(result.new)
        return result

    def run(self, watch: bool = False, interval_minutes: int = 30) -> ScanResult | None:
        while True:
            result = self.scan_once()
            stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
            print(
                f"[{stamp}] zeskanowano={result.scanned} "
                f"pasujących={len(result.matched)} nowych={len(result.new)}"
            )
            for error in result.errors:
                print(f"  błąd: {error}")
            if not watch:
                return result
            time.sleep(interval_minutes * 60)

    def _notify(self, listings: list[Listing]) -> None:
        payload = json.dumps(
            {
                "event": "new_ev_listings",
                "count": len(listings),
                "listings": [l.to_dict() for l in listings],
            },
            ensure_ascii=False,
        ).encode("utf-8")
        request = urllib.request.Request(
            self.webhook, data=payload, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            response.read()
