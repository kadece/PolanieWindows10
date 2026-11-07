from __future__ import annotations

import urllib.error
import urllib.request

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 ev-hunter/0.1 (personal use)"
)
DEFAULT_TIMEOUT = 25


class FetchError(Exception):
    pass


def fetch(url: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "pl-PL,pl;q=0.9",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except (urllib.error.URLError, OSError) as exc:
        raise FetchError(f"nie udało się pobrać {url}: {exc}") from exc
