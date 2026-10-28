# Donation Report — Plan

**Report name:** `Donation Report`
**Type:** Script Report (Python + JS), module `Afif`, ref doctype `Donation`
**Location:** `afif/afif/report/donation_report/` (`.json`, `.py`, `.js`)
**Roles:** Same roles that have access to the `Donation` doctype (currently only System Manager)
**Export:** Built-in report toolbar (Excel / CSV / Print / PDF). Also add a "Donation Report" button on the Donation list view that opens the report with the current list filters.

---

## 1. Filters

| Filter | Fieldname | Type | Default | Notes |
|---|---|---|---|---|
| From Date | `from_date` | Date | first day of current month | required |
| To Date | `to_date` | Date | today | required |
| Date Based On | `date_based_on` | Select: `Created On` / `Paid At` | `Created On` | `creation` vs `paid_at` |
| Payment Status | `payment_status` | Select: blank / Pending / Paid / Failed | blank (all) | |
| Program | `donation_program` | Link → Donation Program | | |
| Project | `donation_project` | Link → Donation Project | | narrowed to the selected Program |
| Frequency | `donation_frequency` | Select: One-Time / Daily / Monthly / Annual | | |
| Currency | `currency` | Link → Currency | | keeps totals in a single currency |
| Group By | `group_by` | Select: `None` / `Program` / `Project` / `Program > Project` | `None` | |
| Donor Name | `donor_name` | Data | | partial match (`LIKE`) |
| Donor Mobile | `donor_mobile` | Data | | partial match |
| Donor Email | `donor_email` | Data | | partial match |
| Reference ID | `reference_id` | Data | | partial match |
| Gateway Txn ID | `gateway_transaction_id` | Data | | partial match |

## 2. Columns

**Detail view (Group By = None):**

| Column | Field | Type |
|---|---|---|
| Donation | `name` | Link → Donation |
| Date | `creation` | Datetime |
| Paid At | `paid_at` | Datetime |
| Program | `donation_program` | Link |
| Project | `donation_project` | Link |
| Donor Name | `donor_name` | Data |
| Mobile | `donor_mobile` | Data |
| Email | `donor_email` | Data |
| Frequency | `donation_frequency` | Data |
| Status | `payment_status` | Data (coloured: Paid green, Pending orange, Failed red) |
| Payment Method | `payment_method` | Data |
| Amount | `amount` | Currency |
| Currency | `currency` | Link |
| Reference ID | `reference_id` | Data |
| Gateway Txn ID | `gateway_transaction_id` | Data |

**Grouped view (Group By = Program / Project / Program > Project):**

The columns stay the same. Donations are nested (as a collapsible tree) under bold group header rows:
- Header row: shows `Title (count)` in the Donation column and links to the Program/Project. The Amount column holds the subtotal.
- `Program > Project` has two levels: Program → Project → donations.
- Groups are sorted by subtotal, largest first. Donations inside a group are newest first.
- Program and Project show titles, because the record IDs are hashes. If the donation has no program, the project's program is used.

## 3. Totals and summary

- A total row (`add_total_row: 1`) sums Amount. In grouped mode it sums only the top-level headers, so nothing is counted twice.
- Report summary cards above the table: **Total Donations (count)**, **Paid**, **Pending**, **Failed**, **Total Amount**.
- No chart.

## 4. Search keys and indexes (Donation doctype)

- Set `search_fields` = `donor_name, donor_mobile, donor_email, reference_id, donation_project`.
- Add `search_index` on `payment_status`, `donation_project`, `donation_program`, `paid_at`, `reference_id`.
- Mark `donation_project`, `donation_frequency` and `currency` as `in_standard_filter` so the list view has the same quick filters.

## 5. Implementation notes

- Build the query with `frappe.qb` and parameterized conditions (no string-built SQL).
- Date filter: `from_date 00:00:00` to `to_date 23:59:59` on the chosen date field.
- Each text filter adds its own `LIKE %term%` condition. When several are filled, they are combined with AND.
- Mixed currencies: if more than one currency is in the result and no Currency filter is set, show a message saying totals are mixed. Totals are not converted.

## 6. Files touched

- `afif/afif/report/donation_report/donation_report.{json,py,js}` (new)
- `afif/afif/doctype/donation/donation.json` (search fields, indexes, standard filters)
- `afif/afif/doctype/donation/donation_list.js` (new: report button)

## Decisions

1. Date Based On defaults to **Created On**. Pending and Failed donations have no `paid_at`, so with all statuses shown, Paid At would hide them.
2. The Status filter defaults to **all statuses**.
3. Roles are the same as the `Donation` doctype permissions.
4. Each searchable field has **its own filter** (donor name, mobile, email, reference ID, transaction ID).
