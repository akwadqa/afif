# Phase 14 — Registration documents after "Update Required"

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Once a scholarship registration has been set to "Update Required", the student uploads the registration documents a normal beneficiary would, and the scholarship request documents stay as they were (P9-10 to P9-15).

**Architecture:**
- **Marker.** `last_required_update_date` tells whether the registration has been through an update. `clear_attachments_and_update_status` sets it on every reset (the desk button and the daily job), and nothing clears it.
- **One rule set.** The server's `get_missing_required_attachments` and the profile's documents card apply the normal rules to the scholarship student. Before the first update, a scholarship registration still needs no documents (P9-2 unchanged).
- **The reset is unchanged.** It already deletes only the files attached to the registration, so the request's files survive. A test pins this.

**Tech Stack:** Frappe v16, Vue 3, Vitest, agent-browser.

**Spec:** [plan.md §8](plan.md#8-client-feedback-2026-10-29)

## Global Constraints
- Use the normal required-documents rules. Don't make a scholarship-specific list.
- First-time scholarship registration and the request flow don't change.
- The reset code (`clear_attachments_and_update_status`, `clear_attachment_fields`) doesn't change.
- New requests stay blocked until a Supervisor accepts the registration again, as today (`before_insert_request` needs Accepted).

## Review Focus
- **A scholarship registration that was never updated.** It still saves with no documents, and the wizard shows no documents card.
- **Old scholarship registrations with the legacy `scholarship_*` fields.** The reset leaves them alone, and they aren't counted as registration documents.
- **The profile, while the status is "Update Required".** The documents card shows the normal list for the student's answers. For a Single student that means no spouse or partner documents.
- **A save with a document still missing.** The status stays "Update Required", in the desk too, not only in the UI.
- **The request after the reset.** Its 4 documents and the other attachments still exist (the File rows and the field values).

---

### Task 1: Server — require the documents after an update

**Files:**
- Modify: `afif/hooks_call.py` (`get_missing_required_attachments`)
- Test: `afif/api/test_scholarship_accepted.py`

**Interfaces:**
- Produces: `get_missing_required_attachments(doc)` returns `[]` for a scholarship registration only while `doc.last_required_update_date` is empty. After that it applies the normal rules.

- [ ] **Step 1: Write the failing tests** (new class `TestScholarshipUpdateRequired(AcceptedBeneficiaryTestCase)`)
  - `test_update_required_keeps_the_request_documents`: create a scholarship request, call `beneficiary_update_required_status_for_document(registration)`. The registration's status is "Update Required", and the request's 4 fields and the File rows (named and other attachments) are unchanged.
  - `test_scholarship_registration_needs_its_documents_after_update_required`: after the reset, save the registration as the beneficiary with no documents. The status stays "Update Required".
  - `test_scholarship_registration_is_updated_once_the_documents_are_in`: upload `qid`, `passport` and `metrash_adress`, plus whatever the fixture's answers require. Save: the status is "Updated beneficiary".
  - `test_scholarship_registration_needs_no_documents_before_any_update`: a regression check that a fresh scholarship registration returns `[]`.
- [ ] **Step 2: Run** `bench --site afif.akwad.qa run-tests --module afif.api.test_scholarship_accepted`. Expected: FAIL.
- [ ] **Step 3: Implement.** Change the scholarship early return to `if doc.is_scholarship and not doc.last_required_update_date: return []`, and update the comment.
- [ ] **Step 4: Run** that module, plus `afif.api.test_scholarship` and `afif.api.test_scholarship_decision`. Expected: PASS.
- [ ] **Step 5: Commit.** `fix(scholarship): require the registration documents after update required`

### Task 2: Profile — show the documents card after an update

**Files:**
- Modify:
  - `frontend/src/components/registration/registrationVariant.js`
  - `frontend/src/components/registration/BeneficiaryRegistration.vue` (load `last_required_update_date`; pass `showDocuments`)
  - `frontend/src/components/registration/registrationValidation.js` (step-4 attachments check)
- Test: `frontend/src/components/registration/registrationValidation.test.js`

**Interfaces:**
- Consumes: the `showDocuments` prop on `AttachmentsCard.vue` (Phase 11).
- Produces: `hasRegistrationDocuments(flow, { hasBeenUpdateRequired }) -> boolean`. It is true for the normal flow, and true for the scholarship flow only when `hasBeenUpdateRequired`. It replaces direct reads of the variant flag.

- [ ] **Step 1: Write the failing tests.**
  - With `hasBeenUpdateRequired`, a scholarship step-4 validation with no documents lists `qid`, `passport` and `metrash_adress`.
  - Without it, the scholarship validation passes with no documents.
  - The normal flow is unchanged.
- [ ] **Step 2: Run** `npx vitest run registrationValidation`. Expected: FAIL.
- [ ] **Step 3: Implement.**
  - The profile reads `last_required_update_date` with the registration.
  - When it is set, step 4 shows `AttachmentsCard` with the normal list and the normal upload behaviour.
  - Step 5 (the request documents) stays read only.
- [ ] **Step 4: Run** `npx vitest run` and `yarn build`. Expected: PASS.
- [ ] **Step 5: Commit.** `feat(scholarship): ask for the registration documents in the profile after update required`

### Task 3: Browser QA (agent-browser)

| # | Scenario | Expected |
|---|---|---|
| 1 | Desk: "Update Required" on an accepted scholarship registration that has a request | Status is "Update Required"; the request still shows its documents |
| 2 | The student opens the profile | Step 4 shows the normal documents card; step 5 shows the request documents read only |
| 3 | Save with a document missing | Error listing the missing documents; status unchanged |
| 4 | Upload all of them, then save | "Updated beneficiary"; `/request` and `/scholarship` stay blocked until the Supervisor accepts again |
| 5 | A new scholarship student registers through the link | No documents card (unchanged) |

- [ ] **Step 1:** Run the scenarios in AR, and repeat scenario 2 at 390px. Record the results in progress.md.
- [ ] **Step 2: Commit.** `docs(scholarship): log phase 14 progress`

## Done when
- The tests and the 5 scenarios pass.
- OQ16 is moved to "Answered".
- `progress.md` is up to date.
