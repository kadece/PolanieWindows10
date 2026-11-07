from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .listing import Listing


def _sort(listings: Iterable[Listing]) -> list[Listing]:
    return sorted(listings, key=lambda l: (l.price_pln or 0))


def to_console(listings: Iterable[Listing]) -> str:
    items = _sort(listings)
    if not items:
        return "Brak ofert spełniających kryteria."
    lines = [f"{'Cena PLN':>10}  {'Rok':>4}  {'Przebieg':>10}  {'Portal':<8}  Oferta"]
    for l in items:
        mileage = f"{l.mileage_km} km" if l.mileage_km is not None else "-"
        year = str(l.year) if l.year is not None else "?"
        lines.append(
            f"{l.price_pln:>10}  {year:>4}  {mileage:>10}  {l.portal:<8}  {l.title}  {l.url}"
        )
    return "\n".join(lines)


def to_markdown(listings: Iterable[Listing]) -> str:
    items = _sort(listings)
    lines = [
        "# Raport EV Hunter",
        "",
        f"Wygenerowano: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"Ofert spełniających kryteria: {len(items)}",
        "",
        "| Cena (PLN) | Rok | Przebieg | Portal | Oferta |",
        "|---:|---:|---:|---|---|",
    ]
    for l in items:
        mileage = f"{l.mileage_km} km" if l.mileage_km is not None else "—"
        year = str(l.year) if l.year is not None else "?"
        lines.append(f"| {l.price_pln} | {year} | {mileage} | {l.portal} | [{l.title}]({l.url}) |")
    return "\n".join(lines) + "\n"


def write_json(path: str, listings: Iterable[Listing]) -> None:
    payload = [l.to_dict() for l in _sort(listings)]
    Path(path).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
