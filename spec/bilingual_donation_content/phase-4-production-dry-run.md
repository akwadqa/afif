# Phase 4 — Production dry run

**Goal:** know exactly what this change does to the production data before it is deployed.

Neither the dev site nor the test suite can answer that on its own: the dev records hold Arabic in the English fields, while production holds English titles with `ar` translations. The only proof is the production data itself.

## 1. Classify the production data (read-only, no deployment)

`afif.patches.backfill_donation_arabic_content.preview()` reports what the patch would write, and writes nothing. It also runs on a database that predates the Arabic columns, so it can be used before any migration.

```
bench --site <site> execute afif.patches.backfill_donation_arabic_content.preview
```

It returns `{doctype: {field: {source: count}}}`, where each field's records are counted by what the patch would use:

| Source | Meaning | What the donor sees afterwards |
|---|---|---|
| `translation` | an `ar` Translation row matches the English text | Arabic from the record, English from the record — the fix working |
| `arabic_source` | the field itself is written in Arabic, with no translation | unchanged in both languages; the Arabic is now safe from a later English edit |
| `no_arabic_available` | English text with no Arabic anywhere | unchanged; an editor has to write the Arabic |
| `already_filled` | the Arabic field already has text | untouched |

A healthy production report has most titles under `translation`.

## 2. Rehearse the migration on a copy of production

```
# on production
bench --site <prod-site> backup

# on the dev bench, with this branch checked out
bench new-site prodcheck.localhost
bench --site prodcheck.localhost install-app afif
bench --site prodcheck.localhost restore <prod-database.sql.gz>
bench --site prodcheck.localhost execute afif.patches.backfill_donation_arabic_content.preview   # before
bench --site prodcheck.localhost migrate
bench --site prodcheck.localhost execute afif.patches.backfill_donation_arabic_content.preview   # after: everything is already_filled or no_arabic_available
```

Then compare the API output against what production serves today, for the same records:

```
bench --site prodcheck.localhost execute afif.donation_api.get_donation_landing --kwargs "{'lang':'ar'}"
bench --site prodcheck.localhost execute afif.donation_api.get_donation_landing --kwargs "{'lang':'en'}"
```

## Done when

- The `preview` report from production is understood, and the `no_arabic_available` counts are accepted as content work.
- The rehearsal on the production copy migrates cleanly and its `lang=en` / `lang=ar` output matches what the live site shows today, record for record.
- No record loses text in either language.
