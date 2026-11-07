from __future__ import annotations

import argparse
import sys

from .agent import EvHunterAgent
from .criteria import Criteria
from .portals import PORTALS
from .report import to_console, to_markdown, write_json
from .store import Store


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ev-hunter",
        description=(
            "Agent przeszukujący polskie portale ogłoszeniowe w poszukiwaniu używanego, "
            "nieuszkodzonego samochodu elektrycznego do 150 000 zł i nie starszego niż 5 lat."
        ),
    )
    parser.add_argument("--max-price", type=int, default=150_000, help="maksymalna cena w PLN")
    parser.add_argument("--max-age", type=int, default=5, help="maksymalny wiek pojazdu w latach")
    parser.add_argument("--max-mileage", type=int, default=None, help="opcjonalny limit przebiegu w km")
    parser.add_argument("--portals", nargs="+", choices=sorted(PORTALS), default=sorted(PORTALS))
    parser.add_argument("--pages", type=int, default=1, help="liczba stron wyników na portal")
    parser.add_argument("--delay", type=float, default=2.0, help="opóźnienie między stronami w sekundach")
    parser.add_argument("--db", default="ev_hunter.db", help="plik bazy SQLite z już widzianymi ofertami")
    parser.add_argument("--report", help="ścieżka raportu Markdown")
    parser.add_argument("--json", help="ścieżka raportu JSON")
    parser.add_argument("--webhook", default=None, help="opcjonalny URL webhooka wysyłanego przy nowych ofertach")
    parser.add_argument("--watch", action="store_true", help="pętla monitorująca")
    parser.add_argument("--interval", type=int, default=30, help="minuty między skanami w trybie --watch")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    criteria = Criteria(
        max_price_pln=args.max_price,
        max_age_years=args.max_age,
        max_mileage_km=args.max_mileage,
    )
    agent = EvHunterAgent(
        criteria=criteria,
        portals=[PORTALS[name]() for name in args.portals],
        store=Store(args.db),
        pages=args.pages,
        delay=args.delay,
        webhook=args.webhook,
    )
    result = agent.run(watch=args.watch, interval_minutes=args.interval)
    if result is not None:
        print(to_console(result.matched))
        if args.report:
            with open(args.report, "w", encoding="utf-8") as handle:
                handle.write(to_markdown(result.matched))
        if args.json:
            write_json(args.json, result.matched)
    return 0


if __name__ == "__main__":
    sys.exit(main())
