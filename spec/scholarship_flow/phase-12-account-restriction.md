# Phase 12 — Account restriction

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A Supervisor marks a scholarship student's account as restricted once the scholarship ends. The student still logs in and sees their history, sees «تم تقييد حسابك لإنتهاء المنحة», and can't file a new request (P9-6).

**Architecture:**
- **Field.** A Check `is_account_restricted` at `permlevel: 1` on `Beneficiaries Registration`. Only Supervisor (and System Manager) can write it. Frappe keeps the stored value when a beneficiary saves the doc without level-1 access, so their profile saves can't clear it.
- **Reading the flag.** The portal can't read level-1 fields, so a whitelisted endpoint returns the session user's flag.
- **Enforcement.** On the server, in `before_insert_request`.

**Tech Stack:** Frappe v16, Vue 3, frappe-ui `Alert`.

**Spec:** [plan.md §8](plan.md#8-client-feedback-2026-10-29)

## Global Constraints
- Exact copy: AR «تم تقييد حسابك لإنتهاء المنحة», EN "Your account has been restricted because the scholarship has ended."
- Server error for a new request: `_("Your account has been restricted because the scholarship has ended.")`, raised as `frappe.PermissionError`.
- Restricting touches neither the User, nor the role profile, nor Sanadi.
- Endpoints return through `gen_response`.

## Review Focus
- **A beneficiary saves their profile while restricted.** The flag must stay 1 (permlevel reset). Test it.
- **A Specialist tries to set the flag** in the desk or through `frappe.client.set_value`. It is refused.
- **A restricted user opens `/request`.** The create button is disabled with the restriction reason, and a direct insert is refused.
- **The flag on a normal registration.** The field shows only for scholarship records (`depends_on`), and the server rule applies whatever the flow.

---

### Task 1: Field, permission and server guard

**Files:**
- Modify:
  - `afif/afif/doctype/beneficiaries_registration/beneficiaries_registration.json`: the field, plus a permission row `{"role": "Supervisor", "permlevel": 1, "read": 1, "write": 1}` (and the same for System Manager if the doctype grants it at level 0).
  - `afif/hooks_call.py` (`before_insert_request`)
- Test: `afif/api/test_scholarship_accepted.py`

**Interfaces:**
- Produces: field `is_account_restricted` (Check, label "Account Restricted (Scholarship Ended)", `permlevel: 1`, `depends_on: eval:doc.is_scholarship`), placed near `is_scholarship`. Add it to the list view filters with `in_standard_filter: 1`.
- Produces: `class AccountRestrictedError(frappe.PermissionError)` in `hooks_call.py`, raised by `before_insert_request` when the beneficiary's registration has `is_account_restricted`.

- [ ] **Step 1: Write the failing tests.**
  - `test_restricted_student_cannot_file_a_request`: set the flag with `frappe.db.set_value`. `create_scholarship_request(make_accepted_request_data())` raises `AccountRestrictedError`, and no request is created.
  - `test_beneficiary_save_keeps_the_restriction`: as the beneficiary, `frappe.get_doc(...)`, set `is_account_restricted = 0`, change a level-0 field, `save()`. Reload: the flag is still 1.
  - `test_specialist_cannot_restrict`: as a Specialist (helper like `make_supervisor_user`), set the flag and `save()`. The flag is not stored.
  - `test_supervisor_can_restrict`.
- [ ] **Step 2: Run them.** FAIL.
- [ ] **Step 3: Implement.** Check the restriction in `before_insert_request` right after the registration is resolved, before the pending and cooldown checks.
- [ ] **Step 4: Migrate and run the modules.** PASS.
- [ ] **Step 5: Commit.** `feat(scholarship): let supervisors restrict a student's account when the scholarship ends`

### Task 2: Status endpoint and banner

**Files:**
- Modify:
  - `afif/api/scholarship.py`
  - `frontend/src/pages/Scholarship.vue`, `frontend/src/pages/Home.vue`, `frontend/src/pages/Request.vue`
  - `frontend/src/components/request/requestEligibility.js`
  - `frontend/src/locales/translations.js`
- Test: `afif/api/test_scholarship_accepted.py`, `frontend/src/components/request/requestEligibility.test.js`

**Interfaces:**
- Produces: `@frappe.whitelist() get_account_status() -> None`. It responds through `gen_response(200, "", {"is_account_restricted": bool})` for the session user's registration, and `False` when there is none.
- Produces: `getRequestBlockReason(requests, { isAccepted, isScholarship, isRestricted = false, now })` returns `'restricted'` first when `isRestricted`.
- Produces: i18n `scholarship.restricted` and `myRequests.disabledReasons.restricted`, both with the exact copy.

- [ ] **Step 1: Write the failing tests.**
  - Backend `test_account_status_reports_the_restriction`, false then true.
  - Vitest: `isRestricted: true` returns `'restricted'` even with no requests.
- [ ] **Step 2: Run them.** FAIL.
- [ ] **Step 3: Implement.**
  - A small composable `useAccountStatus()` in `frontend/src/composables/useAccountStatus.js` wraps a `createResource` for the endpoint, `auto: true`.
  - `Home.vue` and `Scholarship.vue` show `<Alert theme="red" :title="t('scholarship.restricted')" />` at the top when it is restricted.
  - `Scholarship.vue` hides "apply again".
  - `Request.vue` passes `isRestricted`.
- [ ] **Step 4: Run the backend module, `yarn test` and `yarn build`.** PASS.
- [ ] **Step 5: Commit.** `feat(scholarship): tell a restricted student that the scholarship has ended`

## Done when
- The tests pass.
- Phase 13 QA scenario 5 passes in the browser.
- `progress.md` logs it.
