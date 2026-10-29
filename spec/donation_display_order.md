# Donation Display Order — Plan

**Goal:** Admins control the order of programs (categories) and of the projects inside each program on the website, by dragging rows in the desk. No order numbers.

## 1. Desk

### Program order: new Single DocType `Donation Display Settings`

- URL: `/app/donation-display-settings`. Role: System Manager.
- Table field `program_order` → child `Donation Program Order`.

### Project order: new table on `Donation Program`

- New section "Projects Order" with Table field `project_order` → child `Donation Project Order`.

### Child DocTypes

| Child | Fields (all read-only) | Shown in grid |
|---|---|---|
| `Donation Program Order` | `program` (hidden Data: program name), `program_title`, `published` | Title, Published |
| `Donation Project Order` | `project` (hidden Data: project name), `project_title`, `published` | Title, Published |

- Both tables have `cannot_add_rows` and `cannot_delete_rows` set. Admins only drag rows.
- The name is stored as Data, not Link. Frappe checks Links before any hook runs, so a deleted record would block the save before the sync could remove it. The sync fills in the title and published values instead of `fetch_from`.

## 2. Keeping the tables in sync (automatic)

- A shared helper runs in the controller `onload` (when the form opens) and `validate` (on save):
  - drops rows whose program/project no longer exists, or that moved to another program;
  - appends any missing program/project at the end (newest first among the new ones, so the first sync matches today's order);
  - refreshes titles and published flags.
- Deleting a program or project is never blocked by these tables, because they hold no Link fields.

## 3. API (`afif/donation_api.py`)

- `get_programs`, `get_donation_landing` and `get_projects` sort by row position in the order tables.
- Anything not in a table (e.g. created since the last sync) goes after the ordered items, newest first, so the website never misses an item.

## 4. Frontend

No changes. The pages already show items in the order the API returns them.

## 5. Files touched

- `afif/afif/doctype/donation_display_settings/` (new: Single)
- `afif/afif/doctype/donation_program_order/`, `donation_project_order/` (new: child tables)
- `afif/afif/doctype/donation_program/donation_program.{json,py}`
- `afif/donation_order.py` (new: sync + sort helpers)
- `afif/donation_api.py`
- `bench migrate` + `bench restart` (the restart needs sudo)
