import unittest
from pathlib import Path

from ev_hunter.criteria import Criteria
from ev_hunter.parsing import parse_mileages_km, parse_prices_pln, pick_year
from ev_hunter.portals import OtomotoPortal

FIXTURE = Path(__file__).parent / "fixtures" / "otomoto_sample.html"


class ParsingHelpersTest(unittest.TestCase):
    def test_price_with_nbsp(self):
        self.assertEqual(parse_prices_pln("Cena: 138\u00a0499 PLN"), [138499])

    def test_mileage_ignores_kmh(self):
        self.assertEqual(parse_mileages_km("3,8s/100kmh oraz 7 584 km"), [7584])

    def test_pick_year_ignores_future_years(self):
        self.assertEqual(pick_year("GWARANCJA do 10.09.2032, rok 2024", 2026), 2024)


class OtomotoParserTest(unittest.TestCase):
    def setUp(self):
        self.portal = OtomotoPortal()
        self.listings = self.portal.parse(
            FIXTURE.read_text(encoding="utf-8"), reference_year=2026
        )

    def test_parses_all_cards(self):
        self.assertEqual(len(self.listings), 3)

    def test_extracts_fields(self):
        good = next(l for l in self.listings if "Q4" in l.title)
        self.assertEqual(good.price_pln, 138499)
        self.assertEqual(good.year, 2024)
        self.assertEqual(good.mileage_km, 64000)
        self.assertEqual(good.fuel, "electric")
        self.assertFalse(good.damaged)
        self.assertEqual(
            good.url, "https://www.otomoto.pl/oferta/audi-q4-sportback-e-tron-45-2024-12345.html"
        )

    def test_marks_damaged_card(self):
        damaged = next(l for l in self.listings if "e-tron 55" in l.title)
        self.assertTrue(damaged.damaged)

    def test_criteria_filter_on_fixture(self):
        criteria = Criteria(reference_year=2026)
        matched = [l for l in self.listings if criteria.matches(l)]
        self.assertEqual(len(matched), 1)
        self.assertIn("Q4", matched[0].title)


if __name__ == "__main__":
    unittest.main()
