# Phase 3: Project slug

**Goal:** a shared project link shows only the project slug, and a shared category link shows only the category slug.

**Scope**
- Donation Project gets a `slug` field: unique, generated from the English title, capped at 60 characters at a word boundary, and reserved words (`form`, `success`, `project`) are rejected.
- The slug logic moves to `afif/donation_slug.py`, shared with Donation Program.
- Patch `set_donation_project_slugs`.
- `get_project_detail` accepts `slug`, and still accepts `project_name` for legacy links. Landing projects include `slug`.
- Frontend:
  - Route `:slug` (`DonationProject`) replaces `:category/project/:name`. The legacy `project/:name` redirects.
  - The card, share and canonical redirect all use the slug.
  - The popup URL is `?donate=<slug>`, with `?category=` hidden while it's open and restored on close.

**Tests**
- Backend:
  - Word-boundary cut.
  - Reserved names are skipped or rejected.
  - Duplicate manual slugs are rejected.
  - Detail lookup works by slug or name.
  - The landing response returns the slug.
- `useDonationDialog.test.js`: the category is hidden and restored.

**Done when:**
- Migrate fills every project slug.
- The backend tests and Vitest pass, and `yarn build` succeeds.
