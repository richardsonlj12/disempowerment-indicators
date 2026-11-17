import pytest
import responses

from indicators import http
from indicators.http import SourceError, get

URL = "https://example.org/data"


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    sleeps = []
    monkeypatch.setattr(http, "_sleep", sleeps.append)
    return sleeps


@responses.activate
def test_get_sets_user_agent():
    responses.add(responses.GET, URL, body="a,b\n1,2\n")
    get(URL, expect="csv")
    ua = responses.calls[0].request.headers["User-Agent"]
    assert ua == "disempowerment-indicators/0.1 (+https://github.com/richardsonlj12/disempowerment-indicators)"


@responses.activate
def test_get_rejects_html_when_csv_expected():
    responses.add(responses.GET, URL, body="  <!DOCTYPE html><html></html>")
    with pytest.raises(SourceError):
        get(URL, expect="csv")


@responses.activate
def test_get_allows_html_when_any_expected():
    responses.add(responses.GET, URL, body="<html></html>")
    assert get(URL).status_code == 200


@responses.activate
def test_get_retries_on_429(no_sleep):
    responses.add(responses.GET, URL, status=429, headers={"Retry-After": "7"})
    responses.add(responses.GET, URL, status=503)
    responses.add(responses.GET, URL, body="a\n1\n")
    r = get(URL, expect="csv")
    assert r.status_code == 200
    assert len(responses.calls) == 3
    assert no_sleep[0] == 7


@responses.activate
def test_get_raises_after_exhausting_retries():
    responses.add(responses.GET, URL, status=500)
    with pytest.raises(SourceError):
        get(URL)
    assert len(responses.calls) == 4
