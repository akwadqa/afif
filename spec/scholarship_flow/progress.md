# Scholarship Flow — Progress

| Phase | Status | Commits |
|---|---|---|
| [1 — Tracer: end-to-end submit](phase-1-tracer.md) | todo | |
| [2 — Field variants](phase-2-field-variants.md) | todo | |
| [3 — Approval/rejection cascade](phase-3-approval-cascade.md) | todo (needs OQ3, OQ6; OQ4 has a default) | |
| [4 — Accepted users + desk polish](phase-4-accepted-users-desk.md) | todo (OQ5 has a default) | |

## Deviations from plan
- Scholarship moved from a new `request_category` to a subcategory of Education Assistance (mentor answer). The `Categories` patch was dropped because `Education Assistance` already exists.
- `education_invoice` and `grade_transcript` are reused for the university invoice and the transcript, so 6 new Attach fields instead of 8.

## Open issues / blockers
- Still open with the mentor: OQ1b, OQ3, OQ4, OQ5 and OQ6 (see [plan.md §7](plan.md#7-open-questions)).
- The existing code uses DB Workflows, raw SQL and `frappe.db.commit()`. These conflict with the project rules, but this feature leaves them alone, except where Phase 3 needs atomicity.
