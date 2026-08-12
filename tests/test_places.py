from __future__ import annotations

from typing import Any

import pytest
import requests

from world_weather.places import (
    PlacesApiError,
    PlacesClient,
    PlacesConfigurationError,
)


class FakeResponse:
    def __init__(self, status_code: int, payload: object) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> object:
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


class FakeSession:
    def __init__(
        self,
        response: FakeResponse | None = None,
        error: requests.RequestException | None = None,
    ) -> None:
        self.response = response or FakeResponse(200, {})
        self.error = error
        self.calls: list[dict[str, Any]] = []

    def request(self, method: str, url: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": method, "url": url, **kwargs})
        if self.error:
            raise self.error
        return self.response


def test_nearby_search_uses_new_api_contract() -> None:
    session = FakeSession(
        FakeResponse(200, {"places": [{"id": "place-1", "displayName": {"text": "A"}}]})
    )
    client = PlacesClient("secret", session=session, timeout_seconds=7)

    result = client.nearby_search(
        latitude=28.4810971,
        longitude=-81.5089239,
        radius_meters=500,
        included_types=["restaurant", "cafe", "restaurant"],
        max_results=12,
        rank_preference="distance",
        fields=("id", "displayName", "formattedAddress"),
    )

    assert result == [{"id": "place-1", "displayName": {"text": "A"}}]
    assert len(session.calls) == 1
    call = session.calls[0]
    assert call["method"] == "POST"
    assert call["url"] == "https://places.googleapis.com/v1/places:searchNearby"
    assert call["timeout"] == 7
    assert call["headers"] == {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Goog-Api-Key": "secret",
        "X-Goog-FieldMask": ("places.id,places.displayName,places.formattedAddress"),
    }
    assert call["json"] == {
        "includedTypes": ["restaurant", "cafe"],
        "locationRestriction": {
            "circle": {
                "center": {"latitude": 28.4810971, "longitude": -81.5089239},
                "radius": 500.0,
            }
        },
        "maxResultCount": 12,
        "rankPreference": "DISTANCE",
    }


def test_nearby_search_allows_empty_results() -> None:
    session = FakeSession(FakeResponse(200, {}))
    client = PlacesClient("secret", session=session)

    assert client.nearby_search(latitude=0, longitude=0, radius_meters=1) == []


def test_place_details_uses_resource_get_and_unprefixed_fields() -> None:
    session = FakeSession(FakeResponse(200, {"id": "ChIJ123"}))
    client = PlacesClient("secret", session=session)

    result = client.place_details("ChIJ123", fields=("id", "displayName"))

    assert result == {"id": "ChIJ123"}
    call = session.calls[0]
    assert call["method"] == "GET"
    assert call["url"] == "https://places.googleapis.com/v1/places/ChIJ123"
    assert call["headers"]["X-Goog-FieldMask"] == "id,displayName"
    assert call["json"] is None


@pytest.mark.parametrize(
    ("overrides", "match"),
    [
        ({"latitude": -91}, "latitude"),
        ({"latitude": 91}, "latitude"),
        ({"longitude": -181}, "longitude"),
        ({"longitude": 181}, "longitude"),
        ({"radius_meters": 0}, "radius_meters"),
        ({"radius_meters": 50_001}, "radius_meters"),
        ({"max_results": 0}, "max_results"),
        ({"max_results": 21}, "max_results"),
        ({"max_results": True}, "max_results"),
        ({"rank_preference": "nearest"}, "rank_preference"),
        ({"included_types": ["not valid"]}, "place type"),
        ({"included_types": [None]}, "place type must be a string"),
        ({"fields": ("*",)}, "wildcard"),
        ({"fields": (None,)}, "response field must be a string"),
        ({"fields": ()}, "at least one"),
    ],
)
def test_nearby_search_rejects_invalid_bounds(
    overrides: dict[str, object], match: str
) -> None:
    client = PlacesClient("secret", session=FakeSession())
    arguments: dict[str, object] = {
        "latitude": 0,
        "longitude": 0,
        "radius_meters": 1,
    }
    arguments.update(overrides)

    with pytest.raises(PlacesConfigurationError, match=match):
        client.nearby_search(**arguments)  # type: ignore[arg-type]


@pytest.mark.parametrize("place_id", ["", "places/ChIJ123", "../secret", "a b"])
def test_place_details_rejects_invalid_place_ids(place_id: str) -> None:
    client = PlacesClient("secret", session=FakeSession())

    with pytest.raises(PlacesConfigurationError, match="place_id"):
        client.place_details(place_id)


def test_from_env_requires_a_nonempty_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GOOGLE_PLACES_API_KEY", raising=False)
    with pytest.raises(PlacesConfigurationError, match="GOOGLE_PLACES_API_KEY"):
        PlacesClient.from_env()

    monkeypatch.setenv("GOOGLE_PLACES_API_KEY", "  ")
    with pytest.raises(PlacesConfigurationError, match="GOOGLE_PLACES_API_KEY"):
        PlacesClient.from_env()


def test_from_env_passes_key_without_exposing_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = FakeSession(FakeResponse(200, {"id": "ChIJ123"}))
    monkeypatch.setenv("GOOGLE_PLACES_API_KEY", "environment-secret")

    client = PlacesClient.from_env(session=session)
    client.place_details("ChIJ123", fields=("id",))

    assert session.calls[0]["headers"]["X-Goog-Api-Key"] == "environment-secret"


def test_transport_errors_are_wrapped_without_the_key() -> None:
    session = FakeSession(error=requests.Timeout("wire timeout"))
    client = PlacesClient("secret", session=session)

    with pytest.raises(PlacesApiError, match="transport layer") as raised:
        client.place_details("ChIJ123", fields=("id",))
    assert "secret" not in str(raised.value)


def test_http_errors_are_wrapped_and_key_is_redacted() -> None:
    session = FakeSession(
        FakeResponse(
            403,
            {"error": {"message": "key secret is not authorized"}},
        )
    )
    client = PlacesClient("secret", session=session)

    with pytest.raises(PlacesApiError, match=r"HTTP 403.*\[REDACTED\]") as raised:
        client.place_details("ChIJ123", fields=("id",))
    assert raised.value.status_code == 403
    assert "secret" not in str(raised.value)


def test_non_json_response_fails_closed() -> None:
    session = FakeSession(FakeResponse(502, ValueError("not JSON")))
    client = PlacesClient("secret", session=session)

    with pytest.raises(PlacesApiError, match="non-JSON") as raised:
        client.place_details("ChIJ123", fields=("id",))
    assert raised.value.status_code == 502


@pytest.mark.parametrize(
    ("payload", "match"),
    [
        ([{"id": "place-1"}], "not an object"),
        ({"places": {}}, "invalid places array"),
        ({"places": ["place-1"]}, "invalid places array"),
    ],
)
def test_response_shape_drift_fails_closed(payload: object, match: str) -> None:
    session = FakeSession(FakeResponse(200, payload))
    client = PlacesClient("secret", session=session)

    with pytest.raises(PlacesApiError, match=match):
        client.nearby_search(latitude=0, longitude=0, radius_meters=1)
