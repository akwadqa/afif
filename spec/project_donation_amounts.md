# Project Donation Amounts with Custom Labels — Plan

**Goal:** Admins set a project's preset donation amounts in the desk, each with an optional label (e.g. "Iftar meal for a family — 50 QAR"). Today the amounts are hard-coded in the frontend as `[1000, 100, 50, 10]` in the dialog and `[10, 50, 100, 1000]` in the checkout form.

## 1. Backend

### New child DocType: `Donation Project Amount` (istable)

| Label | Fieldname | Type | Required | Notes |
|---|---|---|---|---|
| Amount | `amount` | Currency | yes | must be > 0 |
| Label | `label` | Data | no | translated through the existing `Translation` doctype, like project titles |

### `Donation Project` changes

- New section "Donation Amounts" (after Funding) with a Table field `donation_amounts` → `Donation Project Amount`.
- Validation: each amount must be > 0, an amount can't appear twice, and a project can have at most **6** amounts.
- Rows display in table order, so admins sort them by dragging.

### API (`afif/donation_api.py`)

- Add an `amounts` list (`[{amount, label}]`, label localized with `_localize`) to each project returned by `get_donation_landing`, `get_project_detail` and `get_projects`.
- Load the rows for all projects in one query, not one query per project.

## 2. Frontend

| Where | File | Change |
|---|---|---|
| Donation dialog | `components/donation/DonationDialog.vue` | Build the preset buttons from `activeProject.amounts` |
| Checkout form | `components/donation/DonationForm.vue` | Build the preset buttons from `selectedProjectData.amounts` |

- **Button:** shows the label on top and `amount QAR` below it. With no label, it shows only the amount, as it does now.
- **No amounts:** a project with no rows shows no preset buttons, only the custom amount input (opened by default). The hard-coded presets are removed.
- The **Custom amount** button and the free-entry input stay as they are for projects that have amounts.
- The donation submitted is still the numeric amount. Nothing changes in `create_donation`.

## 3. Files touched

- `afif/afif/doctype/donation_project_amount/` (new: `.json`, `.py`, `__init__.py`)
- `afif/afif/doctype/donation_project/donation_project.{json,py}`
- `afif/donation_api.py`
- `frontend/src/components/donation/DonationDialog.vue`, `DonationForm.vue` (+ shared styles), then `yarn build`
- `bench migrate` + `bench restart` (the restart needs sudo)

## Decisions

1. The label is **optional**. If set, the button shows it; if not, the button shows the amount only.
2. Projects with no amounts show **only the custom amount input**. There are no default presets.
3. A project can have at most **6** amounts, enforced in `Donation Project` validation.

**Note:** once deployed, every existing project shows only the custom input until admins add amounts in the desk.
