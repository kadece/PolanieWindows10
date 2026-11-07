from __future__ import annotations

from typing import Annotated

from mistralai import agents
from pydantic import Field

from .agent import EvHunterAgent
from .criteria import Criteria
from .portals import PORTALS, build_portals
from .store import Store


@agents.tool
def search_ev_listings(
    max_price_pln: Annotated[int, Field(description="Maksymalna cena pojazdu w PLN.")] = 150_000,
    max_age_years: Annotated[int, Field(description="Maksymalny wiek pojazdu w latach (rocznik >= bieżący rok minus ten parametr).")] = 5,
    max_mileage_km: Annotated[int | None, Field(description="Opcjonalny maksymalny przebieg w kilometrach.")] = None,
    portals: Annotated[list[str] | None, Field(description="Portale do przeszukania, np. ['otomoto', 'olx', 'gratka']. Puste oznacza wszystkie.")] = None,
    pages: Annotated[int, Field(description="Liczba stron wyników na portal (1-5).")] = 1,
) -> dict:
    """Przeszukuje polskie portale ogłoszeniowe (Otomoto, OLX, Gratka) w poszukiwaniu
    używanego, nieuszkodzonego samochodu elektrycznego i zwraca listę pasujących ofert
    z ceną, rocznikiem, przebiegiem i linkiem."""
    unknown = [p for p in (portals or []) if p not in PORTALS]
    if unknown:
        raise agents.ToolError(
            f"Nieznane portale: {unknown}. Dostępne: {sorted(PORTALS)}."
        )
    if not 1 <= pages <= 5:
        raise agents.ToolError("Parametr pages musi być w zakresie 1-5.")
    criteria = Criteria(
        max_price_pln=max_price_pln,
        max_age_years=max_age_years,
        max_mileage_km=max_mileage_km,
    )
    hunter = EvHunterAgent(
        criteria=criteria,
        portals=build_portals(portals),
        store=Store(":memory:"),
        pages=pages,
        delay=2.0,
    )
    result = hunter.scan_once()
    matched = sorted(result.matched, key=lambda l: (l.price_pln or 0))
    return {
        "scanned": result.scanned,
        "matched_count": len(matched),
        "matched": [l.to_dict() for l in matched],
        "errors": result.errors,
    }


agent = agents.Agent(
    model="mistral-large-4-0",
    name="ev-hunter",
    description=(
        "Agent wyszukujący używane, nieuszkodzone samochody elektryczne "
        "na polskich portalach ogłoszeniowych (Otomoto, OLX, Gratka)."
    ),
    instructions=(
        "Jesteś asystentem zakupu samochodu elektrycznego. Gdy użytkownik prosi o znalezienie "
        "auta, wywołaj narzędzie search_ev_listings z odpowiednimi kryteriami (domyślnie: cena do "
        "150 000 zł, wiek do 5 lat, bez uszkodzeń) i przedstaw wyniki jako listę ofert: tytuł, cena, "
        "rocznik, przebieg, portal i link. Posortuj rekomendacje od najlepszej (najniższa cena przy "
        "spełnionych kryteriach). Zawsze podaj użyte kryteria. Odpowiadaj po polsku. Pamiętaj, że "
        "filtr 'bez uszkodzeń' jest heurystyką — zaleć sprawdzenie historii pojazdu (CEPiK) przed zakupem."
    ),
    tools=[search_ev_listings],
)
