from .base import Portal
from .gratka import GratkaPortal
from .olx import OlxPortal
from .otomoto import OtomotoPortal

PORTALS = {
    "gratka": GratkaPortal,
    "olx": OlxPortal,
    "otomoto": OtomotoPortal,
}


def build_portals(names: list[str] | None = None) -> list[Portal]:
    names = names or list(PORTALS)
    return [PORTALS[name]() for name in names]
