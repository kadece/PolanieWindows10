from __future__ import annotations

import sqlite3
from typing import Iterable

from .listing import Listing


class Store:
    def __init__(self, path: str = "ev_hunter.db"):
        self.path = str(path)
        self._conn = sqlite3.connect(self.path)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS seen ("
            "key TEXT PRIMARY KEY, portal TEXT, title TEXT, price_pln INTEGER, first_seen TEXT)"
        )
        self._conn.commit()

    def is_new(self, listing: Listing) -> bool:
        cur = self._conn.execute("SELECT 1 FROM seen WHERE key = ?", (listing.key,))
        return cur.fetchone() is None

    def mark(self, listing: Listing) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO seen (key, portal, title, price_pln, first_seen)"
            " VALUES (?, ?, ?, ?, ?)",
            (listing.key, listing.portal, listing.title, listing.price_pln, listing.first_seen),
        )
        self._conn.commit()

    def filter_new(self, listings: Iterable[Listing]) -> list[Listing]:
        return [listing for listing in listings if self.is_new(listing)]

    def close(self) -> None:
        self._conn.close()
