# Phase 3 — Approval and rejection cascade

> The control point is confirmed: **the Supervisor approves the request, and the registration is approved in the same action** (plan D11).
> OQ3 answered: same as today. The office uploads the signed `declaration` before the Supervisor approves; the Approve transition keeps its `doc.declaration` condition.
> OQ4 answered: block direct Approve/Reject on a scholarship registration. OQ12 answered: the passport number and secondary ID are required, as today.
> OQ6 answered for now: Scholarship is sent to Sanadi as `1001050` (Other Educational Assistance) until Sanadi has its own code.

## Goal
A single Supervisor action on a scholarship request approves or rejects **both** the request and its registration in one transaction.

## Scope
1. **Approve.** `BeneficiaryRequest.on_update` runs before the `on_update` doc_events. When a request with `is_scholarship=1` moves from `Pending Supervisor Approval` to `Pending Specialist Approval`:
   - If the linked registration is in `New Registration`, set its `workflow_state` and `status` to `Accepted` and save it with `ignore_permissions` and the `is_scholarship_decision` flag. The registration's own workflow-transition check still runs. Its `create_new_beneficiary` registers the beneficiary in Sanadi and sets `ben_id`.
   - If the registration still has no `ben_id` (for example, Sanadi authentication failed, which `create_new_beneficiary` only logs), raise `ScholarshipCascadeError` so nothing is saved.
   - Only after that does the `new_subvention_request` hook send the request to Sanadi.
   - `validate` resolves the Sanadi lookup id first, so a missing mapping fails before any Sanadi call.
2. **Reject.** When a scholarship request moves to `Rejected by Supervisor`, set a `New Registration` registration to `Not Accepted`. The request has no notes field, so `custom_notes` is set to "Scholarship request {name} was rejected." (the `rejection_note` validation needs it).
3. **Guard the registration (OQ4).** In the registration's `validate`, block any change to `Accepted` / `Not Accepted` while the registration has a scholarship request in `Pending Supervisor Approval`, unless the cascade flag is set (`ScholarshipDecisionError`). Once the request is closed, the normal workflow applies (see OQ13).
4. **Desk.** `check_beneficiary_id` (called by `beneficiary_request.js` before Approve) returns success for a scholarship request whose registration is still `New Registration`, because `ben_id` is created during the same action.
5. **Sanadi lookup.** In `get_aid_lookup_parent_id`, `Scholarship` maps to `(10010, 1001050)`, shared with Other Educational Assistance.
   - This one branch also covers the Aid, because `new_aid_request` calls the function on the Aid's linked request. No Aid hook changes.
   - An unmapped category or subcategory raises `UnmappedAidLookupError` instead of `UnboundLocalError`.

Only lifecycle step 2 (Supervisor approve) changes; see plan §4. Specialist approval, the committee's "Create Aid" and the Aid workflow stay unchanged.

### Known risk: `frappe.db.commit()` in `create_new_beneficiary` (resolved)
Frappe v16 sets `_disable_transaction_control` while doc_event hooks run, so a `commit()` inside a hook is ignored with a warning. The commit after writing `ben_id` therefore never broke atomicity. It was removed anyway, and the raw SQL was replaced by `frappe.db.set_value`.

The remaining non-transactional part is Sanadi itself. If the request step fails after Sanadi created the beneficiary, the database rolls back but the beneficiary exists in Sanadi.

## Tests (`afif/api/test_scholarship_decision.py`, `requests.post` faked)
- Approving a scholarship request → registration `Accepted` with `ben_id` set, the request in `Pending Specialist Approval`, and the Sanadi beneficiary call made before the subvention request.
- Rejecting a scholarship request → registration `Not Accepted` with a note, the request in `Rejected by Supervisor`, and no Sanadi call.
- A Sanadi failure while accepting the registration (the beneficiary call fails, or authentication fails) → neither document changes.
- Directly approving or rejecting a scholarship registration while its request is pending → error.
- A rejected applicant who resubmits → the Supervisor can approve the registration directly.
- `get_aid_lookup_parent_id`: Education / Scholarship → `(10010, 1001050)`; Tuition Fees unchanged; an unmapped subcategory or category → `UnmappedAidLookupError`.
- An unmapped subcategory on approval → error before any Sanadi call.
- A normal (non-scholarship) request approval is unchanged.
- Approving a scholarship request with no `declaration` is blocked, and the registration stays `New Registration`.
- `new_aid_request` for an Aid linked to an Education / Scholarship request sends `(10010, 1001050)`.
- `check_beneficiary_id` lets a pending scholarship through.

## Done when
The tests pass, and a Supervisor can drive both outcomes from the desk.
