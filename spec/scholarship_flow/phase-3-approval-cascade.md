# Phase 3 — Approval and rejection cascade

> The control point is confirmed: **the Supervisor approves the request, and the registration is approved in the same action** (plan D11).
> OQ3 answered: same as today. The office uploads the signed `declaration` before the Supervisor approves; the Approve transition keeps its `doc.declaration` condition.
> OQ4 answered: block direct Approve/Reject on a scholarship registration. Still open: OQ6 (the Sanadi lookup id) and OQ12 (Sanadi beneficiary payload).

## Goal
A single Supervisor action on a scholarship request approves or rejects **both** the request and its registration in one transaction.

## Scope
1. **Approve.** Hook into the request's `validate` (or `before_save`). When a request with `is_scholarship=1` moves from `Pending Supervisor Approval` to `Pending Specialist Approval`:
   - Accept the linked registration first by setting `workflow_state` and `status` to `Accepted` and saving it, with `ignore_permissions` and a `frappe.flags` marker. Its `create_new_beneficiary` then registers the beneficiary in Sanadi and sets `ben_id`.
   - Only after that do the request's own Sanadi hooks run (`validate_subvention_request`, `new_subvention_request`).
2. **Reject.** When a scholarship request moves to `Rejected by Supervisor`, set the registration to `Not Accepted` with a `custom_notes` copied from the request. The `rejection_note` validation needs it.
3. **Guard the registration (OQ4).** In the registration's `validate`, block direct Approve/Reject on a scholarship registration in `New Registration` unless the cascade marker is set.
4. **Desk.** Skip the `check_beneficiary_id` guard in `beneficiary_request.js` when `frm.doc.is_scholarship` is set, because `ben_id` is created during the same action.
5. **Sanadi lookup.** In `get_aid_lookup_parent_id`, the Education branch (parent `10010`) gets `educational_assistance == "Scholarship"` → `aidLookupId` from OQ6.
   - This one branch also covers the Aid, because `new_aid_request` calls the function on the Aid's linked request. No Aid hook changes.
   - Also make an unmapped category or subcategory raise a clear `frappe.throw` instead of `UnboundLocalError`.

Only lifecycle step 2 (Supervisor approve) changes; see plan §4. Specialist approval, the committee's "Create Aid" and the Aid workflow stay unchanged.

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
- `get_aid_lookup_parent_id`:
  - Education / Scholarship → `(10010, <OQ6 id>)`;
  - an unmapped subcategory → clear error.
- A normal (non-scholarship) request approval is unchanged.
- Approving a scholarship request with no `declaration` is blocked, and the registration stays `New Registration`.
- `new_aid_request` for an Aid linked to an Education / Scholarship request sends `(10010, <OQ6 id>)`.

## Done when
The tests pass, and a Supervisor can drive both outcomes from the desk.
