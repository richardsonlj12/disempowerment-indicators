"""HTTP helper: fixed User-Agent, retries, and HTML-instead-of-data detection."""

import time

import requests

USER_AGENT = (
    "disempowerment-indicators/0.1 "
    "(+https://github.com/richardsonlj12/disempowerment-indicators)"
)
RETRIES = 3
BACKOFF_SECONDS = 2.0
_sleep = time.sleep  # patched in tests so the suite stays fast


class SourceError(Exception):
    """A data source returned something unusable."""


def _retry_delay(response, attempt):
    header = response.headers.get("Retry-After")
    if header:
        try:
            return max(0.0, float(header))
        except ValueError:
            pass
    return BACKOFF_SECONDS * (2**attempt)


def get(url, params=None, expect="any", timeout=60):
    headers = {"User-Agent": USER_AGENT}
    for attempt in range(RETRIES + 1):
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        if response.status_code == 429 or response.status_code >= 500:
            if attempt < RETRIES:
                _sleep(_retry_delay(response, attempt))
                continue
            raise SourceError(f"{url} returned {response.status_code} after retries")
        break
    if 400 <= response.status_code < 500:
        # Stack Exchange signals throttling with HTTP 400 and a JSON error body.
        raise SourceError(f"{url} returned {response.status_code}: {response.text[:200]}")
    response.raise_for_status()
    if expect in ("csv", "json"):
        head = response.content.lstrip()[:16].lower()  # only the START of the body counts
        if head.startswith((b"<html", b"<!doctype")):
            raise SourceError(f"{url} returned HTML where {expect} was expected")
    return response
