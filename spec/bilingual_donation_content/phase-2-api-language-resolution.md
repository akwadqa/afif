# Phase 2 — API language resolution

**Goal:** the public API serves each text from the field matching the requested language, and stops reading the `Translation` doctype.

## Scope

- Replace `_localize()` with per-language field selection across all five endpoints.
- Fall back to the English field when the Arabic one is empty.
- Simplify slug generation now that `title` is known to be English.

## Files to change

### `afif/donation_api.py`

- Remove `_localize()`.
- Add a single helper that resolves the localised fields of a record dict in place, e.g. `localize(record: dict, fields: tuple[str, ...], lang: str) -> None`: for `lang == "ar"` it replaces `record[field]` with `record[f"{field}_ar"]` when that value is non-empty, then drops the `*_ar` keys from the payload. For `lang == "en"` it only drops them. Response keys stay `title`, `intro`, `quote`, `body`, `label`.
- Every `frappe.get_all` / `frappe.db.get_value` in the module fetches the `*_ar` field next to its English field:
  - `get_programs` — `title`, `title_ar`, `intro`, `intro_ar`
  - `get_projects` — `title`, `title_ar`, `quote`, `quote_ar`, `body`, `body_ar`
  - `get_donation_landing` — program `title`, `title_ar`, `intro`, `intro_ar`; project `title`, `title_ar`
  - `get_project_detail` — project `title`, `quote`, `body` with their `*_ar`; program `title`, `title_ar`, `intro`, `intro_ar` for `program_title` / `program_intro`
  - `_attach_amounts` — `label`, `label_ar`
- `_normalize_lang` is unchanged.

### `afif/donation_slug.py`

- Remove `get_english_title()` and its `Translation` lookup; `set_slug` slugifies `doc.title` directly.
- The error raised when a title yields no slug and none was entered becomes `Enter a slug for this record` — "add an English translation" no longer describes anything.

### Tests to update

- `afif/afif/doctype/donation_program/test_donation_program.py` — `test_slug_is_generated_from_english_translation` becomes a plain English-title case (no `Translation` row); `test_arabic_title_without_translation_or_slug_is_rejected` becomes "a title with no latin characters and no slug is rejected", matching the new message.
- `afif/afif/doctype/donation_project/test_donation_project.py` — same two adjustments where they appear.

## Tests to add

`afif/tests/test_donation_api_language.py` (new), one program with one project and one preset amount, all with Arabic fields filled:

- `lang="ar"` returns the Arabic title, intro, quote, body and amount label from `get_donation_landing`, `get_programs`, `get_projects` and `get_project_detail`;
- `lang="en"` returns the English values from the same endpoints;
- a project whose `body_ar` is empty returns the English body under `lang="ar"`, while its filled `title_ar` is still Arabic;
- no `lang` argument behaves as `ar` (the existing `_normalize_lang` default);
- the response contains no `*_ar` keys in either language;
- a `Translation` row for a program title is ignored — the record's own fields decide.

Run:
```
bench --site afif.akwad.qa run-tests --module afif.tests.test_donation_api_language
bench --site afif.akwad.qa run-tests --module afif.afif.doctype.donation_program.test_donation_program
bench --site afif.akwad.qa run-tests --module afif.afif.doctype.donation_project.test_donation_project
```

## Done when

- The tests above pass and no code outside the desk reads `Translation` for donation content: `grep -rn "Translation" afif/` returns only the workspace shortcut.
- The donation endpoints return the same JSON keys as before the change.
