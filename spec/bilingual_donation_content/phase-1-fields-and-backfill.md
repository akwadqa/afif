# Phase 1 — Arabic fields and backfill

**Goal:** every donor-facing text on a donation program, project and preset amount has an Arabic field on the record, filled from the translations that exist today.

## Scope

- Add the `*_ar` fields (see `plan.md` §3) and remove `translatable: 1` from their English counterparts.
- One patch that copies the existing `Translation` rows into the new fields.
- No API change yet: the website still reads `Translation`. The site keeps working throughout.

## Files to change

- `afif/afif/doctype/donation_program/donation_program.json` — `title_ar` after `title`; `intro_ar` in a second column of the Content section; drop `translatable` from `title` and `intro`.
- `afif/afif/doctype/donation_project/donation_project.json` — `title_ar` after `title`; `quote_ar` and `body_ar` in a second column of the Content section; drop `translatable` from `title`, `quote`, `body`.
- `afif/afif/doctype/donation_project_amount/donation_project_amount.json` — `label_ar` after `label`, shown in the grid.
- `afif/patches/backfill_donation_arabic_content.py` — new.
- `afif/patches.txt` — register `afif.patches.backfill_donation_arabic_content` under `[post_model_sync]`.

## The patch

`execute()` walks the three doctypes and, for each record, writes every Arabic field that is still empty from the `Translation` row matching its English source text:

- Lookup: `Translation` where `source_text` is the English value and `language = "ar"`.
- One query per doctype collects the records; translations are fetched in one `frappe.get_all` keyed by `source_text`, not one query per field.
- Writes with `frappe.db.set_value(..., update_modified=False)` so the backfill does not touch modification timestamps or fire controller hooks.
- A record with no matching translation is left empty — the API fallback covers it.
- Re-running the patch is safe: it only fills fields that are empty.

## Tests

`afif/tests/test_donation_arabic_backfill.py` (new):

- a program whose title and intro have Arabic `Translation` rows ends up with `title_ar` and `intro_ar` set to the translated text;
- a project with Arabic rows for `title`, `quote` and `body` gets all three;
- a preset amount label with an Arabic row gets `label_ar`;
- a record with no translation keeps its Arabic fields empty;
- an Arabic field that already has text is not overwritten by the patch.

Run: `bench --site afif.akwad.qa run-tests --module afif.tests.test_donation_arabic_backfill`

## Done when

- `bench --site afif.akwad.qa migrate` adds the columns and runs the patch without error.
- The tests above pass.
- The donation pages still render exactly as before (nothing reads the new fields yet).
