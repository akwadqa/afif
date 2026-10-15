# Scholarship Flow — Progress

| Phase | Status | Commits |
|---|---|---|
| [1 — Tracer: end-to-end submit](phase-1-tracer.md) | todo | |
| [2 — Field variants](phase-2-field-variants.md) | todo | |
| [3 — Approval/rejection cascade](phase-3-approval-cascade.md) | todo (blocked: OQ2–OQ4, OQ6) | |
| [4 — Accepted users + desk polish](phase-4-accepted-users-desk.md) | todo (OQ5) | |

## Deviations from plan
_None yet._

## Open issues / blockers
- Waiting for the mentor's answers on OQ1–OQ8 (see [plan.md §6](plan.md#6-open-questions-for-the-mentor)).
- The existing code uses DB Workflows, raw SQL and `frappe.db.commit()`. These conflict with the project rules, but this feature leaves them alone, except where Phase 3 needs atomicity.
