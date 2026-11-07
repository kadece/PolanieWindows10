from urllib.parse import urlencode

from ..criteria import Criteria
from .base import Portal


class GratkaPortal(Portal):
    name = "gratka"
    base_url = "https://gratka.pl"
    link_pattern = r"/ogloszenie/"

    def search_url(self, criteria: Criteria, page: int = 1) -> str:
        params = {
            "cena-do": criteria.max_price_pln,
            "rok-od": criteria.min_year,
        }
        if page > 1:
            params["page"] = page
        return f"{self.base_url}/motoryzacja/samochody/osobowe?q=elektryczny&{urlencode(params)}"
