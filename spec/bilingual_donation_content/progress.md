# Progress: Bilingual donation content

| Phase | Status | Commits |
|---|---|---|
| 1. Arabic fields and backfill | done | b92053c, 813e6b1 |
| 2. API language resolution | done | 50291f6, f2fb6ae |
| 3. Migration and verification | done (restart pending) | 0168f41, c405aa4 |
| 4. Production dry run | todo (needs a production backup) | |

## Deviations

- Phase 2: `get_english_title()` was kept in `afif/donation_slug.py` instead of being deleted. Two shipped patches (`set_donation_program_slugs`, `set_donation_project_slugs`) import it, and this app never modifies an existing patch; deleting it would break a fresh-site migration. It is unused by live code.
- Phase 1: the backfill tests create projects with an `image`, which is mandatory on Donation Project. The phase plan did not mention it.
- `afif.afif.doctype.donation.test_donation` contains a `TestDonation` class with no test methods, so it runs 0 tests. Pre-existing, untouched by this feature.

## Phase 1 results

- `bench --site afif.akwad.qa migrate` — columns created, backfill patch applied, no errors.
- `run-tests --module afif.tests.test_donation_arabic_backfill` — 5 tests, OK.
- `run-tests --module afif.afif.doctype.donation_program.test_donation_program` — 7 tests, OK.
- `run-tests --module afif.afif.doctype.donation_project.test_donation_project` — 12 tests, OK.

## Phase 2 results

- `run-tests --module afif.tests.test_donation_api_language` — 8 tests, OK.
- `run-tests --module afif.afif.doctype.donation_program.test_donation_program` — 8 tests, OK.
- `run-tests --module afif.afif.doctype.donation_project.test_donation_project` — 12 tests, OK.
- `run-tests --module afif.tests.test_donation_arabic_backfill` — 5 tests, OK.
- `run-tests --module afif.tests.test_hooks_call` — 2 tests, OK.
- No endpoint reads the `Translation` doctype any more.

## Phase 3 results (re-run after the Arabic-source rule)

- Backfill re-run on dev data: 9/9 programs have `title_ar`, 8/9 `intro_ar`; 26/26 projects have `title_ar`, 25/26 `body_ar`, 1 `quote_ar`. All 8 preset-amount labels are blank on this site, so `label_ar` stays empty.
- Full suite after the change: backfill 7 OK, api-language 8 OK, program 8 OK, project 12 OK, hooks 2 OK.

## Phase 3 results

- `bench --site afif.akwad.qa migrate` — clean, backfill patch applied.
- `bench --site afif.akwad.qa clear-cache` — clean.
- `bench restart` — **blocked**: `sudo supervisorctl status` is not available in this session. The dev site keeps serving the previous Python code until someone restarts it.
- Full suite: backfill 5 OK, api-language 8 OK, program 8 OK, project 12 OK, hooks 2 OK. `afif.afif.doctype.donation.test_donation` runs 0 tests (empty class, pre-existing).
- Desk/DB: `title_ar`, `intro_ar`, `quote_ar`, `body_ar`, `label_ar` columns exist and the Arabic fields sit in the second column of the Content section.
- `get_donation_landing` through fresh code returns no `*_ar` keys in either language.

## Code review (before taking the PR out of draft)

Three defects in the backfill patch, all fixed with a regression test each:

- The Arabic detector counted letters in the raw HTML, so a Text Editor field whose tags and
  attributes carry more Latin letters than its sentence carries Arabic ones (`<p style="text-align: right;">…`)
  read as "not Arabic" and its Arabic was never copied into the Arabic column — the exact loss
  the copy rule exists to prevent. Markup is now stripped before the letters are counted.
- The patch only read `language: ar` rows. A record holding Arabic in the English column with an
  English `Translation` row — the shape the dev site had — kept Arabic in the English column, so
  `lang=en` visitors lost the English the old `_localize` used to serve. The patch now splits those
  records: the Arabic moves to the Arabic column, the English translation goes into the English one.
- `preview()` reported a field that is empty in both languages as `no_arabic_available`, which the
  phase 4 runbook reads as "English text with no Arabic anywhere" and uses as the go-live gate.
  Empty fields now count as `empty`; on dev that moved 34 rows out of the gate's number.

Still outstanding: an uncommitted desk round-trip on `donation_project.json` moved the required
`location` select into the Arabic column between `quote_ar` and `body_ar`, and added `row_format`.
Revert it with `git checkout -- afif/afif/doctype/donation_project/donation_project.json`, or keep the
move deliberately — but it breaks the English/Arabic column pairing as it stands.

## Dev data repair

Dev stored Arabic in the English columns with the English in `Translation` rows — the mirror image of
production. With the patch fixed, re-running it split 60 field values across 9 programs and 26 projects:
English in the English column, Arabic in the Arabic one. `preview()` now reports no
`no_arabic_available` at all on dev.

Five fields have no English anywhere and were left as they are, because there is nothing to restore:
the `intro` of the Health, Social and Education programs, the `title` of `ce2gaggtbf` and the `body`
of `pli4l8t3hh`. An editor writes the English into the English field; the Arabic is already safe.

## Open issues

- Editors who enter Arabic through the desk's in-form translate dialog will find it gone for these fields: `translatable` was removed, which is the point of the change, but the content team has to be told to use the new Arabic fields instead.

- `bench restart` still has to be run by someone with sudo before the dev site serves the new code.
- English text is still missing for the fields that only ever had Arabic (e.g. most project bodies). The patch preserved the Arabic; an editor now writes the English into the English field, and the Arabic stays put.
- ~~The dev site's data runs the other way round.~~ Resolved: production stores English titles with `ar` translations, which the patch handles, and Arabic-only fields are now copied into their Arabic column. Dev data is Arabic-only, so English output there is unchanged until editors add English text.
- **(historical) The dev site's data runs the other way round.** 7 of 9 Donation Programs and all 26 Donation Projects hold **Arabic** text in the base `title` field, and the content translations stored are `language: en` (67 rows). Production was reported as English-in-base. The backfill patch, which reads `language: ar` rows, therefore fills almost nothing here and the dev site cannot demonstrate the feature until the direction is settled. Needs a decision before go-live.

- The existing `Translation` rows for donation content are left in place after the backfill. A later cleanup can remove them once the Arabic fields have been reviewed.
- Content editors must review records the backfill could not match; those fall back to English until an Arabic value is entered.
