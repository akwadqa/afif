# Phase 3 — Approval and rejection cascade

> Blocked on OQ2, OQ3, OQ4 and OQ6 (plan §6). This file describes the default from the task text: **the request is the control point**. Revise it once the mentor answers.

## Goal
A single Supervisor action on a scholarship document approves or rejects **both** the registration and the request in one transaction.

## Scope (default: the request is the control point)
1. **Approve.** Hook into the request's `validate` (or `before_save`). When a scholarship request moves from `Pending Supervisor Approval` to `Pending Specialist Approval`:
   - Accept the linked registration first by setting `workflow_state` and `status` to `Accepted` and saving it, with `ignore_permissions` and a `frappe.flags` marker. Its `create_new_beneficiary` then registers the beneficiary in Sanadi and sets `ben_id`.
   - Only after that do the request's own Sanadi hooks run (`validate_subvention_request`, `new_subvention_request`).
2. **Reject.** When a scholarship request moves to `Rejected by Supervisor`, set the registration to `Not Accepted` with a `custom_notes` copied from the request. The `rejection_note` validation needs it.
3. **Guard the other document (OQ4).** In the registration's `validate`, block direct Approve/Reject on a scholarship registration in `New Registration` unless the cascade marker is set.
4. **Desk.** Skip the `check_beneficiary_id` guard in `beneficiary_request.js` when `frm.doc.is_scholarship` is set, because `ben_id` is created during the same action.
5. **Sanadi lookup (OQ6).** Add the Scholarship lookup id in `get_aid_lookup_parent_id`.

### Known risk
`create_new_beneficiary` calls `frappe.db.commit()` after writing `ben_id`. That breaks atomicity: if the request step fails afterwards, the registration stays Accepted. Options:

- remove the commit (preferred; it violates the project rules anyway);
- accept the partial state and document it.

This needs a decision during the phase. Record it in `progress.md`.

## Tests (mock `requests.post`)
- Approving a scholarship request → registration `Accepted` with `ben_id` set, and the request in `Pending Specialist Approval`.
- Rejecting a scholarship request → registration `Not Accepted` and the request in `Rejected by Supervisor`.
- A Sanadi failure while accepting the registration → neither document changes.
- Directly approving a scholarship registration → error.
- A normal (non-scholarship) request approval is unchanged.

## Done when
The tests pass, and a Supervisor can drive both outcomes from the desk.
