# Progress: Request required attachments

| Phase | Status | Commits |
|---|---|---|
| 1. Server validation | done | fix: block beneficiary request submission without required attachments |
| 2. Atomic upload in the SPA | todo | |

## Deviations

- The tests patch `afif.hooks_call.before_insert_request`, because it requires the session user to own an Accepted registration, which these tests do not exercise.

## Open issues

- **Python changes need `bench restart` (sudo)** before the live site enforces the check.
