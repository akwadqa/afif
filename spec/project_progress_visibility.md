# Project Progress Visibility — Plan

**Goal:** Admins can choose, per Donation Project in the desk, whether the website shows that project's funding progress.

## 1. New field on `Donation Project`

| Label | Fieldname | Type | Default | Placement |
|---|---|---|---|---|
| Show Progress | `show_progress` | Check | `1` | Funding section, above Required Amount |

- The default of `1` means existing and new projects keep showing progress. No patch is needed: migrate creates the column with `DEFAULT 1`, so existing rows get 1.
- Description: "Show the funding progress bar and amounts on the website."

## 2. API (`afif/donation_api.py`)

Return `show_progress` from the three endpoints that send funding data:
- `get_projects`, used by the checkout form
- `get_donation_landing`, used by the Donate page project cards
- `get_project_detail`, used by the project details page

When `show_progress` is 0, also stop sending `donated_amount`, `required_amount` and `percentage` (return them as `null`). The figures are then hidden from the API response too, not just from the UI.

## 3. Frontend: hide the progress block when `show_progress` is off

| Where | File | Hidden block |
|---|---|---|
| Donate page project card | `components/donation/DonationProjectCard.vue` | `.funding-block` (paid amount, %, bar, target) |
| Project details page | `pages/DonationProjectDetail.vue` | `.financial-progress` (totals, bar, remaining) |
| Checkout form | `components/donation/DonationForm.vue` | Coverage / progress card |

The Donate button and the rest of the layout stay as they are.

## 4. Files touched

- `afif/afif/doctype/donation_project/donation_project.json`
- `afif/donation_api.py`
- The 3 frontend files above, then `yarn build`

## Decisions

1. When Show Progress is off, hide the **whole funding block** (amounts, percentage, bar and target).
2. New projects default to **Show**.
3. On the checkout form, the coverage card still shows before a project is selected. It hides once a project with Show Progress off is selected.
