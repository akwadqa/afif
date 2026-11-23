# Progress: Bilingual donation content

| Phase | Status | Commits |
|---|---|---|
| 1. Arabic fields and backfill | todo | |
| 2. API language resolution | todo | |
| 3. Migration and verification | todo | |

## Deviations

None yet.

## Open issues

- The existing `Translation` rows for donation content are left in place after the backfill. A later cleanup can remove them once the Arabic fields have been reviewed.
- Content editors must review records the backfill could not match; those fall back to English until an Arabic value is entered.
