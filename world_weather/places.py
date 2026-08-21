"""A small, fail-closed client for Google Places API (New)."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping, Sequence
from typing import Any

import requests

PLACES_BASE_URL = "https://places.googleapis.com/v1"
DEFAULT_TIMEOUT_SECONDS = 10.0
MAX_RADIUS_METERS = 50_000.0
MAX_RESULTS = 20
MAX_TYPES = 50

DEFAULT_NEARBY_FIELDS = (
    "id",
    "displayName",
    "formattedAddress",
    "location",
    "primaryType",
    "types",
    "googleMapsUri",
)
DEFAULT_DETAILS_FIELDS = DEFAULT_NEARBY_FIELDS

_FIELD_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)*$")
_PLACE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,256}$")
_PLACE_TYPE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


class PlacesConfigurationError(ValueError):
    """The client or request configuration is invalid."""


class PlacesApiError(RuntimeError):
    """The Places service could not return a trusted response."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def _bounded_number(
    value: float,
    *,
    name: str,
    minimum: float,
    maximum: float,
    minimum_inclusive: bool = True,
) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise PlacesConfigurationError(f"{name} must be a number") from error

    lower_valid = result >= minimum if minimum_inclusive else result > minimum
    if not lower_valid or result > maximum:
        lower = "at least" if minimum_inclusive else "greater than"
        raise PlacesConfigurationError(
            f"{name} must be {lower} {minimum:g} and at most {maximum:g}"
        )
    return result


def _field_mask(fields: Sequence[str], *, prefix: str = "") -> str:
    if isinstance(fields, str):
        raise PlacesConfigurationError("fields must be a sequence, not one string")

    normalized: list[str] = []
    for field in fields:
        if not isinstance(field, str):
            raise PlacesConfigurationError("every response field must be a string")
        value = field.strip()
        if value == "*":
            raise PlacesConfigurationError(
                "wildcard field masks are disabled; request explicit fields"
            )
        if not _FIELD_PATTERN.fullmatch(value):
            raise PlacesConfigurationError(f"invalid Places field: {field!r}")
        if prefix and not value.startswith(f"{prefix}."):
            value = f"{prefix}.{value}"
        if value not in normalized:
            normalized.append(value)

    if not normalized:
        raise PlacesConfigurationError("at least one response field is required")
    return ",".join(normalized)


def _place_types(values: Sequence[str] | None) -> list[str]:
    if not values:
        return []
    if isinstance(values, str):
        raise PlacesConfigurationError("included_types must be a sequence")
    if len(values) > MAX_TYPES:
        raise PlacesConfigurationError(f"at most {MAX_TYPES} place types are allowed")

    normalized: list[str] = []
    for item in values:
        if not isinstance(item, str):
            raise PlacesConfigurationError("every place type must be a string")
        value = item.strip()
        if not _PLACE_TYPE_PATTERN.fullmatch(value):
            raise PlacesConfigurationError(f"invalid place type: {item!r}")
        if value not in normalized:
            normalized.append(value)
    return normalized


class PlacesClient:
    """Explicit, bounded access to Nearby Search and Place Details (New)."""

    def __init__(
        self,
        api_key: str,
        *,
        session: Any | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        key = api_key.strip()
        if not key:
            raise PlacesConfigurationError("a non-empty Places API key is required")
        self._api_key = key
        self._session = session or requests.Session()
        self._timeout_seconds = _bounded_number(
            timeout_seconds,
            name="timeout_seconds",
            minimum=0,
            maximum=120,
            minimum_inclusive=False,
        )

    @classmethod
    def from_env(
        cls,
        *,
        session: Any | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> PlacesClient:
        """Build a client from the only supported credential environment variable."""

        api_key = os.environ.get("GOOGLE_PLACES_API_KEY", "")
        if not api_key.strip():
            raise PlacesConfigurationError(
                "GOOGLE_PLACES_API_KEY is required; "
                "do not pass keys on the command line"
            )
        return cls(api_key, session=session, timeout_seconds=timeout_seconds)

    def nearby_search(
        self,
        *,
        latitude: float,
        longitude: float,
        radius_meters: float,
        included_types: Sequence[str] | None = None,
        max_results: int = 10,
        rank_preference: str = "POPULARITY",
        fields: Sequence[str] = DEFAULT_NEARBY_FIELDS,
    ) -> list[dict[str, Any]]:
        """Return at most 20 places from one bounded Nearby Search request."""

        lat = _bounded_number(latitude, name="latitude", minimum=-90, maximum=90)
        lng = _bounded_number(longitude, name="longitude", minimum=-180, maximum=180)
        radius = _bounded_number(
            radius_meters,
            name="radius_meters",
            minimum=0,
            maximum=MAX_RADIUS_METERS,
            minimum_inclusive=False,
        )
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise PlacesConfigurationError("max_results must be an integer")
        if not 1 <= max_results <= MAX_RESULTS:
            raise PlacesConfigurationError(
                f"max_results must be between 1 and {MAX_RESULTS}"
            )

        rank = rank_preference.strip().upper()
        if rank not in {"POPULARITY", "DISTANCE"}:
            raise PlacesConfigurationError(
                "rank_preference must be POPULARITY or DISTANCE"
            )

        payload: dict[str, Any] = {
            "maxResultCount": max_results,
            "rankPreference": rank,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": radius,
                }
            },
        }
        types = _place_types(included_types)
        if types:
            payload["includedTypes"] = types

        response = self._request_json(
            "POST",
            "/places:searchNearby",
            field_mask=_field_mask(fields, prefix="places"),
            payload=payload,
        )
        places = response.get("places", [])
        if not isinstance(places, list) or any(
            not isinstance(place, dict) for place in places
        ):
            raise PlacesApiError("Nearby Search returned an invalid places array")
        return places

    def place_details(
        self,
        place_id: str,
        *,
        fields: Sequence[str] = DEFAULT_DETAILS_FIELDS,
    ) -> dict[str, Any]:
        """Return one place resource using an explicit, non-wildcard field mask."""

        identifier = place_id.strip()
        if not _PLACE_ID_PATTERN.fullmatch(identifier):
            raise PlacesConfigurationError("place_id has an invalid format")

        return self._request_json(
            "GET",
            f"/places/{identifier}",
            field_mask=_field_mask(fields),
        )

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        field_mask: str,
        payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self._api_key,
            "X-Goog-FieldMask": field_mask,
        }
        try:
            response = self._session.request(
                method,
                f"{PLACES_BASE_URL}{path}",
                headers=headers,
                json=dict(payload) if payload is not None else None,
                timeout=self._timeout_seconds,
            )
        except requests.RequestException as error:
            raise PlacesApiError(
                "Places API request failed at the transport layer"
            ) from error

        try:
            body = response.json()
        except ValueError as error:
            raise PlacesApiError(
                "Places API returned a non-JSON response",
                status_code=getattr(response, "status_code", None),
            ) from error

        status_code = getattr(response, "status_code", None)
        if not isinstance(status_code, int):
            raise PlacesApiError("Places API response did not include an HTTP status")
        if not 200 <= status_code < 300:
            message = "request rejected"
            if isinstance(body, dict):
                error_body = body.get("error")
                if isinstance(error_body, dict) and isinstance(
                    error_body.get("message"), str
                ):
                    message = error_body["message"].replace(self._api_key, "[REDACTED]")
            raise PlacesApiError(
                f"Places API returned HTTP {status_code}: {message}",
                status_code=status_code,
            )
        if not isinstance(body, dict):
            raise PlacesApiError(
                "Places API returned a JSON value that was not an object",
                status_code=status_code,
            )
        return body
