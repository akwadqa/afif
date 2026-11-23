# Progress: Bilingual donation content

| Phase | Status | Commits |
|---|---|---|
| 1. Arabic fields and backfill | done | b92053c, 813e6b1 |
| 2. API language resolution | todo | |
| 3. Migration and verification | todo | |

## Deviations

- Phase 1: the backfill tests create projects with an `image`, which is mandatory on Donation Project. The phase plan did not mention it.
- `afif.afif.doctype.donation.test_donation` contains a `TestDonation` class with no test methods, so it runs 0 tests. Pre-existing, untouched by this feature.

## Phase 1 results

- `bench --site afif.akwad.qa migrate` — columns created, backfill patch applied, no errors.
- `run-tests --module afif.tests.test_donation_arabic_backfill` — 5 tests, OK.
- `run-tests --module afif.afif.doctype.donation_program.test_donation_program` — 7 tests, OK.
- `run-tests --module afif.afif.doctype.donation_project.test_donation_project` — 12 tests, OK.

## Open issues

- The existing `Translation` rows for donation content are left in place after the backfill. A later cleanup can remove them once the Arabic fields have been reviewed.
- Content editors must review records the backfill could not match; those fall back to English until an Arabic value is entered.
