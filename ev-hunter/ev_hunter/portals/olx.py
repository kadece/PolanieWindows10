from urllib.parse import urlencode

from ..criteria import Criteria
from .base import Portal


class OlxPortal(Portal):
    name = "olx"
    base_url = "https://www.olx.pl"
    link_pattern = r"/d/oferta/"

    def search_url(self, criteria: Criteria, page: int = 1) -> str:
        params = {
            "search[filter_float_price:to]": criteria.max_price_pln,
            "search[filter_int_year:from]": criteria.min_year,
        }
        if page > 1:
            params["page"] = page
        return f"{self.base_url}/motoryzacja/samochody/q-elektryczny/?{urlencode(params)}"
