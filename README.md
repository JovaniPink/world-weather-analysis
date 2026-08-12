# World Weather Analysis

World Weather Analysis is a historical collection of notebooks, data snapshots,
plots, and experiments exploring weather, geography, and travel questions. The
repository also contains one maintained utility: a bounded Python client for
Google Places API (New).

The committed CSV files, workbooks, images, and notebook outputs are research
artifacts from earlier exercises. They are not current observations, a
reproducible weather pipeline, or an approved redistribution corpus.

## Repository map

- `notebooks/` contains exploratory weather, vacation, and mapping notebooks.
- `data/` contains historical weather snapshots.
- `resources/` contains generated plots, notes, and workbook artifacts.
- `world_weather/` contains the tested Places API (New) client and CLI.
- `scripts/google_places_requests.py` remains a compatibility entry point for
  the same CLI.

No notebook is executed in CI, and no live service is contacted during tests.

## Places API (New) client

The previous script used the legacy Nearby Search and Place Details endpoints.
The maintained client now follows Google’s current web-service contract:

- Nearby Search is one bounded `POST /v1/places:searchNearby` request.
- Place Details is `GET /v1/places/{place_id}`.
- every operation has an explicit, non-wildcard response field mask;
- Nearby Search limits radius to 50 km and results to 20;
- every HTTP request has a finite timeout;
- transport, HTTP, JSON, and response-shape failures stop the command;
- there is no hidden retry or legacy next-page loop.

This tool does not persist responses. Technical API access does not establish
permission to store, display, combine, or redistribute Google place data.
Review the applicable Google Maps Platform terms for the intended use.

### Set up

Requirements:

- Python 3.14
- [uv](https://docs.astral.sh/uv/) 0.12.3
- a Google Cloud project with Places API (New) enabled
- a restricted API key authorized only for the required API and environment

```bash
python -m pip install uv==0.12.3
uv sync --all-groups --frozen
```

`.env.example` documents the variable name but the client deliberately does not
auto-load dotenv files. Do not commit `.env`, paste a key into source, or pass a
key on the command line. Export it from a secret manager or the local shell:

```bash
export GOOGLE_PLACES_API_KEY='replace-with-a-restricted-key'
```

### Nearby Search

```bash
uv run weather-places nearby \
  --latitude 28.4810971 \
  --longitude -81.5089239 \
  --radius-meters 500 \
  --type restaurant \
  --max-results 10
```

The default field mask requests identifiers, names, addresses, coordinates,
types, and a Google Maps URI. Request only the fields the caller needs because
Google uses field masks to determine returned data and billing. Explicit fields
can be supplied without the `places.` prefix:

```bash
uv run weather-places nearby \
  --latitude 40.754851 \
  --longitude -73.984164 \
  --radius-meters 50 \
  --type transit_station \
  --fields id,displayName,location
```

Nearby Search (New) returns at most 20 results and does not expose the legacy
`next_page_token`. The command performs one request only.

### Place Details

```bash
uv run weather-places details ChIJ8WvuSB7Lj4ARFyHppkxDRQ4 \
  --fields id,displayName,formattedAddress,googleMapsUri
```

The compatibility entry point invokes the same commands after the environment
has been installed:

```bash
uv run python scripts/google_places_requests.py --help
```

## Quality and dependency gates

```bash
./scripts/check.sh
```

The gate checks the frozen lock, installs the exact Python 3.14 graph, runs Ruff
lint and formatting, executes isolated fake-HTTP tests, smokes both CLI entry
points, and audits resolved third-party dependencies for known vulnerabilities.
`pyproject.toml` exact-pins direct runtime and quality dependencies; `uv.lock`
captures the complete graph; Renovate monitors packages, uv, and digest-pinned
GitHub Actions.

## Historical analysis scope

The notebooks explored:

- OpenWeatherMap collection across generated city coordinates;
- latitude relationships with temperature, humidity, cloudiness, and wind;
- travel filtering and nearby-place experiments;
- detailed New York City weather questions;
- plots and maps produced from point-in-time snapshots.

They may depend on retired APIs, unstated package versions, local credentials,
and mutable upstream data. Reproducing one requires a separate source, terms,
environment, schema, and freshness review. Do not infer current weather from
committed outputs.

## Release and rollback boundary

Merging this repository changes source and CI only. It does not enable an API,
create a key, call Google, deploy a service, or migrate stored data. Rollback is
a normal source revert. Key creation, restriction, rotation, quota, billing, and
any production execution remain explicit Google Cloud owner actions.

## Official references

- [Migrate to Places API (New)](https://developers.google.com/maps/documentation/places/web-service/legacy/migrate-overview)
- [Nearby Search (New)](https://developers.google.com/maps/documentation/places/web-service/nearby-search)
- [Place Details (New)](https://developers.google.com/maps/documentation/places/web-service/place-details)
- [Choose response fields](https://developers.google.com/maps/documentation/places/web-service/choose-fields)

## License

Original repository code and documentation are licensed under the
[MIT License](LICENSE.md). Third-party data, maps, images, and service responses
remain subject to their own terms.
