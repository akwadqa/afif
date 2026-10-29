# Scholarship Flow (منحة الشيخ خالد بن ناصر) — Plan

**Branch:** `feature/scholarship-flow`
**Design:** Figma `Afif-Charity`, node `723:1544` (step 5 "بيانات الطلب")

## 1. Requirement

Today a beneficiary must:

1. Register through the 5-step wizard.
2. Wait for a Supervisor to accept the registration.
3. Submit an aid request.

The scholarship is one combined flow:

- **One wizard.** It uses the registration steps with the same fields as the normal registration (Phase 6), plus the guardian mobile, the `Single` marital status and a new step **بيانات الطلب** (request data).
- **One atomic submission.** The registration moves to `New Registration`, and a Beneficiary Request (Education Assistance → Scholarship) is created in `Pending Supervisor Approval`.
- **A flag on both documents** separates scholarship records from the normal flow.
- **When the Supervisor approves the request, the related registration is approved in the same action.**

The normal registration flow and the normal aid request flow stay unchanged.

## 2. Decisions

| # | Decision |
|---|---|
| D1 | Add a read-only Check `is_scholarship` to `Beneficiaries Registration` and to `Beneficiary Request`. It shows in the list view and as a standard filter. It can only be set on insert; `validate` throws if it changes afterwards. On the request it means "created through the scholarship flow", and that is what triggers the approval cascade (D11). Since Phase 6, a request is Education → Scholarship if and only if it has the flag, and only the scholarship endpoints set it. |
| D2 | A scholarship is a **subcategory of Education Assistance**: `request_category = "Education Assistance"` and `educational_assistance = "Scholarship"`. There is no new category and no new DocType. The `Categories` tree already has `Education Assistance`, so it is not touched. |
| D3 | *(Changed in Phase 11: the scholarship wizard asks for no registration documents; the attachments sub-step keeps only the consents.)* Wizard steps: 1 البيانات الشخصية · 2 تفاصيل الدخل · 3 الالتزامات المالية · 4 بيانات إضافية, followed by the **same registration attachments sub-step** as the normal flow · 5 بيانات الطلب. |
| D4 | *(Superseded by Phase 6: the 10 attachments are registration fields, in their own tab; step 5 still shows them.)* Step 5 belongs entirely to the **request**: the requested amount, the request summary (OQ1b), 10 required attachments (8 at first; 2 bank statements added in Phase 5) and the request declarations. All of it is stored on the Beneficiary Request, not on the registration. Two of the attachments reuse existing Education fields (§3); this attachment list replaces the older one in Figma. |
| D5 | Drafts are saved step by step, exactly as today. A single whitelisted endpoint, `submit_scholarship_application`, validates **all** registration attachments and consents **and** all step-5 data. In one transaction it submits the registration and creates the request. If anything is missing, nothing is submitted. |
| D6 | The existing DB Workflows stay as they are. The cascade logic lives in server hooks. Moving to status-only workflows is out of scope. |
| D7 | Eligibility: the scholarship wizard is open to users with no registration, or with their own scholarship Draft. Since Phase 7, `/scholarship` is only for scholarship registrations: a normal-flow beneficiary cannot apply there, and an accepted scholarship beneficiary can file a new scholarship request under the request page's rules. |
| D8 | *(Superseded by Phase 6: same fields and labels as the normal registration; father/mother income removed.)* Where a field means the same thing, reuse it with a scholarship label. Where the meaning differs, add a new field (§3). The father and mother incomes are **new fields**. |
| D9 | *(Replaced in Phase 8.)* Rejecting a scholarship request only rejects the request, as in the normal request flow; the registration is left as it is and follows its own workflow. |
| D10 | *(Changed in Phase 10: no sidebar item; `/scholarship` is reached only through the shared link.)* Frontend: add a sidebar item "منحة الشيخ خالد بن ناصر" at route `/scholarship`. `BeneficiaryRegistration.vue` is reused with `flow="scholarship"`, and each card reads a variant config. The public nav link `khaledGrant` (terms page) stays unchanged. |
| D11 | **The request is the control point.** When the Supervisor approves a scholarship request, the linked registration is accepted in the same action. The registration is accepted first, so Sanadi creates the beneficiary and sets `ben_id` before the request's Sanadi hooks run. |

## 3. Data model

> **Phase 6 changes this section.** The father/mother income fields are removed, the 8 `scholarship_*` request fields move to a new registration tab (with 2 new fields for the invoice and the transcript), and the field mapping below no longer applies: the scholarship wizard uses the normal fields and labels. See [phase-6-registration-parity.md](phase-6-registration-parity.md).

### Beneficiaries Registration (new fields)

| Field | Type | Notes |
|---|---|---|
| `is_scholarship` | Check, read only | in list view and standard filter |
| `guardian_mobile_number` | Data | رقم جوال ولي الأمر, 8 digits, required in scholarship mode |
| `father_income` | Check | هل لديك دخل ولي الأمر (الأب)؟ |
| `father_income_periodicity` | Select `Yearly\nMonthly\nOthers` | `depends_on: father_income` |
| `father_income_amount` | Data | numeric only, same as the existing amount fields |
| `father_income_note` | Small Text | |
| `mother_income` | Check | هل لديك دخل الأم إن كانت تعمل؟ |
| `mother_income_periodicity` / `mother_income_amount` / `mother_income_note` | same types as the father fields | |

### Beneficiary Request

| Field | Change | Notes |
|---|---|---|
| `is_scholarship` | new Check, read only | in list view and standard filter |
| `educational_assistance` | add option `Scholarship` | Education subcategory |
| `requested_amount` | existing, reused | required in step 5 |
| `education_invoice` | existing Attach, reused | فاتورة الجامعة |
| `grade_transcript` | existing Attach, reused | السجل التراكمي للطالب |
| `scholarship_guardian_id` | new Attach | صورة البطاقة الشخصية لولي الأمر أو مقدم الطلب |
| `scholarship_guardian_passport` | new Attach | صورة جواز السفر لولي الأمر أو مقدم الطلب |
| `scholarship_student_id` | new Attach | صورة البطاقة الشخصية للطالب |
| `scholarship_student_passport` | new Attach | صورة جواز السفر للطالب |
| `scholarship_family_ids` | new Attach | صور البطاقات الشخصية لجميع أفراد العائلة |
| `scholarship_guardian_bank_statement` | new Attach | كشف الحساب لولي الأمر |
| `scholarship_mother_bank_statement` | new Attach (Phase 5) | كشف حساب الأم |
| `scholarship_student_bank_statement` | new Attach (Phase 5) | كشف حساب الطالب |
| `is_data_accuracy_declared` | new Check | اقر أنا مقدم الطلب بأن كافة الوثائق والبيانات المقدمة في هذا الطلب صحيحة. |
| `is_eligibility_check_accepted` | new Check | يحق لمؤسسة عفيف التأكد من أهلية مقدم الطلب بحسب اجراءاتها المتبعة. |

- **Visibility.** The new Attach fields use `depends_on: eval:doc.request_category=="Education Assistance" && doc.educational_assistance=="Scholarship"`. For that subcategory, all 10 attachments, the amount, the summary and both declarations are required, and the server enforces it.
- **Third Figma declaration dropped.** It says "this is only a registration, not an aid request", which is a registration consent and is already covered by the registration attachments sub-step.

### Where the Scholarship subcategory must be added

There is no single source for subcategories; each place below holds its own copy:

| Place | What to add |
|---|---|
| `beneficiary_request.json` → `educational_assistance` (Select) | option `Scholarship` |
| `beneficiary_aid.json` → `educational_assistance` (Select, its own copy) | option `Scholarship`. The committee fills this in by hand on the Aid: the "Aid Button" Client Script copies only `request_category`, `beneficiaries`, `beneficiary_request` and `suggested_amount`. |
| `frontend/src/components/request/BeneficiaryRequest.vue` → `SUBCATEGORY_MAP['Education Assistance'].options` and `requiredDocs` | `Scholarship`, plus the 6 extra docs when it is selected |
| `locales/translations.js` | `request.subtypes.education.Scholarship` (AR منحة دراسية / EN Scholarship) |
| `hooks_call.py` → `get_aid_lookup_parent_id`, Education branch | `educational_assistance == "Scholarship"` → parent `10010` (Education), `aidLookupId` `1001050` (Other Educational Assistance) for now (OQ6) |

### Field mapping in scholarship mode

| Existing field(s) | Scholarship behaviour |
|---|---|
| `ben_income` | reused, for the applicant's own income (Phase 5). Label: هل لديك (دخل/راتب)؟; sub-fields keep the beneficiary wording |
| `marital_status` | option `Single` (أعزب) added, offered only in the scholarship wizard; the server refuses it on a normal registration (Phase 5) |
| `bank_loans` | relabelled: هل لديك أو لدى رب الأسرة التزامات بنكية ومديونيات؟ (Phase 5) |
| `private_income` | reused. Label: هل يوجد دخل للأسرة من عمل خاص أو تجارة منزلية؟ |
| `stock_income` | reused unchanged |
| `family_income`, `family_extra`, `children_income`, `rent_income` | hidden (replaced by the new `father_income` / `mother_income`) |
| `family_obligation` | relabelled: هل لدى الأسرة التزامات مالية؟ |
| `rent_obligation` | relabelled: هل لدى الأسرة التزامات دفع إيجار شهرية؟ |
| `treatment_obligation` | relabelled: هل لدى الأسرة التزامات دفع مصاريف علاج شهرية مستمرة؟ |
| `debt_obligation` | relabelled: هل لدى الأسرة ديون بنكية أو شخصية؟ |
| `tuition_obligation` | relabelled: هل لدى الأسرة التزامات بمصاريف مدرسية وجامعية؟ |
| `id_expiry_date`, `partners_phone_number`, `worked_before`, `family_visa_type`, `visa_dependent`, `have_children` (+ children sub-fields), `afif_charity_assistance` (+ `affif_assistance`) | hidden and not required. `passport_number` and the `ben_sec_*` group stay shown and required, as in the normal flow (OQ12). |

In the Sanadi integration, `father_income` and `mother_income` map to income type 5 (family) in `get_beneficiary_income_set`.

## 4. Request → Aid lifecycle and Sanadi lookup ids

### Lifecycle (unchanged for scholarship except step 2)

| # | Who | Action | Status | Sanadi |
|---|---|---|---|---|
| 1 | Beneficiary | Submit | Request: Pending Supervisor Approval | nothing |
| 2 | **Supervisor** | Approve | Request: Pending Specialist Approval | request created (`new_subvention_request`, both lookup ids sent) |
| 3 | Specialist | Approve | Request: Approved | request approved |
| 4 | Committee | "Create Aid" workflow action | Request: Approved For Aid | — |
| 5 | Committee | "Create Aid" button (DB Client Script "Aid Button") → new Beneficiary Aid, saved by hand | Aid: New Aid | — |
| 6 | Committee → Accountant | Aid: Submit → Approve | Aid: Under Processing → Approved | aid sent (`new_aid_request`, using the **request's** lookup ids) |

- **Approving the request does not create the Aid.** The Aid is a separate, manual step (4–5).
- **The scholarship changes only step 2.** The linked registration is accepted in the same action, before the request is sent to Sanadi (D11). Steps 3–6 stay as they are.

### Lookup ids

- **The mapping.** `get_aid_lookup_parent_id` (`hooks_call.py:952`) maps the request's category to `aidLookupParentId` and its subcategory to `aidLookupId`. These are hardcoded Sanadi codes; nothing is stored or fetched. Education is parent `10010`, with children `1001010`–`1001050`.
- **Callers.**
  - `new_subvention_request` (`:851`) calls it with the request.
  - `new_aid_request` (`:1344`) loads the Aid's linked Beneficiary Request and calls it with that.

  The Aid never uses its own category fields for Sanadi, so a single Scholarship branch covers both the request and the Aid.
- **Status for Scholarship.** Parent `10010` (Education), `aidLookupId` `1001050` (Other Educational Assistance). This is temporary until Sanadi has a dedicated Scholarship code (OQ6).
- **An unmapped category or subcategory** now fails with `UnmappedAidLookupError` (it used to crash with `UnboundLocalError`).

## 5. Affected areas

- **Backend:**
  - `beneficiaries_registration.json`, `beneficiary_request.json` and `beneficiary_aid.json` (the `Scholarship` option only)
  - `afif/hooks_call.py`: `before_insert_request`, `get_beneficiary_income_set`, `get_aid_lookup_parent_id`, and the request transition hooks in Phase 3
  - new `afif/api/scholarship.py`
- **Desk:** the `check_beneficiary_id` guard used by `beneficiary_request.js` lets a pending scholarship through (Phase 3, changed on the server, not in the JS).
- **Frontend (`frontend/src`):**
  - `router.js`
  - `components/sidebar/AppSidebar.vue`, `navbar/MobileMenu.vue` and `navbar/NavLinks.vue`
  - new `pages/Scholarship.vue`
  - `components/registration/BeneficiaryRegistration.vue` and its cards
  - new `ScholarshipRequestCard.vue`
  - `components/request/BeneficiaryRequest.vue`
  - `locales/translations.js`
- **Sanadi:** the beneficiary payload (new income types) and the subvention request lookup (OQ6).

## 6. Go-live prerequisites

- `bench migrate` (new fields), `bench clear-cache`, `bench restart`, and a frontend build.
- Scholarship is sent to Sanadi as `1001050` (Other Educational Assistance) until Sanadi has a Scholarship code (OQ6). Swap the code in `get_aid_lookup_parent_id` when it does.

## 7. Open questions

### Answered

| # | Answer |
|---|---|
| OQ1 | Step 5 includes the requested amount. |
| OQ2 | The Supervisor approves the request, and the registration is approved in the same action (D11). |
| OQ7 | The father and mother incomes are new fields. |
| OQ8 | The last step is for the request: its attachments and declarations are stored on the Beneficiary Request (D4). |
| OQ9 | Scholarship is a subcategory under Education Assistance (D2). |
| OQ4 | Yes. A scholarship registration changes only through its request: a direct Approve/Reject on it is blocked (Phase 3). |
| OQ1b | Yes. Step 5 includes `request_summary`, and it is required (same as the normal request page). |
| OQ3 | Same as today. After submitting, the applicant visits the office to sign the declaration; the office uploads it, then the Supervisor approves (the Approve transition keeps its `doc.declaration` condition, and that approval sends the declaration to Sanadi). The Specialist then finishes the normal flow. No workflow change. |
| OQ5 | Keep the normal rules for scholarship requests: one open request at a time, the 3-month cooldown after a rejection and the 6-month cooldown after an approval, and scholarship requests count as the latest request for later ones. The only exception is the new-applicant scholarship submission, which skips "only an accepted beneficiary can create a request" because the registration is submitted with it (already built in Phase 1). |
| OQ11 | Keep today's rule: the registration `passport` copy stays required, so a scholarship applicant uploads it in the attachments sub-step and the guardian's and student's passports again in step 5. |
| OQ6 | For now, Scholarship uses `aidLookupId` `1001050` (Other Educational Assistance) under parent `10010`, for both the request and the Aid. It changes when Sanadi provides a dedicated code. |
| OQ14 | Phase 6: the scholarship wizard is identical to the normal one, so years of residence is asked of every applicant. |
| OQ13 | Phase 8: a rejected scholarship request stays final, as in the normal request flow, and the registration is not touched by the rejection. The applicant edits the registration in the profile; a new scholarship request follows the request rules. |
| OQ12 | Keep today's rule: the passport number (and the secondary-ID group that carries it to Sanadi) is required. No beneficiary has ever been accepted without one, so there is no evidence Sanadi accepts it empty. |
| OQ16 | No. "Update Required" leaves the scholarship request documents as they were; the student re-uploads the normal registration documents instead (P9-10 to P9-15, Phase 14). |

### Still open

| # | Question | Blocks |
|---|---|---|
| OQ15 | Should the Supervisor be able to ask for an update on a pending scholarship application, instead of only Approve/Reject? Left as is (Phase 8). | — |
| OQ10 | The wizard requires the applicant to be at least 21; there is no server-side age check, in the normal flow either. The scholarship keeps the same rule for now. If the applicant is the student, most students are blocked. Mentor to check later. | — |
| OQ17 | Is «هل لديك أبناء؟» (`have_children`) needed in the scholarship flow? The applicant is always Single (P9-5), yet the field is required in step 2, and «Yes» opens the children fields and the children's ID attachment. Ask the mentor: hide it (and the children fields) for scholarship, or keep it. | — |

## 8. Client feedback (2026-10-29)

After reviewing phases 1–8, the client asked for the changes below. Each one is limited to scholarship records, and the normal flow stays unchanged (the mentor's Phase 8 constraint).

| # | Decision |
|---|---|
| P9-1 | **Link only.** `/scholarship` is removed from the sidebar. The company shares the URL with its clients. A signed-out visitor who signs in or registers lands back on the link. There is no secret token. |
| P9-2 | **Registration without documents.** The scholarship registration asks for no file at all: no general registration documents and none of the 10 `scholarship_*` files. The consents stay. This reverses **OQ11**. |
| P9-3 | **The documents are on the request.** Required: فاتورة الجامعة (`education_invoice`), السجل التراكمي (`grade_transcript`), صورة البطاقة الشخصية للطالب (`student_id_copy`), صورة جواز السفر للطالب (`student_passport_copy`). Optional: مرفقات أخرى, 0–n files attached to the request without a field. |
| P9-4 | **Read only after submitting.** Request documents can't be edited once the request is submitted. On the profile, step 5 shows them read only. This replaces the document editing of **P8-1/P8-2**. |
| P9-5 | **Single only.** The scholarship marital status is `Single`, enforced on the server. |
| P9-6 | **Account restriction.** A Supervisor can set `is_account_restricted` on a scholarship registration. The student keeps logging in and sees «تم تقييد حسابك لإنتهاء المنحة», and no new request is accepted. |
| P9-7 | **No cooldowns.** A scholarship student skips the 3-month (rejected) and 6-month (approved) waits for every request: scholarship requests through the link, and normal requests through "Create new request" on My Requests (widened 2026-10-29 after the client found the My Requests button blocked). The "a previous request is pending review" block stays. Students of the normal flow keep both waits. |
| P9-8 | **My Requests.** A new "Assistance type" column shows the sub-category; scholarship rows show «منحة الشيخ خالد بن ناصر». |
| P9-9 | **Not in the normal flow.** The Scholarship option stays out of the normal request form, and the server keeps refusing it. Both already hold since Phase 6; Phase 9 adds the regression checks. |
| P9-10 | **Update Required: both triggers.** The rules below apply after the desk button "Update Required" and after the daily automatic job, as for a normal beneficiary (agreed 2026-10-29). |
| P9-11 | **Update Required: the normal documents.** The student uploads the normal registration documents, worked out from their own answers by the normal rules. There is no scholarship-specific list. |
| P9-12 | **Update Required: only after an update.** First-time scholarship registration still has no documents (P9-2). They are required only once the registration has been through "Update Required" (`last_required_update_date` is set). |
| P9-13 | **Update Required: same place, server-enforced.** The student uploads in the profile's documents step. The save reaches "Updated beneficiary" only when every required document is present, and the server enforces this. |
| P9-14 | **Update Required: requests blocked.** As for a normal beneficiary, new requests (scholarship and normal) stay blocked until a Supervisor accepts the registration again. |
| P9-15 | **Update Required: request documents untouched.** The scholarship request documents are not deleted or cleared, and stay read only. This answers OQ16. |

**Old data.** `REQ3881`–`REQ3888` and their registrations keep the 10 documents on the registration. The fields are kept and shown read-only in the desk; nothing is deleted.

## 9. Phases

1. [Phase 1 — Tracer: end-to-end scholarship submit](phase-1-tracer.md)
2. [Phase 2 — Scholarship field variants](phase-2-field-variants.md)
3. [Phase 3 — Approval and rejection cascade](phase-3-approval-cascade.md)
4. [Phase 4 — Accepted users and desk polish](phase-4-accepted-users-desk.md)
5. [Phase 5 — Review edits](phase-5-review-edits.md)
6. [Phase 6 — Registration parity and attachments on the registration](phase-6-registration-parity.md)
7. [Phase 7 — What the applicant sees after submitting](phase-7-scholarship-views.md)
8. [Phase 8 — Editing a scholarship application, and request rejection](phase-8-profile-edit-and-rejection.md)
9. [Phase 9 — Scholarship requests without cooldowns](phase-9-no-cooldowns.md)
10. [Phase 10 — Reached only through the link](phase-10-link-only.md)
11. [Phase 11 — Documents on the request, Single only](phase-11-request-documents.md)
12. [Phase 12 — Account restriction](phase-12-account-restriction.md)
13. [Phase 13 — Assistance type on My Requests, and the browser QA](phase-13-my-requests-and-qa.md)
14. [Phase 14 — Registration documents after "Update Required"](phase-14-update-required-documents.md)

Progress: [progress.md](progress.md)
