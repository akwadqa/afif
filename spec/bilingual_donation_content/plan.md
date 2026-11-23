# Bilingual Donation Content — Plan

**Goal:** Enter every donor-facing text of a donation program and project in English and in Arabic on the record itself, so the website shows accurate content in the language the donor chose.

## 1. Requirement

Donors report poor Arabic content on donation programs and projects.

Today the record holds the **English** text, and the Arabic version lives in Frappe's `Translation` doctype, matched on the exact source string (`afif/donation_api.py` → `_localize`). Two consequences:

- Editing the English text breaks the match, and the Arabic visitor silently gets English. Nothing warns the editor.
- Two records that happen to share a title share one translation.

Both displayed languages must be editable fields on the record.

## 2. Decisions

| Decision | Reason |
|---|---|
| Keep the existing fields as the **English** source and add an Arabic sibling (`*_ar`) | Production data already holds English in these fields. No column rename, no data move, `title_field`, slug generation and the display-order tables keep working. |
| Rejected: rename to `*_en` + add `*_ar` | Symmetric naming, but a schema rename on live data plus follow-up changes in `title_field`, the order tables, slug generation, the API and the tests. Not worth the risk. |
| Rejected: a child table with one row per language | Overkill for two fixed languages, and a bad desk experience for the rich-text `body`. |
| Arabic falls back to English when empty | A half-translated record must never render blank. |
| Arabic fields are not mandatory | Existing records would become unsaveable; the fallback already covers the gap. |
| Existing `Translation` rows are copied, not deleted | Non-destructive and reversible. |
| A field written in Arabic with no English version is copied into its `*_ar` field | Some records (e.g. project `body`) hold Arabic with no translation at all. Left alone, the Arabic would be lost the day an editor writes English into that field. Copying, not moving, keeps today's output identical. |
| `status` and `location` Select options keep Frappe's native translation | Fixed option lists, not editorial content. |
| The order tables (`program_title`, `project_title`) stay English | Desk-only, admin-facing. |

## 3. Data model

New fields, all alongside their English counterpart in the Content section (English column, Arabic column), and `translatable` removed from the English fields:

| DocType | English (existing) | Arabic (new) | Fieldtype |
|---|---|---|---|
| Donation Program | `title` | `title_ar` | Data |
| Donation Program | `intro` | `intro_ar` | Text Editor |
| Donation Project | `title` | `title_ar` | Data |
| Donation Project | `quote` | `quote_ar` | Small Text |
| Donation Project | `body` | `body_ar` | Text Editor |
| Donation Project Amount | `label` | `label_ar` | Data |

## 4. Affected areas

- `afif/donation_api.py` — `_localize` is replaced by per-language field selection in all five public endpoints (`get_programs`, `get_projects`, `get_donation_landing`, `get_project_detail`, and the preset amounts helper `_attach_amounts`).
- `afif/donation_slug.py` — `get_english_title()` is removed; `doc.title` is already the English title.
- `afif/patches/` — one new post-model-sync patch backfills the `*_ar` fields from `Translation`.
- **Frontend: no change.** The API keeps returning the same keys (`title`, `intro`, `quote`, `body`, `label`) resolved for the requested `lang`.
- Tests: `afif/afif/doctype/donation_program/test_donation_program.py`, `.../donation_project/test_donation_project.py`, and a new API test module.

## 5. Go-live prerequisites

- `bench --site afif.akwad.qa migrate` (creates the columns and runs the backfill patch).
- `bench --site afif.akwad.qa clear-cache` and `bench restart` (gunicorn runs with `--preload`, so Python changes are not live before a restart).
- After the backfill, content editors review the Arabic fields: anything the patch could not match stays empty and falls back to English.

## 6. Phases

1. [Phase 1 — Arabic fields and backfill](phase-1-fields-and-backfill.md)
2. [Phase 2 — API language resolution](phase-2-api-language-resolution.md)
3. [Phase 3 — Migration and end-to-end verification](phase-3-verification.md)

## 7. Open items

- Whether the `Translation` rows for these texts are deleted in a later cleanup. Out of scope here; they are left in place and simply stop being read.
