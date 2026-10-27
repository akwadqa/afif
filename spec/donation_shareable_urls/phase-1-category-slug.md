# Phase 1: Category slug

**Goal:** every Donation Program has a stable, readable slug, and the donation APIs return it.

**Scope**
- Add a `slug` field to Donation Program.
- In `validate`, normalise and check a manually entered slug, or generate one from the English title and make it unique.
- A patch backfills existing programs.
- `get_donation_landing` returns `slug` on each program and `program_slug` on each project. `get_project_detail` returns `program_slug`.

**Tests** (`test_donation_program.py`)
- Generated from the translation.
- Rejected when it's Arabic-only with no translation.
- Invalid manual slug rejected; manual slug normalised.
- Collision suffix.
- Slug kept when the title changes.
- The APIs return the slug.

**Done when:** migrate fills the slugs for every existing program and the tests pass.
