# Phase 11 — Documents on the request, Single only

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A scholarship registration asks for no documents (P9-2). The scholarship request carries 4 required documents plus 0–n optional extras (P9-3), read only once submitted (P9-4). The scholarship marital status is Single only (P9-5).

**Architecture:**
- **Server.** The request doctype owns the 4 file fields. `BeneficiaryRequest.get_missing_scholarship_fields` requires them. Both scholarship endpoints receive file URLs, insert the request, then attach the user's own unattached Files to it: named fields for the 4, no field for the extras.
- **Wizard.** Holds the picked files in memory and uploads them unattached on submit, the way `ScholarshipApplyForm` already does. Nothing is saved on the registration any more.

**Tech Stack:** Frappe v16, Vue 3, Vitest.

**Spec:** [plan.md §8](plan.md#8-client-feedback-2026-10-29)

## Global Constraints
- The normal registration and the normal request flow must not change. Every change is gated on `is_scholarship` or `flow === 'scholarship'`.
- The 10 `scholarship_*` registration fields stay in the doctype, so old records keep their files. They are no longer required, written or shown in the portal.
- The scholarship request files are private (`is_private: '1'`).
- Field labels: `student_id_copy` = "Student ID Copy" / «صورة البطاقة الشخصية للطالب»; `student_passport_copy` = "Student Passport Copy" / «صورة جواز السفر للطالب». `education_invoice` and `grade_transcript` keep their labels; the portal uses «فاتورة الجامعة» and «السجل التراكمي للطالب». Other files: «مرفقات أخرى تود إرفاقها لدعم الطلب».
- Allowed file types and size: the existing `ALLOWED_EXTENSIONS` and `isFileTooLarge`.

## Review Focus
- **A file URL that belongs to another user, or that is already attached somewhere**, in the 4 fields or in `other_attachments`. Raise `PermissionError` and create nothing.
- **The same URL sent twice** (the same file picked for two fields). The second lookup must not reuse the first File: keep the `name not in` exclusion of `get_unattached_own_files`.
- **A failed upload in the middle of a submit.** Files already uploaded are kept as URLs, so a retry doesn't re-upload them (the existing `ScholarshipApplyForm` pattern).
- **A beneficiary edits their profile** (`frappe.client.save` sends the whole doc). The old 10 `scholarship_*` values must survive, so the wizard keeps sending them back unchanged.
- **The desk marks the general registration attachments mandatory on a scholarship record** at `current_step == 5`. Gate them with `!doc.is_scholarship`.

---

### Task 1: Request fields and the server rule for the 4 documents

**Files:**
- Modify: `afif/afif/doctype/beneficiary_request/beneficiary_request.json`, `beneficiary_request.py`
- Test: `afif/afif/doctype/beneficiary_request/test_beneficiary_request.py`

**Interfaces:**
- Produces: `SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS = ("education_invoice", "grade_transcript", "student_id_copy", "student_passport_copy")` in `beneficiary_request.py`.
- Produces: `get_missing_scholarship_fields()`, which now also lists the labels of the missing files.

- [ ] **Step 1: Write the failing tests.**
  - `test_scholarship_request_requires_its_four_documents`: build a scholarship request (flag set, `flags.is_scholarship_submission = True`, declarations, amount, summary). With no files, `get_missing_scholarship_fields()` contains the 4 labels. With the 4 set, it is `[]`.
  - `test_normal_education_request_rules_unchanged`: `get_missing_required_attachments()` for Tuition Fees still returns `["education_invoice", "grade_transcript"]`.
- [ ] **Step 2: Run `bench --site afif.akwad.qa run-tests --module afif.afif.doctype.beneficiary_request.test_beneficiary_request`.** FAIL.
- [ ] **Step 3: Implement.**
  - JSON: add `student_id_copy` and `student_passport_copy` (Attach) right after `grade_transcript`, with `depends_on: eval:doc.educational_assistance=="Scholarship"`.
  - For `education_invoice` and `grade_transcript`, drop `&& doc.educational_assistance != "Scholarship"` from `depends_on`. Keep `mandatory_depends_on` as it is, because the server rule covers scholarship.
  - `get_missing_scholarship_fields` adds the 4 fields to `missing`.
  - `get_missing_required_attachments` stays as it is (it already skips Scholarship).
- [ ] **Step 4: Run `bench --site afif.akwad.qa migrate` and the module.** PASS.
- [ ] **Step 5: Commit.** `feat(scholarship): require the student's documents on the scholarship request`

### Task 2: Endpoints attach the files to the request

**Files:**
- Modify: `afif/api/scholarship.py`
- Test: `afif/api/test_scholarship.py`, `afif/api/test_scholarship_accepted.py`

**Interfaces:**
- Consumes: `SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS` (Task 1).
- Produces: request payload keys `requested_amount`, `request_summary`, the 2 declarations, the 4 file fields (file URLs) and `other_attachments: list[str]` (file URLs, may be empty or missing).
- Produces: `attach_own_files(request_doc: Document, request: dict) -> None` in `scholarship.py`.
  - It finds, for each of the 4 fields and each `other_attachments` URL, a File with `owner == session user` and `attached_to_name` not set, never reusing one already picked. Otherwise it raises `frappe.PermissionError`.
  - It sets `attached_to_doctype="Beneficiary Request"` and `attached_to_name=request_doc.name`, plus `attached_to_field` for the 4 fields.
  - It replaces `get_unattached_own_files` and `attach_files_to_registration`, which are deleted along with `validate_scholarship_attachments_given`.

- [ ] **Step 1: Update the tests.**
  - `make_request_data()` and `make_accepted_request_data()` upload the 4 files with `upload_unattached_file` and include `other_attachments` with one file.
  - `make_registration(is_scholarship=1)` no longer sets `REGISTRATION_ATTACHMENTS` or `SCHOLARSHIP_ATTACHMENTS`. Normal registrations keep `REGISTRATION_ATTACHMENTS`.
  - New and changed assertions:
    - `test_submit_attaches_the_documents_to_the_request`: each of the 4 fields on the request equals the sent URL; the matching File has `attached_to_doctype == "Beneficiary Request"` and the right `attached_to_field`; the extra File is attached to the request with an empty `attached_to_field`; the registration's 10 `scholarship_*` fields are empty.
    - `test_submit_without_registration_documents_succeeds`: a scholarship Draft with no attachment field set is submitted.
    - `test_missing_request_document_creates_nothing`: a subTest for each of the 4 fields; `IncompleteScholarshipRequestError`; the registration is still Draft and has no request.
    - `test_another_users_file_is_rejected` and `test_a_file_already_attached_elsewhere_is_rejected`: run them for a named field and for `other_attachments`.
    - In `test_scholarship_accepted.py`: rename `test_accepted_user_creates_a_scholarship_request_with_its_files_on_the_registration` to `..._on_the_request`, with the same assertions as above.
- [ ] **Step 2: Run the two modules.** The new assertions FAIL.
- [ ] **Step 3: Implement.**
  - `REQUEST_INPUT_FIELDS` gains the 4 fields.
  - `SCHOLARSHIP_REGISTRATION_REQUIRED_FIELDS` loses the 10 `scholarship_*` fields.
  - `validate_registration_complete` no longer calls `get_missing_required_attachments`. It checks only `SCHOLARSHIP_REGISTRATION_REQUIRED_FIELDS`.
  - Both endpoints call `attach_own_files(request_doc, request)` after `request_doc.insert(...)`. On a `PermissionError` the whole transaction rolls back, which the Frappe request handler does.
- [ ] **Step 4: Run all three scholarship modules.** PASS.
- [ ] **Step 5: Commit.** `feat(scholarship): attach the scholarship documents to the request instead of the registration`

### Task 3: Registration — Single only, no documents in the desk

**Files:**
- Modify: `afif/afif/doctype/beneficiaries_registration/beneficiaries_registration.py`, `.json`; `afif/hooks_call.py` (`get_missing_required_attachments`)
- Test: `afif/api/test_scholarship.py` (`TestSingleMaritalStatus`)

**Interfaces:**
- Produces: `ScholarshipMaritalStatusError(frappe.ValidationError)` and `BeneficiariesRegistration.validate_scholarship_marital_status()`. It runs in `validate` when `is_scholarship` is set and `marital_status` is set and is not `"Single"`, on insert or when the value changes.
- Produces: `get_missing_required_attachments(doc)` returns `[]` when `doc.is_scholarship`. `is_registration_complete` and the `updated_status` hook then treat scholarship registrations as complete once the consents are given.

- [ ] **Step 1: Write the failing tests.**
  - `test_scholarship_registration_refuses_married`: a subTest per value in `Married`, `Divorced`, `Widowed` and `Separated` → `ScholarshipMaritalStatusError`.
  - `test_scholarship_registration_accepts_single`.
  - `test_normal_registration_still_refuses_single` (regression; one may already exist).
  - `test_scholarship_registration_needs_no_attachments`: `get_missing_required_attachments` on a scholarship doc with no files → `[]`. On a normal doc it is unchanged.
- [ ] **Step 2: Run them.** FAIL.
- [ ] **Step 3: Implement.**
  - In the JSON, prefix every `mandatory_depends_on` of an `Attach` field that starts with `eval: doc.current_step == 5` with `!doc.is_scholarship && `. Do it with a script to avoid hand edits, and check the result with `git diff`.
  - `scholarship_attachments_tab`: change `depends_on` to `eval:doc.is_scholarship && doc.scholarship_university_invoice`, so the tab shows only on old records.
  - Delete the `SCHOLARSHIP_ATTACHMENT_FIELDS` constant if nothing imports it any more. Tests that need the old names use a local tuple.
- [ ] **Step 4: Migrate, then run the three scholarship modules and `test_beneficiaries_registration`.** PASS.
- [ ] **Step 5: Commit.** `feat(scholarship): register scholarship applicants as single, without documents`

### Task 4: Frontend config and validation

**Files:**
- Modify: `frontend/src/components/registration/registrationVariant.js`, `registrationValidation.js`
- Test: `frontend/src/components/registration/registrationValidation.test.js`

**Interfaces:**
- Produces, in `registrationVariant.js`:
  - `SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS = ['education_invoice', 'grade_transcript', 'student_id_copy', 'student_passport_copy']`.
  - `LEGACY_SCHOLARSHIP_ATTACHMENT_FIELDS`: the 10 old names, only so `ATTACHMENT_FIELDS` keeps sending them back.
  - `SCHOLARSHIP_VARIANT.maritalStatuses = ['Single']`.
  - A new variant flag `hasRegistrationDocuments`: `true` for the normal variant, `false` for scholarship.
- Produces: the step-5 form data shape. `scholarshipRequest.files` is `{ [field]: File | string | null }` for the 4 fields, plus `other_attachments: Array<File | string>`.

- [ ] **Step 1: Write the failing tests.**
  - The scholarship variant offers only `['Single']`.
  - Step 4/2 in scholarship mode with no files and all 3 consents → no errors. With a consent missing → an error for that consent.
  - Step 5 in scholarship mode with `scholarshipRequest.files` empty → an error for each of the 4 (`attach_<field>`). With the 4 set and `other_attachments: []` → no file errors.
  - A submitted request (`isSubmitted: true`) on step 5 → no errors (P9-4). This replaces the Phase 8 test that checks the documents.
  - Normal flow step 4/2 is unchanged (regression).
- [ ] **Step 2: Run `yarn test registrationValidation`.** FAIL.
- [ ] **Step 3: Implement.** `validateAttachmentsStep` skips the documents when `!variant.hasRegistrationDocuments`. `validateScholarshipRequestStep` reads `sr.files` and returns early when `sr.isSubmitted`.
- [ ] **Step 4: Run `yarn test`.** PASS.
- [ ] **Step 5: Commit.** `feat(scholarship): validate the request documents instead of registration documents`

### Task 5: Wizard, request card and apply form

**Files:**
- Modify:
  - `frontend/src/components/registration/BeneficiaryRegistration.vue`
  - `ScholarshipRequestCard.vue`
  - `ScholarshipApplyForm.vue`
  - `AttachmentsCard.vue`
  - `frontend/src/locales/translations.js`

**Interfaces:**
- Consumes: Task 4 constants and shape. The endpoints' payload (Task 2).
- `ScholarshipRequestCard` props change:
  - `files` now means `modelValue.files`, so the card owns the 4 fields and `other_attachments` through `v-model`.
  - The `select-file`, `remove-file`, `uploading` and `uploadErrors` props and events are removed.
  - New prop: `documentsReadOnly: Boolean`.
- `AttachmentsCard` gains the prop `showDocuments: Boolean` (default `true`).

- [ ] **Step 1: `AttachmentsCard`.** With `showDocuments` false, render only the consents block. The wizard passes `:show-documents="variant.hasRegistrationDocuments"`.
- [ ] **Step 2: `ScholarshipRequestCard`.**
  - Render the 4 required rows from `SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS` (pick, replace, delete, all local).
  - Render a multi-file «مرفقات أخرى» list: add, remove, no asterisk. Reuse the `additional_attachments` UI pattern from `AttachmentsCard`.
  - With `documentsReadOnly`, show each document as a link (`<a :href="url" target="_blank">`) and hide the buttons.
- [ ] **Step 3: Extract a shared upload helper.** Add `uploadScholarshipRequestFiles(files): Promise<object>` in a new `frontend/src/components/registration/scholarshipRequestFiles.js`.
  - It uploads each `File` with `uploadFile(file, { is_private: '1' })`, storing the URL back in place so a retry reuses it.
  - It returns `{ ...4 fields: url, other_attachments: url[] }`.
  - Both `ScholarshipApplyForm.submitRequest` and `BeneficiaryRegistration.submitScholarshipApplication` use it, and both send `request: { ...requestData, ...uploadedFiles }`.
- [ ] **Step 4: `BeneficiaryRegistration.vue`.**
  - Remove the scholarship parts of `handleAttachmentFileSelected`, `removeScholarshipAttachment`, `queueAttachmentSave` and `uploadRegistrationFile`'s `is_private` branch.
  - Remove the `pendingAttachmentOps` wait on step 5 if nothing else uses it.
  - `ATTACHMENT_FIELDS` uses `LEGACY_SCHOLARSHIP_ATTACHMENT_FIELDS`.
  - `latestScholarshipRequest` also fetches the 4 fields and maps them into `scholarshipRequest.files`.
  - Pass `:documents-read-only="isSubmittedApplication"`.
  - `finishScholarshipRegistrationEdit` stays as it is: it saves the registration only.
- [ ] **Step 5: i18n.**
  - Under `scholarship.attachments`, AR and EN: `education_invoice`, `grade_transcript`, `student_id_copy`, `student_passport_copy`, `other_attachments`, `addOther`.
  - Keep the old keys only if a remaining view uses them; delete the rest.
- [ ] **Step 6: Run `yarn test`, `yarn lint` and `yarn build`.** All pass.
- [ ] **Step 7: Commit.** `feat(scholarship): collect the scholarship documents with the request`

## Done when
- All backend modules and `yarn test` pass.
- Phase 13 QA scenarios 3 and 4 pass in the browser.
- `progress.md` logs the test counts and the reversal of OQ11 and P8-1/P8-2.
