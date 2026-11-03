# Phase 9 — Scholarship requests without cooldowns

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A scholarship request is no longer blocked by the 3-month (rejected) or 6-month (approved) wait. The pending-review block stays, and the normal flow is unchanged (P9-7). Regression checks prove Scholarship stays out of the normal request form (P9-9).

**Architecture:** One condition in `before_insert_request` (server) and the matching option in `getRequestBlockReason` (client). The scholarship page passes the option; the request page doesn't.

**Tech Stack:** Frappe v16 (Python), Vue 3 + Vitest.

**Spec:** [plan.md §8](plan.md#8-client-feedback-2026-10-29)

## Global Constraints
- The normal (non-scholarship) request flow must behave exactly as before.
- Error messages go through `_()`.
- Tests: `bench --site afif.akwad.qa run-tests --module <module>`; `cd frontend && yarn test`.

## Review Focus
- A beneficiary whose **last request is a normal one** and who files a scholarship request gets no cooldown either. That is fine: only scholarship applicants can file one (`create_scholarship_request` checks `is_scholarship` on the registration).
- A scholarship request while the previous one is still **pending** must still fail with "pending review".

---

### Task 1: Server — skip the cooldowns for scholarship requests

**Files:**
- Modify: `afif/hooks_call.py` (`before_insert_request`, lines ~747-798)
- Test: `afif/api/test_scholarship_accepted.py`

**Interfaces:**
- Consumes: `doc.is_scholarship` (set by `new_scholarship_request` in `afif/api/scholarship.py`).

- [ ] **Step 1: Rewrite the cooldown tests.** In `test_scholarship_accepted.py`:
  - `test_recent_rejection_blocks_a_scholarship_request` becomes `test_recent_rejection_does_not_block_a_scholarship_request`.
  - `test_recent_approval_blocks_a_scholarship_request` becomes `test_recent_approval_does_not_block_a_scholarship_request`.
  - `test_approved_scholarship_request_blocks_the_next_request_for_six_months` becomes `..._does_not_block_...`.
  - Each one closes the previous request with a date from yesterday, then asserts that `create_scholarship_request(make_accepted_request_data())` creates a request (`frappe.response["data"]["request"]` exists).
  - Add `test_recent_rejection_still_blocks_a_normal_request`: the same setup through `make_normal_education_request()`, asserting a `frappe.ValidationError` matching `"Three months"`.
- [ ] **Step 2: Run the module and see the new tests fail.** `bench --site afif.akwad.qa run-tests --module afif.api.test_scholarship_accepted` → the three changed tests FAIL with "must pass".
- [ ] **Step 3: Implement.** In `before_insert_request`, keep the pending check. Put the two date checks under `if not doc.is_scholarship:`. Wrap the three messages in `_()`.
- [ ] **Step 4: Run it again.** Expected: OK (15 tests).
- [ ] **Step 5: Commit.** `fix(scholarship): exempt scholarship requests from the request cooldowns`

### Task 2: Client — same rule on the scholarship page

**Files:**
- Modify: `frontend/src/components/request/requestEligibility.js`, `frontend/src/pages/Scholarship.vue` (the `getRequestBlockReason` call)
- Test: `frontend/src/components/request/requestEligibility.test.js`

**Interfaces:**
- Produces: `getRequestBlockReason(requests, { isAccepted, isScholarship = false, now = new Date() })`. With `isScholarship`, the function never returns `cooldownRejected` or `cooldownApproved`.

- [ ] **Step 1: Write the failing tests.**
  - `it('ignores the cooldowns for a scholarship request')`: a last request with status `Rejected` and `rejected_date` from yesterday, with `{ isAccepted: true, isScholarship: true }` → `''`. Do the same with `approved_for_aid_date` → `''`.
  - `it('still blocks a scholarship request while one is pending')`: status `Pending Supervisor Approval` → `'pending'`.
- [ ] **Step 2: Run `yarn test requestEligibility`.** Expected: the first test FAILS.
- [ ] **Step 3: Implement.** Add the option. In `Scholarship.vue`, pass `isScholarship: true`. `Request.vue` stays unchanged.
- [ ] **Step 4: Run `yarn test`.** All PASS.
- [ ] **Step 5: Commit.** `fix(scholarship): show the apply button without a cooldown on the scholarship page`

### Task 3: Regression — Scholarship stays out of the normal flow (P9-9)

**Files:**
- Test: `afif/api/test_scholarship.py`. Extract the sub-category filter if needed: `frontend/src/components/request/requestCategories.js`, test `requestCategories.test.js`.

- [ ] **Step 1: Backend.** Check that an existing test inserts a request with `educational_assistance="Scholarship"` as a beneficiary, through `frappe.get_doc(...).insert()`, and asserts `ScholarshipSubcategoryError` or `ScholarshipFlagChangeError` (`test_normal_flow_beneficiary_cannot_create_a_scholarship_request` and the subcategory tests). If none covers the plain insert, add `test_plain_insert_of_a_scholarship_request_is_refused`.
- [ ] **Step 2: Frontend.**
  - Move `SUBCATEGORY_MAP` from `BeneficiaryRequest.vue` into `requestCategories.js`. Phase 13 reuses it.
  - Export `getSubcategoryOptions(category, { includeScholarship })`, which returns the option values.
  - `BeneficiaryRequest.vue` calls it with `includeScholarship: props.readOnly`.
  - Test: `getSubcategoryOptions('Education Assistance', { includeScholarship: false })` does not contain `'Scholarship'`; with `true` it does.
- [ ] **Step 3: Run the backend module and `yarn test`.** Both PASS.
- [ ] **Step 4: Commit.** `test(scholarship): keep Scholarship out of the normal request form`

## Done when
- The backend modules `test_scholarship`, `test_scholarship_accepted` and `test_scholarship_decision` pass, and `yarn test` passes.
- `progress.md` has the Phase 9 log.
