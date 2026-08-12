from __future__ import annotations

import json

import pytest

from world_weather import cli


class FakeClient:
    def nearby_search(self, **kwargs: object) -> list[dict[str, object]]:
        assert kwargs["radius_meters"] == 500.0
        assert kwargs["included_types"] == ["restaurant"]
        return [{"id": "place-1"}]

    def place_details(
        self, place_id: str, *, fields: tuple[str, ...]
    ) -> dict[str, object]:
        assert place_id == "ChIJ123"
        assert fields == ("id", "displayName")
        return {"id": place_id}


def test_nearby_cli_prints_json(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli.PlacesClient, "from_env", lambda **kwargs: FakeClient())

    result = cli.main(
        [
            "nearby",
            "--latitude",
            "28.4",
            "--longitude",
            "-81.5",
            "--radius-meters",
            "500",
            "--type",
            "restaurant",
        ]
    )

    assert result == 0
    assert json.loads(capsys.readouterr().out) == {"places": [{"id": "place-1"}]}


def test_details_cli_accepts_explicit_fields(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli.PlacesClient, "from_env", lambda **kwargs: FakeClient())

    result = cli.main(["details", "ChIJ123", "--fields", "id,displayName"])

    assert result == 0
    assert json.loads(capsys.readouterr().out) == {"id": "ChIJ123"}


def test_cli_reports_configuration_errors_without_traceback(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("GOOGLE_PLACES_API_KEY", raising=False)

    assert cli.main(["details", "ChIJ123"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "GOOGLE_PLACES_API_KEY is required" in captured.err
