# Scholarship Flow (منحة الشيخ خالد بن ناصر) — Plan

**Branch:** `feature/scholarship-flow`
**Design:** Figma `Afif-Charity`, node `723:1544` (step 5 "بيانات الطلب")

## 1. Requirement

Today a beneficiary must:

1. Register through the 5-step wizard.
2. Wait for a Supervisor to accept the registration.
3. Submit an aid request.

The scholarship is one combined flow:

- **One wizard.** It uses the registration steps, with scholarship-specific field changes, plus a new step **بيانات الطلب** (request data).
- **One atomic submission.** The registration moves to `New Registration`, and a Beneficiary Request (Education Assistance → Scholarship) is created in `Pending Supervisor Approval`.
- **A flag on both documents** separates scholarship records from the normal flow.
- **When the Supervisor approves the request, the related registration is approved in the same action.**

The normal registration flow and the normal aid request flow stay unchanged.

## 2. Decisions

| # | Decision |
|---|---|
| D1 | Add a read-only Check `is_scholarship` to `Beneficiaries Registration` and to `Beneficiary Request`. It shows in the list view and as a standard filter. It can only be set on insert; `validate` throws if it changes afterwards. On the request it means "created through the scholarship flow", and that is what triggers the approval cascade (D11). |
| D2 | A scholarship is a **subcategory of Education Assistance**: `request_category = "Education Assistance"` and `educational_assistance = "Scholarship"`. There is no new category and no new DocType. The `Categories` tree already has `Education Assistance`, so it is not touched. |
| D3 | Wizard steps: 1 البيانات الشخصية · 2 تفاصيل الدخل · 3 الالتزامات المالية · 4 بيانات إضافية, followed by the **same registration attachments sub-step** as the normal flow · 5 بيانات الطلب. |
| D4 | Step 5 belongs entirely to the **request**: the requested amount, 8 required attachments and the request declarations. All of it is stored on the Beneficiary Request, not on the registration. Two of the 8 attachments reuse existing Education fields (§3); this attachment list replaces the older one in Figma. |
| D5 | Drafts are saved step by step, exactly as today. A single whitelisted endpoint, `submit_scholarship_application`, validates **all** registration attachments and consents **and** all step-5 data. In one transaction it submits the registration and creates the request. If anything is missing, nothing is submitted. |
| D6 | The existing DB Workflows stay as they are. The cascade logic lives in server hooks. Moving to status-only workflows is out of scope. |
| D7 | Eligibility: the scholarship wizard is open to users with no registration, or with their own scholarship Draft. Users who are already Accepted pick Education Assistance → Scholarship on the normal request page (Phase 4). |
| D8 | Where a field means the same thing, reuse it with a scholarship label. Where the meaning differs, add a new field (§3). The father and mother incomes are **new fields**. |
| D9 | When the Supervisor rejects a scholarship request, the registration is also set to `Not Accepted`. |
| D10 | Frontend: add a sidebar item "منحة الشيخ خالد بن ناصر" at route `/scholarship`. `BeneficiaryRegistration.vue` is reused with `flow="scholarship"`, and each card reads a variant config. The public nav link `khaledGrant` (terms page) stays unchanged. |
| D11 | **The request is the control point.** When the Supervisor approves a scholarship request, the linked registration is accepted in the same action. The registration is accepted first, so Sanadi creates the beneficiary and sets `ben_id` before the request's Sanadi hooks run. |

## 3. Data model

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
| `is_data_accuracy_declared` | new Check | اقر أنا مقدم الطلب بأن كافة الوثائق والبيانات المقدمة في هذا الطلب صحيحة. |
| `is_eligibility_check_accepted` | new Check | يحق لمؤسسة عفيف التأكد من أهلية مقدم الطلب بحسب اجراءاتها المتبعة. |

- **Visibility.** The new Attach fields use `depends_on: eval:doc.request_category=="Education Assistance" && doc.educational_assistance=="Scholarship"`. For that subcategory, all 8 attachments, the amount and both declarations are required, and the server enforces it.
- **Third Figma declaration dropped.** It says "this is only a registration, not an aid request", which is a registration consent and is already covered by the registration attachments sub-step.

### Where the Scholarship subcategory must be added

There is no single source for subcategories; each place below holds its own copy:

| Place | What to add |
|---|---|
| `beneficiary_request.json` → `educational_assistance` (Select) | option `Scholarship` |
| `beneficiary_aid.json` → `educational_assistance` (Select, its own copy) | option `Scholarship`. The committee fills this in by hand on the Aid: the "Aid Button" Client Script copies only `request_category`, `beneficiaries`, `beneficiary_request` and `suggested_amount`. |
| `frontend/src/components/request/BeneficiaryRequest.vue` → `SUBCATEGORY_MAP['Education Assistance'].options` and `requiredDocs` | `Scholarship`, plus the 6 extra docs when it is selected |
| `locales/translations.js` | `request.subtypes.education.Scholarship` (AR منحة دراسية / EN Scholarship) |
| `hooks_call.py` → `get_aid_lookup_parent_id`, Education branch | `educational_assistance == "Scholarship"` → parent `10010` (Education), with the Sanadi `aidLookupId` from OQ6 |

### Field mapping in scholarship mode

| Existing field(s) | Scholarship behaviour |
|---|---|
| `ben_income` | reused. Labels: آلية صرف راتب ولي الأمر / راتب ولي الأمر / ملاحظات |
| `private_income` | reused. Label: هل يوجد دخل للأسرة من عمل خاص أو تجارة منزلية؟ |
| `stock_income` | reused unchanged |
| `family_income`, `family_extra`, `children_income`, `rent_income` | hidden (replaced by the new `father_income` / `mother_income`) |
| `family_obligation` | relabelled: هل لدى الأسرة التزامات مالية؟ |
| `rent_obligation` | relabelled: هل لدى الأسرة التزامات دفع إيجار شهرية؟ |
| `treatment_obligation` | relabelled: هل لدى الأسرة التزامات دفع مصاريف علاج شهرية مستمرة؟ |
| `debt_obligation` | relabelled: هل لدى الأسرة ديون بنكية أو شخصية؟ |
| `tuition_obligation` | relabelled: هل لدى الأسرة التزامات بمصاريف مدرسية وجامعية؟ |
| `passport_number`, `id_expiry_date`, `partners_phone_number`, `ben_sec_*`, `worked_before`, `family_visa_type`, `visa_dependent`, `have_children` (+ children sub-fields), `afif_charity_assistance` (+ `affif_assistance`) | hidden and not required |

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
- **Status for Scholarship.** The parent is settled (`10010`, Education). The `aidLookupId` is still open (OQ6): either Sanadi's dedicated Scholarship code, or a mapping to an existing one such as `1001010` Tuition Fees.
- **An unmapped subcategory currently crashes** with `UnboundLocalError`. Phase 3 makes it fail with a clear `frappe.throw`.

## 5. Affected areas

- **Backend:**
  - `beneficiaries_registration.json`, `beneficiary_request.json` and `beneficiary_aid.json` (the `Scholarship` option only)
  - `afif/hooks_call.py`: `before_insert_request`, `get_beneficiary_income_set`, `get_aid_lookup_parent_id`, and the request transition hooks in Phase 3
  - new `afif/api/scholarship.py`
- **Desk:** `beneficiary_request.js`, where the `check_beneficiary_id` guard is skipped for scholarship in Phase 3.
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
- The Sanadi `aidLookupId` for Scholarship (OQ6) must be known before a scholarship request can be approved by the Supervisor.

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

### Still open

| # | Question | Blocks |
|---|---|---|
| OQ1b | Does step 5 also need `request_summary`? Sanadi receives it as `requestSummary`. The default is to show it as optional. | Phase 1 |
| OQ3 | Partly answered: after the Supervisor approves, the request follows the normal flow, with the office (beneficiary visit, declaration upload, Specialist approval) and not us. Still to confirm: today the Supervisor's Approve **requires** `declaration` (transition condition `doc.declaration`), and that same transition sends the declaration to Sanadi (`new_subvention_request`). Does the scholarship keep that order (visit and declaration before Supervisor approval), or must the Supervisor approve before the declaration exists? The second needs a workflow and Sanadi change. | Phase 3 |
| OQ5 | Do the pending, 3-month and 6-month cooldowns in `before_insert_request` apply to Scholarship requests from users who are already accepted? The default is that they apply, like every other subcategory. | Phase 4 |
| OQ6 | What is the Sanadi `aidLookupId` for the Scholarship subcategory under Education (`10010`)? Is it a dedicated Sanadi code, or should it map to an existing one such as `1001010` Tuition Fees or `1001050` Other? It is used for both the request (step 2) and the Aid (step 6). | Phase 3 |

## 8. Phases

1. [Phase 1 — Tracer: end-to-end scholarship submit](phase-1-tracer.md)
2. [Phase 2 — Scholarship field variants](phase-2-field-variants.md)
3. [Phase 3 — Approval and rejection cascade](phase-3-approval-cascade.md)
4. [Phase 4 — Accepted users and desk polish](phase-4-accepted-users-desk.md)

Progress: [progress.md](progress.md)
