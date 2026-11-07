# EV Hunter

Agent (tylko biblioteka standardowa Pythona) przeszukujący popularne polskie portale
ogłoszeniowe w poszukiwaniu **używanego samochodu elektrycznego**:

- cena do **150 000 zł**,
- rocznik nie starszy niż **5 lat**,
- pojazd **bez uszkodzeń**.

Domyślnie monitorowane portale: **Otomoto**, **OLX**, **Gratka**.

## Kryteria (domyślne)

| Kryterium | Wartość |
|---|---|
| Maks. cena | 150 000 PLN |
| Maks. wiek | 5 lat (rocznik >= bieżący rok − 5) |
| Napęd | wyłącznie elektryczny |
| Stan | bez uszkodzeń (flaga portalu + heurystyka słów kluczowych: „powypadkowy”, „po wypadku”, „uszkodzony” itp., z wykluczeniem „bezwypadkowy” / „nieuszkodzony”) |
| Przebieg | opcjonalny limit przez `--max-mileage` |

Filtrowanie wykonywane jest **po stronie klienta** — parametry URL portalu są best-effort,
a ostateczną decyzję podejmuje `ev_hunter.criteria.Criteria`.

## Instalacja i uruchomienie

```bash
cd ev-hunter
pip install -e .          # opcjonalnie; można też użyć bezpośrednio:
python -m ev_hunter       # jednorazowe skanowanie wszystkich portali
```

Przydatne opcje:

```bash
python -m ev_hunter --portals otomoto olx --pages 2 \
    --report raport.md --json oferty.json
python -m ev_hunter --max-price 120000 --max-age 3 --max-mileage 60000
python -m ev_hunter --watch --interval 30          # pętla co 30 minut
python -m ev_hunter --webhook https://example.org/hook   # powiadomienie o nowych ofertach
```

Nowe oferty są zapamiętywane w lokalnej bazie SQLite (`--db`, domyślnie `ev_hunter.db`),
więc w trybie `--watch` każda oferta jest raportowana tylko raz.

## Architektura

```
ev_hunter/
  criteria.py     # Criteria: filtrowanie ofert wg ceny/rocznika/napędu/uszkodzeń
  listing.py      # model pojedynczej oferty
  parsing.py      # ekstrakcja ceny/rocznika/przebiegu z tekstu HTML
  http.py         # pobieranie stron (urllib, User-Agent, timeout)
  portals/        # adaptery: otomoto.py, olx.py, gratka.py (dziedziczą po base.Portal)
  store.py        # SQLite: deduplikacja już widzianych ofert
  report.py       # raporty: konsola / Markdown / JSON
  agent.py        # EvHunterAgent: skan -> filtrowanie -> deduplikacja -> raport/webhook
  __main__.py     # CLI (argparse)
tests/            # testy jednostkowe (unittest) + fixture HTML
```

Aby dodać nowy portal, wystarczy dopisać klasę dziedziczącą po `portals.base.Portal`
(`name`, `base_url`, `link_pattern`, `search_url`) i zarejestrować ją w `portals/__init__.py`.

## Testy

```bash
cd ev-hunter
python -m unittest discover -s tests -v
```

## Uwagi prawne i etyczne

- Agent pobiera wyłącznie **publicznie dostępne** strony wyników wyszukiwania, w niskim
  tempie (domyślne opóźnienie między stronami: 2 s, jedna strona na portal na skan).
- Należy respektować regulaminy i pliki `robots.txt` portali; narzędzie przeznaczone jest
  do użytku osobistego, nie do masowego scrapowania ani komercyjnego wykorzystania danych.
- Portale mogą zmieniać strukturę HTML — wtedy należy zaktualizować adapter w `portals/`.
