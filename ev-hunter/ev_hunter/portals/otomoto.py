from urllib.parse import urlencode

from ..criteria import Criteria
from .base import Portal


class OtomotoPortal(Portal):
    name = "otomoto"
    base_url = "https://www.otomoto.pl"
    link_pattern = r"/oferta/"

    def search_url(self, criteria: Criteria, page: int = 1) -> str:
        params = {
            "search[filter_enum_fuel_type]": "electric",
            "search[filter_float_price:to]": criteria.max_price_pln,
            "search[order]": "created_at:desc",
        }
        if page > 1:
            params["page"] = page
        return f"{self.base_url}/osobowe?{urlencode(params)}"
