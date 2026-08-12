#!/usr/bin/env bash
set -euo pipefail

uv lock --check
uv sync --all-groups --frozen
uv run ruff check world_weather scripts tests
uv run ruff format --check world_weather scripts tests
uv run pytest
uv run weather-places --help >/dev/null
uv run python scripts/google_places_requests.py --help >/dev/null
uv run pip-audit --skip-editable
