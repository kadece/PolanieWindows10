import unittest

from ev_hunter.criteria import Criteria
from ev_hunter.listing import Listing


def make_listing(**overrides) -> Listing:
    base = dict(
        portal="otomoto",
        url="https://www.otomoto.pl/oferta/test-1.html",
        title="Tesla Model 3 Long Range 2024",
        price_pln=120_000,
        year=2024,
        mileage_km=30_000,
        fuel="electric",
        damaged=False,
    )
    base.update(overrides)
    return Listing(**base)


class CriteriaTest(unittest.TestCase):
    def setUp(self):
        self.criteria = Criteria(reference_year=2026)

    def test_accepts_matching_listing(self):
        self.assertTrue(self.criteria.matches(make_listing()))

    def test_accepts_boundary_price_and_year(self):
        self.assertTrue(self.criteria.matches(make_listing(price_pln=150_000, year=2021)))

    def test_rejects_price_above_limit(self):
        listing = make_listing(price_pln=150_001)
        self.assertFalse(self.criteria.matches(listing))
        self.assertTrue(any("cena" in r for r in self.criteria.check(listing)))

    def test_rejects_too_old(self):
        self.assertFalse(self.criteria.matches(make_listing(year=2020)))

    def test_rejects_damaged_flag(self):
        self.assertFalse(self.criteria.matches(make_listing(damaged=True)))

    def test_rejects_damage_keyword_in_title(self):
        self.assertFalse(self.criteria.matches(make_listing(title="Audi e-tron powypadkowy")))

    def test_accepts_undamaged_keywords(self):
        listing = make_listing(title="Tesla Model 3 bezwypadkowa, nieuszkodzony")
        self.assertTrue(self.criteria.matches(listing))

    def test_rejects_non_electric_fuel(self):
        self.assertFalse(self.criteria.matches(make_listing(fuel="Diesel")))

    def test_max_mileage(self):
        criteria = Criteria(reference_year=2026, max_mileage_km=50_000)
        self.assertTrue(criteria.matches(make_listing()))
        self.assertFalse(criteria.matches(make_listing(mileage_km=80_000)))


if __name__ == "__main__":
    unittest.main()
