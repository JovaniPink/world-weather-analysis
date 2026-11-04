# Repository guidance

- Treat committed notebooks, CSV files, and images as historical research artifacts, not current observations or a licensed redistribution corpus.
- Keep credentials out of Git and command-line arguments. The Places client reads only `GOOGLE_PLACES_API_KEY`.
- Keep the credential destination fixed to `https://places.googleapis.com/v1`; tests inject a fake HTTP session, never a replacement host.
- Tests and CI must never call Google or another live weather/place service.
- Preserve explicit field masks, finite bounds, finite timeouts, and no-hidden-retry behavior so quota and billing remain visible.
- Stage explicit files only and preserve unrelated research artifacts.
- Run `./scripts/check.sh` before handoff.

## Shared personal platform

The owner-selected Google Cloud project for all personal deployments is
[`jovanipink`](https://console.cloud.google.com/welcome?project=jovanipink).
Use the [Netlify `jovanipink` team](https://app.netlify.com/teams/jovanipink/projects)
for web publishing and [Clerk](https://dashboard.clerk.com/apps) for application
identity when accounts are needed. Separate products and environments through
resource names, scoped identities, data boundaries and Terraform state; do not
create a GCP project per product or environment. This decision supersedes older
platform-selection prose. It does not establish that integrations are implemented
or authorize a deployment. Static sites and local-only apps need no added login.
