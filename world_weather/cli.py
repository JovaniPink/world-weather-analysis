"""Command-line interface for the bounded Places API (New) client."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from .places import (
    DEFAULT_DETAILS_FIELDS,
    DEFAULT_NEARBY_FIELDS,
    PlacesApiError,
    PlacesClient,
    PlacesConfigurationError,
)


def _fields(value: str) -> tuple[str, ...]:
    fields = tuple(item.strip() for item in value.split(",") if item.strip())
    if not fields:
        raise argparse.ArgumentTypeError("provide at least one comma-separated field")
    return fields


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Query Google Places API (New) with explicit request bounds."
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=10.0,
        help="finite HTTP timeout; defaults to 10 seconds",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    nearby = commands.add_parser("nearby", help="run one bounded Nearby Search")
    nearby.add_argument("--latitude", type=float, required=True)
    nearby.add_argument("--longitude", type=float, required=True)
    nearby.add_argument("--radius-meters", type=float, required=True)
    nearby.add_argument("--type", dest="included_types", action="append", default=[])
    nearby.add_argument("--max-results", type=int, default=10)
    nearby.add_argument(
        "--rank", choices=("POPULARITY", "DISTANCE"), default="POPULARITY"
    )
    nearby.add_argument(
        "--fields", type=_fields, default=DEFAULT_NEARBY_FIELDS, metavar="FIELD,..."
    )

    details = commands.add_parser("details", help="retrieve one place by ID")
    details.add_argument("place_id")
    details.add_argument(
        "--fields", type=_fields, default=DEFAULT_DETAILS_FIELDS, metavar="FIELD,..."
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        client = PlacesClient.from_env(timeout_seconds=args.timeout_seconds)
        if args.command == "nearby":
            payload = {
                "places": client.nearby_search(
                    latitude=args.latitude,
                    longitude=args.longitude,
                    radius_meters=args.radius_meters,
                    included_types=args.included_types,
                    max_results=args.max_results,
                    rank_preference=args.rank,
                    fields=args.fields,
                )
            }
        else:
            payload = client.place_details(args.place_id, fields=args.fields)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except (PlacesApiError, PlacesConfigurationError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
