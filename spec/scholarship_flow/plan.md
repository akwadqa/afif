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
- **One atomic submission.** The registration moves to `New Registration`, and a Beneficiary Request is created in `Pending Supervisor Approval`.
- **A flag on both documents** separates scholarship records from the normal flow.
- **Approval keeps both documents in sync.** The direction is open; see OQ2.

The normal registration flow and the normal aid request flow stay unchanged.

## 2. Decisions

| # | Decision |
|---|---|
| D1 | Add a read-only Check `is_scholarship` to `Beneficiaries Registration` and to `Beneficiary Request`. It shows in the list view and as a standard filter. It can only be set on insert; `validate` throws if it changes afterwards. |
| D2 | The request is a normal `Beneficiary Request` with a new `request_category` option, `Scholarship`, plus 8 new Attach fields. There is no new DocType. |
| D3 | Wizard steps: 1 البيانات الشخصية · 2 تفاصيل الدخل · 3 الالتزامات المالية · 4 بيانات إضافية, followed by the **same registration attachments sub-step** as the normal flow · 5 بيانات الطلب. |
| D4 | Step 5 has 8 required attachments: guardian/applicant ID, guardian/applicant passport, student ID, student passport, IDs of all family members, university invoice, student transcript, and the guardian's bank statement. This list replaces the older attachment list in Figma. |
| D5 | Drafts are saved step by step, exactly as today. A single whitelisted endpoint, `submit_scholarship_application`, then validates **all** registration attachments and consents and **all** request attachments. In one transaction it submits the registration and creates the request. If anything is missing, nothing is submitted. |
| D6 | The existing DB Workflows stay as they are. The cascade logic lives in server hooks. Moving to status-only workflows is out of scope. |
| D7 | Eligibility: the scholarship wizard is open to users with no registration, or with their own scholarship Draft. Users who are already Accepted use the normal request page with the `Scholarship` category (Phase 4). |
| D8 | Where a field means the same thing, reuse it with a scholarship label. Where the meaning differs, add a new field (§3). |
| D9 | Rejecting a scholarship request also sets the registration to `Not Accepted`. |
| D10 | Frontend: add a sidebar item "منحة الشيخ خالد بن ناصر" at route `/scholarship`. `BeneficiaryRegistration.vue` is reused with `flow="scholarship"`, and each card reads a variant config. The public nav link `khaledGrant` (terms page) stays unchanged. |

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

### Beneficiary Request (new fields)

| Field | Type | Notes |
|---|---|---|
| `is_scholarship` | Check, read only | in list view and standard filter |
| `request_category` | add option `Scholarship` | |
| `scholarship_guardian_id` | Attach | صورة البطاقة الشخصية لولي الأمر أو مقدم الطلب |
| `scholarship_guardian_passport` | Attach | صورة جواز السفر لولي الأمر أو مقدم الطلب |
| `scholarship_student_id` | Attach | صورة البطاقة الشخصية للطالب |
| `scholarship_student_passport` | Attach | صورة جواز السفر للطالب |
| `scholarship_family_ids` | Attach | صور البطاقات الشخصية لجميع أفراد العائلة |
| `scholarship_university_invoice` | Attach | فاتورة الجامعة |
| `scholarship_student_transcript` | Attach | السجل التراكمي للطالب |
| `scholarship_guardian_bank_statement` | Attach | كشف الحساب لولي الأمر |
| `is_scholarship_declaration_accepted` | Check | request declaration in step 5 (see OQ8) |

All Attach fields use `depends_on: eval:doc.request_category=="Scholarship"`. They are required for that category, and the server enforces this.

### Field mapping in scholarship mode

| Existing field(s) | Scholarship behaviour |
|---|---|
| `ben_income` | reused. Labels: آلية صرف راتب ولي الأمر / راتب ولي الأمر / ملاحظات |
| `private_income` | reused. Label: هل يوجد دخل للأسرة من عمل خاص أو تجارة منزلية؟ |
| `stock_income` | reused unchanged |
| `family_income`, `family_extra`, `children_income`, `rent_income` | hidden (replaced by `father_income` / `mother_income`) |
| `family_obligation` | relabelled: هل لدى الأسرة التزامات مالية؟ |
| `rent_obligation` | relabelled: هل لدى الأسرة التزامات دفع إيجار شهرية؟ |
| `treatment_obligation` | relabelled: هل لدى الأسرة التزامات دفع مصاريف علاج شهرية مستمرة؟ |
| `debt_obligation` | relabelled: هل لدى الأسرة ديون بنكية أو شخصية؟ |
| `tuition_obligation` | relabelled: هل لدى الأسرة التزامات بمصاريف مدرسية وجامعية؟ |
| `passport_number`, `id_expiry_date`, `partners_phone_number`, `ben_sec_*`, `worked_before`, `family_visa_type`, `visa_dependent`, `have_children` (+ children sub-fields), `afif_charity_assistance` (+ `affif_assistance`) | hidden and not required |

In the Sanadi integration, `father_income` and `mother_income` map to income type 5 (family) in `get_beneficiary_income_set`.

## 4. Affected areas

- **Backend:**
  - `beneficiaries_registration.json` and `beneficiary_request.json`
  - `afif/hooks_call.py`: `before_insert_request`, `get_beneficiary_income_set`, and the request transition hooks in Phase 3
  - new `afif/api/scholarship.py`
- **Desk:** `beneficiary_request.js`, where the `check_beneficiary_id` guard is skipped for scholarship in Phase 3.
- **Frontend (`frontend/src`):**
  - `router.js`
  - `components/sidebar/AppSidebar.vue`, `navbar/MobileMenu.vue` and `navbar/NavLinks.vue`
  - new `pages/Scholarship.vue`
  - `components/registration/BeneficiaryRegistration.vue` and its cards
  - new `ScholarshipRequestCard.vue`
  - `components/request/BeneficiaryRequest.vue` (Phase 4)
  - `locales/translations.js`
- **Sanadi:** the beneficiary payload (new income types) and the subvention request lookup (OQ6).

## 5. Go-live prerequisites

- `bench migrate` (new fields), `bench clear-cache`, `bench restart`, and a frontend build.
- The Sanadi lookup id for Scholarship (OQ6) must be known before a scholarship request can reach Specialist approval.

## 6. Open questions (for the mentor)

| # | Question | Blocks |
|---|---|---|
| OQ1 | Should step 5 also ask for `requested_amount` and `request_summary`? | Phase 1 (default until answered: not shown) |
| OQ2 | Which approval comes first? The task text says the Supervisor approves the **request** and the registration is approved with it. The alternative is that the Supervisor approves the **registration** and the request is approved automatically. | Phase 3 |
| OQ3 | Does the request that follows stop at `Pending Specialist Approval`, which is its normal next state, or skip ahead? The request's Approve transition needs `declaration` and a Sanadi `ben_id`. Who uploads the declaration for a scholarship request? | Phase 3 |
| OQ4 | Should direct approve/reject be blocked on the document that is **not** the control point? | Phase 3 |
| OQ5 | Do the pending, 3-month and 6-month cooldowns in `before_insert_request` apply to Scholarship requests? | Phase 4 |
| OQ6 | What is the Sanadi lookup id for the Scholarship category in `get_aid_lookup_parent_id`? | Phase 3 |
| OQ7 | Are the father and mother incomes right as new fields, rather than relabelling `family_income` / `family_extra`? | Phase 2 |
| OQ8 | In Figma, the step-5 declarations repeat the registration consents. The third one also says "this is not an aid request". Should step 5 show one request-level declaration (the default), or something else? | Phase 1 |

## 7. Phases

1. [Phase 1 — Tracer: end-to-end scholarship submit](phase-1-tracer.md)
2. [Phase 2 — Scholarship field variants](phase-2-field-variants.md)
3. [Phase 3 — Approval and rejection cascade](phase-3-approval-cascade.md)
4. [Phase 4 — Accepted users and desk polish](phase-4-accepted-users-desk.md)

Progress: [progress.md](progress.md)
