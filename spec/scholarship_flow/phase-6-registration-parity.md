# Phase 6 — Registration parity and attachments on the registration

Review edits from 2026-10-20. They undo the field variants from Phases 2 and 5, and move the scholarship documents from the request to the registration.

## Decisions (grilled with the mentor, 2026-10-20)

| # | Decision |
|---|---|
| P6-1 | **Same fields as the normal registration.** The scholarship wizard shows every field the normal wizard shows, with the same labels and the same required rules: no hidden fields and no relabels. The desk drops its 18 `!doc.is_scholarship` guards. |
| P6-2 | **Father and mother income are removed completely:** the fields, the wizard, the Sanadi income mapping and the tests. The income and obligations steps are identical to the normal ones. |
| P6-3 | **What stays scholarship-only:** `guardian_mobile_number` (required), marital status `Single`, and step 5 بيانات الطلب. |
| P6-4 | **The 10 scholarship documents are registration fields.** They sit in a new Tab "Scholarship Attachments" on Beneficiaries Registration, shown when `is_scholarship`. The 8 `scholarship_*` fields are removed from Beneficiary Request, and the request keeps the amount, the summary and the 2 declarations. The university invoice and the transcript get their own registration fields. |
| P6-5 | **The wizard still shows the documents in step 5**, together with the amount, the summary and the declarations. |
| P6-6 | **Scholarship can only be requested through `/scholarship`.** The request page no longer offers it. The server ties the subcategory to the flag: a request is Education → Scholarship **if and only if** `is_scholarship = 1`, and only the scholarship endpoints can set the flag. This blocks direct API inserts and desk edits. |
| P6-7 | **Accepted beneficiaries get step 5 only on `/scholarship`.** The documents go onto their registration's scholarship tab, and the request is created with the normal rules (one open request, the 3- and 6-month cooldowns). |
| P6-8 | **Upload, new applicant (Draft).** Each document is uploaded when it is picked: native `upload_file`, `is_private: 1`, attached to the Draft by field, and saved to the Draft straight away (the same path as the registration attachments). Submit only checks that the fields are filled. |
| P6-9 | **Upload, accepted beneficiary.** The beneficiary can't save an Accepted registration (the workflow's `allow_edit` is Supervisor only). So the files are uploaded private and unattached when Submit is pressed. The endpoint checks that each file is theirs and unattached, inserts the request, writes the URLs onto the registration with `db_set` (no save, so no Sanadi hooks) and attaches the File records, all in one transaction. |
| P6-10 | **Normal registration uploads stay public** (mentor's choice). |
| P6-11 | **Replacing or deleting a document removes its old File record.** On every registration save, the File records attached to the replaced or cleared URL of that field are deleted. The yearly "Update Required" reset (raw SQL) and the existing unattached files are out of scope. |
| P6-12 | **No data patch.** Only demo records use the removed fields. |
| P6-13 | **OQ14 closed:** years of residence is asked of every applicant, as in the normal wizard. OQ10 (21+ in the wizard only) is unchanged. |

## Data model

### Beneficiaries Registration
- **Removed:** `father_income`, `father_income_periodicity`, `father_income_amount`, `father_income_note`, and the same 4 for `mother_`.
- **Desk:** the `!doc.is_scholarship` guards from Phase 4 are dropped.
- **New Tab** `scholarship_attachments_tab` "Scholarship Attachments", `depends_on: eval:doc.is_scholarship`, holding these Attach fields:

| Field | Label (AR) |
|---|---|
| `scholarship_university_invoice` | فاتورة الجامعة |
| `scholarship_grade_transcript` | السجل التراكمي للطالب |
| `scholarship_guardian_id` | صورة البطاقة الشخصية لولي الأمر أو مقدم الطلب |
| `scholarship_guardian_passport` | صورة جواز السفر لولي الأمر أو مقدم الطلب |
| `scholarship_student_id` | صورة البطاقة الشخصية للطالب |
| `scholarship_student_passport` | صورة جواز السفر للطالب |
| `scholarship_family_ids` | صور البطاقات الشخصية لجميع أفراد العائلة |
| `scholarship_guardian_bank_statement` | كشف الحساب لولي الأمر |
| `scholarship_mother_bank_statement` | كشف حساب الأم |
| `scholarship_student_bank_statement` | كشف حساب الطالب |

`SCHOLARSHIP_ATTACHMENT_FIELDS` moves to `beneficiaries_registration.py`.

### Beneficiary Request
- **Removed:** the 8 `scholarship_*` Attach fields.
- `education_invoice` / `grade_transcript` are no longer used by Scholarship.
- **Validation** of an Education / Scholarship request: amount > 0, summary, and both declarations.

## Backend

- **`afif/api/scholarship.py`**
  - `submit_scholarship_application(registration, request)`: `request` carries only the amount, the summary and the declarations. The registration check also requires the 10 scholarship attachments. The file handling is gone, because the files are already on the Draft.
  - `create_scholarship_request(request)` (accepted beneficiary, P6-9): the request carries the 10 file URLs. The request is built with `is_scholarship = 1` and inserted with normal permissions, so `before_insert_request` applies its rules. The files are then written to the registration and attached to it.
- **`before_insert_request`** skips the accepted-only rules only for the new-applicant submission (`flags.is_new_scholarship_applicant`), not for every scholarship request.
- **`BeneficiaryRequest.validate`**: Scholarship subcategory ⇔ `is_scholarship` (P6-6).
- **`BeneficiariesRegistration`**
  - `on_update` deletes the File records of replaced or cleared Attach values (P6-11).
  - The OQ4 guard only applies while the registration is `New Registration`. Without this, an Accepted beneficiary's pending scholarship request would block the Supervisor from changing their registration.
- **`get_beneficiary_income_set`**: the father/mother loop is removed.
- **Unchanged:** the Sanadi lookup `1001050` (Other Educational Assistance) and the approval cascade.

## Frontend

- **`registrationVariant.js`**: the variants differ only in `hiddenFields` (`guardian_mobile_number` is hidden in the normal flow) and `maritalStatuses`. The income sources, the obligation labels and the bank-loans label are the normal ones for both flows.
- **The cards** (`PersonalInfoCard`, `FamilyDetailsCard`, `IncomeDetailsCard`, `FinancialObligationsCard`, `AdditionalDataCard`) drop the scholarship-only branches.
- **`BeneficiaryRegistration.vue`**
  - The scholarship documents live in `formData.attachments.files` with the other registration documents. They are loaded from the doc, uploaded on pick (private) and saved with the attachments payload.
  - Step 5 waits for pending uploads, then calls the endpoint with the amount, the summary and the declarations.
- **`ScholarshipRequestCard.vue`**: the files come in as a prop. Picking or deleting a file emits an event, so the parent decides whether it uploads now (Draft) or at submit (accepted).
- **`pages/Scholarship.vue`**: an Accepted beneficiary gets step 5 only (a new `ScholarshipApplyForm.vue` that wraps the card), with the success view on submit. Accepted users who can't create a request (pending request or cooldown) see the server's message.
- **`BeneficiaryRequest.vue` / `requestAttachments.js` / `Request.vue`**
  - Scholarship is no longer offered for a new request. It is still shown when viewing an existing scholarship request, with its declarations.
  - The scholarship upload path and the `?category=&subcategory=` preset are removed.
- **`translations.js`**: the scholarship relabels and the father/mother keys are removed, and the 2 new attachment keys are added.

## Tests

- **Backend**
  - Submit with all 10 registration attachments → the request is Education / Scholarship, `is_scholarship = 1`, and the registration is `New Registration`.
  - A missing scholarship attachment, amount, summary or declaration → nothing submitted.
  - Accepted beneficiary:
    - Files land on the registration fields, attached to it by field and private. The request is `is_scholarship = 1`, and the registration stays Accepted.
    - Someone else's file, or a file already attached elsewhere → `PermissionError`, nothing written.
    - The cooldowns still apply.
    - Supervisor approval does not cascade.
  - Inserting a Scholarship request without the endpoint → refused, for both a new and an accepted user. Turning a normal request into Scholarship → refused.
  - Replacing a registration attachment deletes the old File record, but not another field's File record with the same URL. Clearing a field deletes its File record too.
  - The father/mother income tests are removed. The Sanadi lookup test still pins `(10010, 1001050)`.
- **Vitest**
  - The scholarship variant hides nothing and uses the normal income and obligation labels.
  - Step 5 requires the 10 documents from `attachments.files`.
  - The request page offers no Scholarship for a new request.
  - AR/EN keys exist.
- **Browser**
  - A new applicant goes through the whole wizard. Every normal field is shown, the step-5 uploads land on the Draft, and the submit works.
  - An Accepted beneficiary on `/scholarship` sees step 5 only, and submits.
  - `/request` doesn't offer Scholarship.
  - The desk shows the new tab.

## Done when

The tests pass, `migrate` and `yarn build` are done, and both paths have been walked through in the browser.
