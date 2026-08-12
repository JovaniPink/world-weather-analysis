# Repository guidance

- Treat committed notebooks, CSV files, and images as historical research artifacts, not current observations or a licensed redistribution corpus.
- Keep credentials out of Git and command-line arguments. The Places client reads only `GOOGLE_PLACES_API_KEY`.
- Tests and CI must never call Google or another live weather/place service.
- Preserve explicit field masks, finite bounds, finite timeouts, and no-hidden-retry behavior so quota and billing remain visible.
- Stage explicit files only and preserve unrelated research artifacts.
- Run `./scripts/check.sh` before handoff.
