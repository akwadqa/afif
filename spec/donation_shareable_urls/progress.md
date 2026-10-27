# Progress: Donation shareable URLs

| Phase | Status | Commits |
|---|---|---|
| 1. Category slug | done | feat: add slug to donation program |
| 2. URL state | done | feat: reflect donation category, project and dialog in URL |
| 3. Project slug | done | feat: add slug to donation project; feat: use project slug in donation URLs |

## Deviations

- Phase 3 replaced phase 2's `/donate/<category>/project/<id>` with `/donate/<project-slug>`, and `?donate=<id>` with `?donate=<project-slug>`. Phase 2 never went live, so no links depended on it.

## Open issues

- **Not yet checked in a real browser.** The agent's headless Chrome couldn't start because `libasound2` is missing. What has been verified:
  - Vitest tests for the dialog/URL logic pass.
  - The API, through `bench serve`, returns the slugs.
  - The three URL shapes return 200.
- **Python changes need `bench restart` (sudo)** before the live site serves the slugs.
- **GA is still set up twice**, through `analytics.js` and `useGoogleAnalytics.js`. This is out of scope here.
