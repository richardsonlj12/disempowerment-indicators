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
    assert ua == "keel-indicators/0.1 (+https://github.com/richardsonlj12/keel)"


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


@responses.activate
def test_get_raises_source_error_on_4xx_with_status_and_body_prefix():
    # Stack Exchange signals throttling with HTTP 400 and a JSON error body.
    body = '{"error_id":502,"error_name":"throttle_violation","error_message":"' + "x" * 400 + '"}'
    responses.add(responses.GET, URL, status=400, body=body)
    with pytest.raises(SourceError) as excinfo:
        get(URL, expect="json")
    message = str(excinfo.value)
    assert "400" in message
    assert "throttle_violation" in message
    assert body[:200] in message
    assert body[:201] not in message
    assert len(responses.calls) == 1  # a 4xx other than 429 is not retried


@responses.activate
def test_get_allows_json_that_mentions_html_later_in_the_body():
    responses.add(responses.GET, URL, body='{"note": "this field contains <html> text", "ok": true}')
    assert get(URL, expect="json").status_code == 200


@responses.activate
def test_get_rejects_html_after_leading_whitespace_case_insensitive():
    responses.add(responses.GET, URL, body="\n\t <HTML><body>blocked</body></HTML>")
    with pytest.raises(SourceError):
        get(URL, expect="json")
