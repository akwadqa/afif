# Phase 3 — Migration and end-to-end verification

**Goal:** prove the change on the dev site, in both languages, through the real frontend.

## Scope

No new behaviour. Migration, the full test suite, and a pass over the website.

## Steps

1. `bench --site afif.akwad.qa migrate` — columns created, backfill patch applied.
2. `bench --site afif.akwad.qa clear-cache` and `bench restart` (needs sudo; gunicorn runs with `--preload`, so the API is not live until it restarts).
3. Full donation suite:
   ```
   bench --site afif.akwad.qa run-tests --module afif.tests.test_donation_arabic_backfill
   bench --site afif.akwad.qa run-tests --module afif.tests.test_donation_api_language
   bench --site afif.akwad.qa run-tests --module afif.afif.doctype.donation_program.test_donation_program
   bench --site afif.akwad.qa run-tests --module afif.afif.doctype.donation_project.test_donation_project
   bench --site afif.akwad.qa run-tests --module afif.afif.doctype.donation.test_donation
   ```
4. Desk check: open a Donation Program and a Donation Project and confirm the English and Arabic fields sit side by side in the Content section, and that the preset-amount grid shows `label_ar`.
5. Website check on `/frontend`: the donation landing page, a program and a project detail page, each in Arabic and in English. Confirm the text follows the record's fields, and that a project with an empty `body_ar` shows the English body rather than a blank area.
6. Update `progress.md` and reconcile any deviation back into `plan.md`.

## Done when

- Every command above has been run and its result recorded in `progress.md` — including failures, if any.
- Both languages render correctly on the three page types.
