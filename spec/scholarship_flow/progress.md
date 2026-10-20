# Scholarship Flow — Progress

| Phase | Status | Commits |
|---|---|---|
| [1 — Tracer: end-to-end submit](phase-1-tracer.md) | done (live site still needs `bench restart`) | `41fc2c0`, `e77431a`, `5448fe2`, `d8c9642` |
| [2 — Field variants](phase-2-field-variants.md) | done (live site still needs `bench restart`) | `90c863d`, `ae1203b`, `e2e4436`, `919ada1`, `67b95e6`, `0cfa57f` |
| [3 — Approval/rejection cascade](phase-3-approval-cascade.md) | done (live site still needs `bench restart`) | `b99fcd8`, `3fadd55`, `4468f6b`, `bfc8ae6` |
| [4 — Accepted users + desk polish](phase-4-accepted-users-desk.md) | done (live site still needs `bench restart` for the endpoint) | `6587698`, `ae1e5f2`, `efcf2cd`, `e8aba43`, `7cffa9d`, `4960c0c` |
| [5 — Review edits](phase-5-review-edits.md) | done (live site still needs `bench restart`) | `d1346a5`, `b85fcb8`, `f9c654a`, `3f6a815`, `b2c673a`, `034f705` |
| [6 — Registration parity](phase-6-registration-parity.md) | done (live site still needs `bench restart`) | `c832071`, `69ba9dc`, `1297605`, `163509b`, `f1f71b3`, `a1f4225` |
| [7 — What the applicant sees](phase-7-scholarship-views.md) | done (live site still needs `bench restart`) | `3dac039`, `aa6762a`, `7570946`, `e748836`, `124a858`, `83b91f7` |
| [8 — Profile edit and request rejection](phase-8-profile-edit-and-rejection.md) | done (live site still needs `bench restart`) | `09557c1`, `2d41dc7`, `9b4a572` |

## Phase 8 — log (2026-10-20)

Mentor constraint: the normal flow must not change. Decisions P8-1 to P8-5 are in the [phase plan](phase-8-profile-edit-and-rejection.md).

### What was built
- **Rejection only rejects the request (P8-3, replaces D9).** `accept_scholarship_registration_with_request` runs on approval only. A rejected scholarship request leaves the registration as it is (New Registration), with no note, and the Supervisor then decides the registration through its own workflow. Approval still accepts the registration first (D11).
- **Profile edit (P8-1, P8-2).**
  - `BeneficiaryRegistration` has `hasRequestStep` (the scholarship wizard, or any scholarship registration) and `isSubmittedApplication`.
  - A submitted scholarship registration loads its latest scholarship request itself (this replaces the Phase 7 prop) and shows it on step 5. The amount, summary and declarations are locked (`requestReadOnly`); the 10 documents can be replaced while editing.
  - The attachments step saves and moves on to step 5. The workflow action (Review) is applied there.
  - A submitted request's fields are not re-validated; the documents are.
- **Normal flow:** every new condition is false for a registration with `is_scholarship = 0`, so its steps, saves, workflow actions and server rules are the same as before.

### Tests
- **Backend:** `test_scholarship` 20 OK, `test_scholarship_accepted` 14 OK, `test_scholarship_decision` **14 OK**, `test_beneficiaries_registration` 4 OK.
  - New: the rejection leaves the registration in New Registration, and the Supervisor can then approve it directly; rejecting a normal request does not touch the registration (regression).
  - The old cascade code fails the 2 changed tests.
- **Frontend:** `vitest run` **40 OK**. New: a submitted request's step checks only the documents.

### Browser run (agent-browser, temporary `bench serve` on :8010, stopped afterwards)
| Check | Result |
|---|---|
| Profile, `scholarship.demo.phase8.rejected` (`SA-6631-2026` Not Accepted, `REQ3893` Rejected by Supervisor) | 5 steps with بيانات الطلب; Edit; steps 1–4 save with no popup; step 5 shows حالة الطلب: مرفوض, 19000 locked, declarations disabled |
| Replace the family IDs on step 5, submit | new private file on the registration field; success view; `SA-6631-2026` Updated; `REQ3893` unchanged |
| Profile, `scholarship.demo.phase8.normal` (`SA-6632-2026`, normal, Not Accepted) | 4 steps, as before; submit on the attachments step; success view; Updated |

- **Status timing.** The scholarship registration became Updated when the attachments step saved, not on step 5. That is the existing `updated_status` hook (Not Accepted + complete + `current_step >= 5`), which does the same in the normal flow. It was left as is; the spec says so.
- **Seed artefact.** The demo record was copied from `SA-6628-2026` and its fields still point at that record's files, while Frappe made its own copies at insert. Replacing a document therefore left the copied File in place. The cleanup only deletes a File attached to the same registration with the old URL, and correctly did not touch `SA-6628-2026`'s file. Real uploads always match.

### The yearly "Update Required" (mentor question, answered here; OQ16 stays open)
`beneficiary_update_required_status` runs daily on **Accepted** registrations only. It looks at the latest request created since the last "Update Required":
- **With such a request** (and no pending update): "Update Required" only when that request was rejected 3+ months ago or approved for aid 6+ months ago, and the registration was accepted more than 10 days ago. An open request, or an approved one not yet for aid, never triggers it.
- **Without one:** "Update Required" once the registration was accepted 10+ days ago.
- **The desk button "Update Required"** does the same reset at any time, whatever the requests.
- **When it applies:** the attachment fields are cleared (raw SQL), and the status becomes Update Required; the beneficiary re-uploads in the profile, and the next complete save moves it to Updated beneficiary.

### Demo data added on the dev site (on purpose)
Password: `Scholarship@2026`.

| User | State |
|---|---|
| `scholarship.demo.phase8.rejected@example.com` | `SA-6631-2026` (scholarship), Updated after the browser edit; `REQ3893` Rejected by Supervisor |
| `scholarship.demo.phase8.normal@example.com` | `SA-6632-2026` (normal), Updated after the browser edit |

## Phase 7 — log (2026-10-20)

Review after trying Phase 6: after submitting, `/scholarship` only said "submitted" and `/request` showed no request. After approval, `/scholarship` showed an empty request form. The partner phone must be optional for Single. Decisions P7-1 to P7-5 are in the [phase plan](phase-7-scholarship-views.md).

### What was built
- **`/scholarship` only for scholarship registrations (P7-1).**
  - A normal-flow beneficiary is blocked there, accepted or not. This replaces P6-7.
  - `create_scholarship_request` refuses a caller whose registration is not a scholarship one (`PermissionError`).
- **Full application, read only (P7-2).**
  - A submitted scholarship applicant sees the wizard read only: steps 1–4, then step 5 with the latest scholarship request (amount, summary, declarations, the 10 documents) and a "حالة الطلب" badge.
  - Read-only navigation now reaches step 5. The Edit button is hidden in the scholarship flow; edits go through the profile page.
- **New scholarship request (P7-3).**
  - "تقديم طلب منحة جديد" appears when `getRequestBlockReason` allows it (Accepted, last request closed, cooldowns passed), and opens `ScholarshipApplyForm`.
  - The rules moved from `Request.vue` to `components/request/requestEligibility.js`, shared by both pages.
- **`/request` before acceptance (P7-4).**
  - The page lists the user's requests with "create new" disabled ("يمكنك تقديم طلبات جديدة بعد قبول ملف المستفيد الخاص بك"). It is blocked only when there are none.
  - The patch `allow_applicants_to_read_their_requests` gives `Beneficiary New Registration` and `Beneficiary Not Accepted` read + if_owner on Beneficiary Request.
- **Partner phone (P7-5).** Optional for Single in the wizard (asterisk and validation) and in the desk (`mandatory_depends_on`). Its 8-digit format is still checked when given.

### Tests
- **Backend:** `test_scholarship` **20 OK**, `test_scholarship_accepted` **14 OK**, `test_scholarship_decision` **13 OK**, `test_beneficiaries_registration` **4 OK**.
  - New: an applicant reads their own request but not someone else's; a normal accepted beneficiary is refused by `create_scholarship_request`.
  - The accepted-path tests now use accepted scholarship registrations.
- **Mutation check.** Dropping the scholarship-only check fails 1 test. Requiring the partner phone for Single again fails 1.
- **Frontend:** `vitest run` **39 OK**.
  - New: `requestEligibility.test.js` (9) covers not accepted, pending and the cooldowns.
  - The partner phone is optional for Single only, and its format is still checked.
  - New keys exist.
- **Lint and build.** Biome is clean on the changed JS files. `migrate` (with the patch) and `yarn build` are done.

### Browser run (agent-browser, temporary `bench serve` on :8010, stopped afterwards)
| Check | Result |
|---|---|
| `/scholarship` as `scholarship.demo.phase6.draft` (`SA-6628-2026` New Registration, `REQ3890` pending) | read-only application; step 5 shows حالة الطلب: تحت الإجراء, 22000, the summary, the 10 documents and both declarations ticked; no Edit, no new-request button |
| `/request`, same user | `REQ3890` listed (مساعدات تعليمية, تحت الإجراء), create disabled with the "after acceptance" message; opening it shows Education / منحة دراسية |
| Approval simulated (registration Accepted, request Pending Specialist Approval) | `/scholarship` still shows the data, not an empty form; no new-request button |
| Request closed (Approved) | `/scholarship` shows "تقديم طلب منحة جديد", which opens the request step; `/request` create is enabled too |
| `/scholarship` as `scholarship.demo.phase6.requestpage` (normal, Accepted) | blocked: "لا يمكن التقديم على المنحة من هنا" |

### Demo data changed on the dev site (on purpose)
- **Approval simulated in the database**, not through the desk, because a real approval would call Sanadi staging. `SA-6628-2026` is Accepted (`ben_id = demo-p7-approved`), and its user now has the `Beneficiary Accepted` profile.
- **`REQ3890` is `Approved`**, so that user can try a new scholarship request.

### Deviations from the phase plan
- The new-request button sits in the wizard header, through a new `actions` slot on `BeneficiaryRegistration`.
- The blocked view's "submitted" variant and its two keys are removed, because a scholarship applicant now always gets the application view. The blocked message is back to the Phase 1 wording.

## Phase 6 — log (2026-10-20)

Mentor review: the scholarship registration has the same fields as the normal one, and the scholarship documents live on the registration. Decisions P6-1 to P6-13 are in the [phase plan](phase-6-registration-parity.md).

### What was built
- **Same fields as the normal registration.**
  - The scholarship variant hides nothing. The income and obligations steps and the bank-loans question are the normal ones.
  - The father/mother incomes are removed: the fields, the Sanadi type-5 mapping and the wizard.
  - The 18 desk `!doc.is_scholarship` guards are dropped.
  - Only `guardian_mobile_number` and `Single` remain scholarship-only.
- **Documents on the registration.**
  - New tab "Scholarship Attachments" on Beneficiaries Registration (10 Attach fields, `depends_on: is_scholarship`).
  - The 8 `scholarship_*` fields are removed from Beneficiary Request. `education_invoice` / `grade_transcript` no longer show or are required for Scholarship in the desk.
  - The request keeps the amount, the summary and the 2 declarations.
- **New applicant (Draft).**
  - Each step-5 document is uploaded when picked (native `upload_file`, private, attached by field) and saved on the Draft.
  - `submit_scholarship_application` now takes only the request data. It requires the 10 documents on the registration.
- **Accepted beneficiary.**
  - `/scholarship` shows step 5 only (`ScholarshipApplyForm.vue`).
  - `create_scholarship_request` uploads nothing itself. It checks that the files are the caller's own and unattached, then inserts the request with normal permissions (cooldowns apply). It then writes the URLs onto the registration with `db_set` and attaches the File records, all in one transaction.
  - Saving an Accepted registration would re-run `create_new_beneficiary` (a new Sanadi call and a reset acceptance date), which is why the registration is not saved.
- **Scholarship only through `/scholarship`.**
  - The request page no longer offers it for a new request; it still shows an existing one with its declarations.
  - The server enforces "Scholarship subcategory ⇔ `is_scholarship`" (`ScholarshipSubcategoryError`), and only the endpoints set the flag.
  - `before_insert_request` skips its rules only for the new applicant (`flags.is_new_scholarship_applicant`).
- **Replaced or cleared attachments.** `BeneficiariesRegistration.on_update` deletes the File of that field and URL. A File with the same URL on another field (Frappe's dedup) is kept, and so is its disk copy.
- **Unchanged:** Sanadi lookup `1001050` and the approval cascade.

### Tests
- **Backend:** `test_scholarship` **19 OK**, `test_scholarship_accepted` **13 OK**, `test_scholarship_decision` **13 OK**, `beneficiaries_registration.test_beneficiaries_registration` **4 OK** (new).
  - New cases: a missing scholarship document on the registration; the accepted path writing private files to the registration; inserting Scholarship without the endpoint (with and without the flag); switching a request to or from Scholarship; the attachment cleanup (replace, clear, shared URL, no change).
  - The guard test: an accepted scholarship registration with a new pending scholarship request can still be rejected by the Supervisor.
- **Mutation check.** Each of these fails the suite:
  - Undoing the guard narrowing.
  - Dropping the subcategory check (4 tests).
  - Dropping the cleanup (3).
  - Dropping the `attached_to_field` filter in the cleanup (1).
- **Frontend:** `vitest run` **25 OK**.
  - Every normal field is required in both flows, and the guardian mobile only in the scholarship flow.
  - The normal incomes and bank-loans label appear in both flows; father/mother are gone.
  - Step 5 reads the documents from the registration files.
  - Scholarship requests list no request documents.
  - The AR/EN keys exist.
  - Mutations caught: hiding a field again (1), reading the step-5 files from the old place (3).
- **Lint and build.** Biome is clean on the changed JS files. It crashes on `.vue` files, as before. `migrate` and `yarn build` are done.

### Browser run (agent-browser, temporary `bench serve` on :8010, stopped afterwards)
| Check | Result |
|---|---|
| `scholarship.demo.phase6.draft` (`SA-6628-2026`, copied from the Phase 2 Draft), step 1 empty Next | popup lists the normal fields Phases 2–5 hid: ID expiry, passport number, partner phone, secondary nationality, family visa, children, Afif assistance |
| Steps 2 / 3 / 4 | 7 normal incomes; normal obligation labels; "هل لديك قروض بنكية ومديونيات؟" |
| Step 5 uploads | each file saved on the Draft at once, private, attached by field |
| Replace the transcript, delete the student ID | old File records and disk files gone; the cleared field is empty |
| Submit | `SA-6628-2026` New Registration with 10 private scholarship files; `REQ3890` Education / Scholarship, `is_scholarship=1`, Pending Supervisor Approval, 22000 |
| `/scholarship` again as the same user | "تم تقديم طلب المنحة", status تسجيل جديد |
| `scholarship.demo.phase6.accepted` (`SA-6629-2026`, Accepted) on `/scholarship` | step 5 only; empty submit lists 14 items; nothing uploaded before submit |
| Submit | `REQ3891` Scholarship, `is_scholarship=1`, pending; the 10 private files on `SA-6629-2026`; registration still Accepted with its `ben_id`; success message "يمكنك متابعة حالته من صفحة طلباتي" |
| `/request` as the accepted user, open `REQ3891` | read-only: مساعدات تعليمية / منحة دراسية, both declarations ticked and disabled |
| `/request` as `scholarship.demo.phase6.requestpage` (`SA-6630-2026`), new request | Education options stop at Other Educational Assistance; no Scholarship |
| Desk as `scholarship.demo.supervisor` | "Scholarship Attachments" tab with the documents on `SA-6628-2026`; hidden on the normal `SA-6630-2026` |

### Demo data added on the dev site (on purpose)
Password: `Scholarship@2026`.

| User | State |
|---|---|
| `scholarship.demo.phase6.draft@example.com` | submitted through the browser: `SA-6628-2026` + `REQ3890` |
| `scholarship.demo.phase6.accepted@example.com` | `SA-6629-2026` Accepted (`ben_id = demo-p6-accepted`), applied through the browser: `REQ3891` |
| `scholarship.demo.phase6.requestpage@example.com` | `SA-6630-2026` Accepted (`ben_id = demo-p6-requestpage`), no requests |

Older scholarship requests (`REQ3881`–`REQ3889`) had their documents on the request; those columns are no longer DocFields, so the documents are not shown (P6-12). `REQ3888` (Phase 4) is Scholarship with `is_scholarship=0`, so saving it now fails the subcategory rule. That's fine for demo data.

### Deviations from the phase plan
- **No Vitest for the request page's subcategory list.** The filter lives in the component, and the app has no `@vue/test-utils`. It was checked in the browser instead.
- **The guard narrowing matters only for scholarship registrations.** A normal registration never hits it. The test uses an applicant accepted through an earlier scholarship who applies again.
- **The field variant follows the record.** A scholarship registration opened from `/beneficiary-profile` keeps the guardian mobile and `Single`. Before this, editing it there dropped `guardian_mobile_number` (the normal flow stripped it from the payload). This affected the OQ13 resubmit path.
- **The scholarship document fields are always in the wizard payload**, normal flow included. Without them, editing a scholarship registration from the profile page would clear them, and the cleanup would then delete the files.
- **The success view** has a separate message for accepted beneficiaries, and the blocked view now says they can apply once accepted.
- **`utils/fileUpload.js`** holds the native upload for the wizard and the accepted form. The request page keeps its own copy (unchanged).

### Found, not fixed (outside this phase)
- **The wizard clears every field it doesn't send.** `frappe.client.save` rebuilds the document from the payload, and the wizard never sends `ben_id`, `registration_acceptance_date` and other desk-only fields. 4 of the 5 "Updated beneficiary" registrations (re-saved through the wizard after "Update Required") have no `ben_id`. A fix would load the doc and update only the wizard fields (for example a whitelisted save, or `frappe.client.set_value`). This needs its own fix branch and a check of the affected records.

## Phase 5 — log (2026-10-19)

Review edits to the scholarship wizard. Answers on the ambiguous points: Single is for the scholarship flow only, the two new statements are required, and years of residence is an open question (OQ14, no change).

### What was built
- **Marital status `Single` (أعزب / عزباء).** New option on `marital_status`. The scholarship wizard offers it first (variant `maritalStatuses`); the normal wizard keeps its 4 options. `validate` refuses *setting* Single on a normal registration (`SingleMaritalStatusError`); the 3 older normal registrations that already hold Single (`SA-5652-2024`, `SA-6606-2026`, `SA-6607-2026`) can still be saved. Sanadi already maps Single → 1.
- **Income, first option.** The scholarship wizard asks "هل لديك (دخل/راتب)؟" on `ben_income`, with the beneficiary wording for its sub-fields (آلية صرف دخل المستفيد / راتب المستفيد / ملاحظة دخل المستفيد). The guardian wording from Phase 2 and its 4 translation keys are gone.
- **Bank debts.** In the scholarship wizard `bank_loans` reads "هل لديك أو لدى رب الأسرة التزامات بنكية ومديونيات؟", in the card and in the validation popup (variant `labelKeys.bankLoans`).
- **Two more required documents.** `scholarship_mother_bank_statement` (كشف حساب الأم) and `scholarship_student_bank_statement` (كشف حساب الطالب) on Beneficiary Request, in `SCHOLARSHIP_ATTACHMENT_FIELDS` on both sides. Both entry points (step 5 and the request page's Scholarship option) now require 10 documents.
- **Years of residence:** unchanged (OQ14).

### Tests
- **Backend:** `test_scholarship` **22 OK** (3 new for Single: scholarship accepted and sent as 1, normal refused, older Single still saves; 2 new incomplete cases for the statements); `test_scholarship_accepted` **12 OK** (new statement case added); `test_scholarship_decision` **13 OK**.
- **Mutation check.** Always refusing Single fails the older-record test; never refusing it fails the normal-registration test.
- **Frontend:** `yarn test:run` **27 OK** (5 new: Single per flow, a single applicant needs no partner data, bank-debts label per flow, the 2 statements are required, the income label and sub-labels; the translation check now also covers the label keys, marital options and attachments). Biome lint clean. `migrate` and `yarn build` done.

### Browser run (agent-browser, temporary `bench serve` on :8010, stopped afterwards)
`scholarship.demo.phase5.draft@example.com` (Draft `SA-6627-2026`, copied from `SA-6619-2026`):
- Step 1: marital options أعزب / متزوج / مطلق / أرمل / منفصل; Single chosen. The copied Draft predates OQ12, so the wizard asked for the passport number and secondary nationality, which were filled in.
- Step 2: first question هل لديك (دخل/راتب)؟, sub-fields with the beneficiary wording, then father, mother, private business, stock market.
- Step 4: هل لديك أو لدى رب الأسرة التزامات بنكية ومديونيات؟
- Step 5: 10 documents, the last two كشف حساب الأم and كشف حساب الطالب. Submitted → success view.
- Result: `SA-6627-2026` New Registration, `marital_status = Single`; `REQ3889` Education / Scholarship, `is_scholarship=1`, Pending Supervisor Approval, 21000, both new statements set, 10 private files attached.
- Normal wizard (`scholarship.demo.new@example.com`): no Single option.
- Ticking both declarations from one script call lost the first one (the known "two updates in the same tick" note below); single clicks work.

### Demo data added on the dev site (on purpose)
Password: `Scholarship@2026`.

| User | State |
|---|---|
| `scholarship.demo.phase5.draft@example.com` | submitted through the browser: `SA-6627-2026` (Single) + `REQ3889` (10 documents) |

Older scholarship requests (`REQ3881`–`REQ3888`) were created with 8 documents. The new rule applies when a request is saved, so editing one of them in the desk now asks for the 2 statements.

## Phase 4 — log (2026-10-19)

### What was built
- **Endpoint** `afif.api.scholarship.create_scholarship_request(request)` for accepted beneficiaries. It builds the Education / Scholarship request (`is_scholarship=0`), checks completeness, checks that every file is the caller's own and unattached, inserts with **normal permissions** (so `before_insert_request` applies the accepted-only, pending-request and cooldown rules, OQ5), and attaches the files, in one transaction. The request builder is shared with `submit_scholarship_application`.
- **Request page** (`BeneficiaryRequest.vue`).
  - `Scholarship` is offered under Education Assistance. It requires the 8 scholarship documents (step-5 labels) and the 2 declarations; the read-only view shows them.
  - For Scholarship only, the files are uploaded first (private, unattached) and the new endpoint is called. Other subcategories keep insert-then-upload.
  - The required-docs rule moved to `requestAttachments.js`.
  - `initialCategory` / `initialSubcategory` props preselect a new request.
- **`/request?category=…&subcategory=…`** opens the form preselected when the user may create a request; otherwise the list shows with the existing disabled reason.
- **Scholarship page blocked view.** A normal Accepted beneficiary gets "apply from My Requests" (link to `/request` with Scholarship preselected). A submitted scholarship applicant sees the registration status, and the same link once Accepted. Other normal registrations keep the existing message.
- **Desk.** 18 fields the scholarship wizard hides (personal, family, children, Afif assistance and the 4 replaced income checks) get `!doc.is_scholarship` in `depends_on`. `is_scholarship` was already in the list view and standard filters of both DocTypes (Phase 1).
- **Home.** A scholarship Draft already opens the scholarship wizard (Phase 1); checked again in the browser.

### Tests
- **New:** `bench --site afif.akwad.qa run-tests --module afif.api.test_scholarship_accepted`: **12 tests, OK.**
  - Accepted user creates the request: `Pending Supervisor Approval`, `is_scholarship=0`, all 8 files attached by field, registration unchanged.
  - Missing attachment (new and reused field), amount, summary or declaration → `IncompleteScholarshipRequestError`, nothing created.
  - Someone else's file, or a file already attached elsewhere → `PermissionError`, nothing created. A non-accepted user → `PermissionError`.
  - Cooldowns (OQ5): pending request, rejection < 3 months, approval < 6 months each block; past both cooldowns it is allowed; an approved scholarship request blocks the next request for 6 months; a pending scholarship request blocks the next one.
  - Supervisor approval of an accepted user's scholarship request: no cascade, the registration stays Accepted, no Sanadi beneficiary call, the subvention request sends the existing `ben_id` with `1001050`.
- **Regression:** `--module afif.api.test_scholarship` **19 OK**; `--module afif.api.test_scholarship_decision` **13 OK**.
- **Mutation check.** Dropping the file-ownership check and inserting with `ignore_permissions` fails 3 tests (both file tests and the non-accepted user).
- **Frontend:** `yarn test:run` **22 tests, OK** (9 new in `requestAttachments.test.js`: 8 scholarship docs and their labels, the normal Education docs unchanged, no scholarship rule outside Education, the read-only field list, AR/EN keys). Biome lint is clean on the new files. `yarn build` done; `migrate` done for the desk `depends_on`.

### Browser run (agent-browser, temporary `bench serve` on :8010, stopped afterwards)
The headless Chrome now starts: `libasound.so.2` was extracted from the Ubuntu package into the session scratchpad and passed with `LD_LIBRARY_PATH` (nothing installed system-wide).

| Check | Result |
|---|---|
| `/scholarship` as `scholarship.demo.phase4.accepted@example.com` (normal, Accepted) | "apply from My Requests" button → `/request?category=Education+Assistance&subcategory=Scholarship` |
| The form | Education Assistance / منحة دراسية preselected, 8 documents, 2 declarations |
| Empty save | popup lists 12 items; with the files in, only the 2 declarations |
| Save | success view; `REQ3888` is Education / Scholarship, `is_scholarship=0`, Pending Supervisor Approval, 18000, both declarations set, 8 private files owned by the user and attached by field; `SA-6624-2026` still Accepted |
| Back to the list | `REQ3888` listed, "create new" disabled (pending); its read-only view shows the 8 files and both declarations ticked and disabled |
| Same link as `scholarship.demo.phase4.pending@example.com` (pending `REQ3887`) | list shown, not the form; "create new" disabled |
| `/scholarship` as `phase3.approve` / `phase3.reject` | "تم تقديم طلب المنحة" with status تسجيل جديد / غير مقبول |
| `/scholarship` as `draft2` | the 5-step wizard |
| `/beneficiary-profile` as `draft2`, click the Draft | redirected to `/scholarship` |
| Desk as `scholarship.demo.supervisor@example.com` | `SA-6621-2026` (scholarship): the 9 checked hidden fields are hidden; guardian mobile, father/mother income and passport number shown. `SA-6624-2026` (normal): the opposite |

### Demo data added on the dev site (on purpose)
Password: `Scholarship@2026`.

| User | State |
|---|---|
| `scholarship.demo.phase4.accepted@example.com` | normal registration `SA-6624-2026`, Accepted, `ben_id = demo-p4-accepted`; applied through the browser: `REQ3888` (Education / Scholarship, pending) |
| `scholarship.demo.phase4.pending@example.com` | normal registration `SA-6625-2026`, Accepted, `ben_id = demo-p4-pending`, with a pending Tuition Fees request `REQ3887`, so a new request is blocked |

Their `ben_id` values are placeholders (not real Sanadi ids), and the registration attachments point to `/files/test-*.pdf`, as in the earlier demo data.

## Phase 3 — log (2026-10-19)

### What was built
- **Approve cascade.** `BeneficiaryRequest.on_update` (it runs before the `on_update` doc_events) accepts the linked `New Registration` when a scholarship request moves from `Pending Supervisor Approval` to `Pending Specialist Approval`. `create_new_beneficiary` then registers the beneficiary in Sanadi and sets `ben_id`, and only after that does `new_subvention_request` send the request. If `ben_id` is still empty afterwards, `ScholarshipCascadeError` rolls the whole action back.
- **Reject cascade.** `Rejected by Supervisor` sets the registration to `Not Accepted`, with `custom_notes` = "Scholarship request REQxxxx was rejected."
- **Registration guard (OQ4).** `ScholarshipDecisionError` blocks a direct change to `Accepted` / `Not Accepted` while the registration has a scholarship request pending with the Supervisor.
- **Sanadi lookup (OQ6).** Scholarship → `(10010, 1001050)`, the same code as Other Educational Assistance. An unmapped category or subcategory raises `UnmappedAidLookupError`, and the scholarship approval checks the mapping in `validate`, before any Sanadi call.
- **Desk.** `check_beneficiary_id` returns success for a scholarship request whose registration is still `New Registration`.
- **Commit removed** from `create_new_beneficiary` (see the deviations below).

### Tests
- **New:** `bench --site afif.akwad.qa run-tests --module afif.api.test_scholarship_decision`: **13 tests, OK.**
  - Sanadi is faked by URL: it records the calls and can fail one endpoint.
  - Approve: registration Accepted with `ben_id`, request in Pending Specialist Approval with `request_id`, and the beneficiary call made before the subvention request, which sends `benId` and `(10010, 1001050)`.
  - Reject: registration Not Accepted with the note, and no Sanadi call.
  - Sanadi failure (the beneficiary call fails, or authentication fails), rolled back to a savepoint as the request handler would: both documents unchanged.
  - Direct Approve/Reject on the registration is blocked. A rejected applicant who resubmits can be approved directly.
  - No declaration → `Not a valid Workflow Action`, and nothing changes.
  - Unmapped subcategory → error before any Sanadi call.
  - Lookup mapping (Scholarship, Tuition Fees unchanged, unknown subcategory or category); `new_aid_request` sends `(10010, 1001050)`; the `check_beneficiary_id` pass-through; a normal request approval leaves the registration alone.
- **Existing:** `--module afif.api.test_scholarship`: **19 tests, OK.**
- **Mutation check.** Each of these fails the suite: dropping the cascade call (5 tests), the registration guard (3), the fail-fast lookup (1), or the `ben_id` check (1).
- Frontend untouched (no Vitest or build change).

### Desk run (temporary `bench serve` on :8010, stopped afterwards)
The headless browser could not start (`libasound.so.2` is missing on the server). The desk actions were driven through the same endpoints the desk buttons call (`frappe.model.workflow.apply_workflow`, `run_doc_method`), logged in as `scholarship.demo.supervisor@example.com`:

| Action | Result |
|---|---|
| `check_beneficiary_id` on `REQ3884` | `success: true` |
| Approve / Reject `SA-6621-2026` directly | blocked: "Approve or reject the scholarship request REQ3884; this registration follows its decision." |
| Approve `REQ3886` (no declaration) | `Not a valid Workflow Action` |
| Reject `REQ3885` | request `Rejected by Supervisor`; `SA-6622-2026` `Not Accepted` with the note |
| Approve `REQ3884` | stops at "Sanadi Integration Settings not available for current user." (see the blockers) |

### Demo data added on the dev site (on purpose)
Password: `Scholarship@2026`. Each applicant was submitted through the endpoint and has the Sanadi profile fields (gender, education level, relation type, city) filled in.

| User | State |
|---|---|
| `scholarship.demo.supervisor@example.com` | System User with the `Supervisor` role, for the desk |
| `scholarship.demo.phase3.approve@example.com` | `SA-6621-2026` + `REQ3884`, declaration uploaded: ready to **approve** |
| `scholarship.demo.phase3.reject@example.com` | `SA-6622-2026` + `REQ3885`: **rejected** in the desk run (registration Not Accepted) |
| `scholarship.demo.phase3.nodeclaration@example.com` | `SA-6623-2026` + `REQ3886`, **no declaration**: approval is blocked until one is uploaded |

The registration attachments on these records point to placeholder `/files/test-*.pdf` URLs, as in the test fixtures.

## Phase 2 — log (2026-10-18)

### What was built
- **Fields.** `father_income` / `mother_income` Checks on the registration (shown in desk only when `is_scholarship`), each with `*_periodicity`, `*_amount` and `*_note`. They follow the existing income pattern: `depends_on` the Check and `mandatory_depends_on` at `current_step == 2`.
- **Sanadi.** `get_beneficiary_income_set` sends both as income type 5 (family).
- **Endpoint.** `submit_scholarship_application` now refuses a registration without `guardian_mobile_number` (`IncompleteScholarshipApplicationError`). Nothing is submitted.
- **Frontend.**
  - `registrationVariant.js`: `getRegistrationVariant(flow)` returns the hidden fields, the income sources and the obligation label keys for each flow. The scholarship constants (`SCHOLARSHIP_ATTACHMENT_FIELDS`, `SCHOLARSHIP_DECLARATION_FIELDS`) moved here from `ScholarshipRequestCard.vue`.
  - `registrationValidation.js`: `validateStep` moved out of the wizard into `validateRegistrationStep`, split by step. A hidden field is never required or format-checked. The duplicated income list is gone; the card and the validation read the same sources.
  - Cards take a `flow` prop. `PersonalInfoCard` hides the ID expiry date, passport, partner phone, secondary ID group and `worked_before`, and shows the guardian mobile (8 digits, required). `FamilyDetailsCard` hides family visa, other dependants, children and Afif assistance. `IncomeDetailsCard` shows guardian salary, father, mother, private business and stock market. `FinancialObligationsCard` relabels the 5 obligations.
  - The wizard loads and saves the new fields, and **leaves hidden fields out of the step-1 payload**, so card defaults such as `ben_sec_idtype = Passport` are never saved on a scholarship registration.
  - AR/EN keys under `scholarship.personalInfo`, `scholarship.incomeDetails` and `scholarship.financialObligations`.

### Tests
- **Backend:** `bench --site afif.akwad.qa run-tests --module afif.api.test_scholarship`: **18 tests, OK** (15 from Phase 1 + 3 new: missing guardian mobile creates nothing; father/mother → two type-5 rows; unchecked parent income is not sent).
- **Frontend (first Vitest suite in the app):** `yarn test:run`: **10 tests, OK**, in `registrationValidation.test.js`.
  - Scholarship step 1 with the hidden fields empty passes; normal mode with the same data fails on those fields; normal mode passes once they are filled.
  - Guardian mobile is required and must be 8 digits, only in scholarship mode.
  - Step 2: a checked parent income requires its details; incomes hidden by the flow don't count towards "at least one"; the popup uses the scholarship labels.
  - Attachments sub-step: documents that only hidden fields can trigger (children IDs, sponsored IDs, termination letter) are not required.
  - Every label key of both variants exists in AR and EN.
- **Mutation check.** Making `isShown` always true, or making step 2 use the normal income list, fails 2 and 3 frontend tests respectively. Dropping the guardian requirement, or the father/mother branch, fails the matching backend test.
- `yarn build` OK. Biome lint is clean on the new files.

### Browser run (temporary `bench serve` on :8010, stopped afterwards)
`scholarship.demo.phase2.new@example.com`:
- Step 1: the hidden fields are not shown. Empty Next lists 15 items, including رقم جوال ولي الأمر and none of the hidden fields.
- Step 2: exactly 5 income sources with the scholarship labels. Guardian salary, father and mother checked with empty details → the popup lists their 9 sub-fields.
- Step 3: the 5 relabelled obligations.
- Step 4 + attachments: only the 8 documents the visible answers require. Step 5: amount, 8 files, 2 declarations → success view.
- Result: `SA-6620-2026` is in `New Registration`, with the guardian mobile and father/mother incomes saved, and `passport_number` / `ben_sec_idtype` empty. `REQ3883` is Education Assistance / Scholarship, `is_scholarship=1`, `Pending Supervisor Approval`. `get_beneficiary_income_set` gives rows of types 1, 5 and 5.
- Normal wizard (`scholarship.demo.new@example.com`, `/beneficiary-profile`): every original field is shown and the guardian mobile is not.

### Demo data added on the dev site (on purpose)
Password: `Scholarship@2026`.

| User | State |
|---|---|
| `scholarship.demo.phase2.new@example.com` | submitted through the browser: `SA-6620-2026` + `REQ3883` |
| `scholarship.demo.phase2.draft@example.com` | complete Phase 2 scholarship Draft `SA-6619-2026` (no hidden fields, guardian mobile, father/mother incomes), ready for step 5 |

`SA-6617-2026` (Phase 1 Draft) was given a guardian mobile number (`55000102`) so it can still be submitted under the new rule. The other Phase 1 records were created before Phase 2 and still have the now-hidden fields filled in.

## Phase 1 — log (2026-10-18)

### What was built
- **Fields.** `is_scholarship` on the registration and the request (read only, list view, standard filter); `guardian_mobile_number` on the registration; `Scholarship` option on `educational_assistance` in the request and the Aid; 6 `scholarship_*` Attach fields and the 2 declaration Checks on the request.
- **Controllers.**
  - Both DocTypes reject a change to `is_scholarship` after insert.
  - The request rejects `is_scholarship=1` on insert unless `flags.is_scholarship_submission` is set.
  - An Education / Scholarship request needs `requested_amount > 0`, all 8 attachments and both declarations (`IncompleteScholarshipRequestError`).
  - A scholarship registration cannot leave `Draft` without the flag (`ScholarshipSubmissionError`), so it can only be submitted together with its request.
- **`before_insert_request`** returns early for the scholarship submission: it only sets `request_date`.
- **Endpoint** `afif.api.scholarship.submit_scholarship_application(registration, request)`. Every check runs before the first write: ownership and Draft state, registration attachments and consents, step-5 data, and file ownership. It then runs `apply_workflow(..., "Submit")`, inserts the request and attaches the files to it. Returns through the new `afif/api/response.py → gen_response`.
- **Frontend.**
  - `/scholarship` route, a website route rule, and a sidebar, mobile menu and nav item.
  - `pages/Scholarship.vue`: wizard, blocked view and success view.
  - `BeneficiaryRegistration.vue` takes a `flow` prop and shows a 5th step. Its attachments sub-step saves and advances, and step 5 uploads private unattached files and calls the endpoint.
  - New `ScholarshipRequestCard.vue`, and AR/EN keys.

### Checks requested by the phase plan
- **No `frappe.db.commit()` on the Submit path.** `updated_status` has no commit, `create_new_beneficiary` only acts on `Accepted`, and `link_user` only runs `after_insert`. Confirmed.
- **`declaration`'s `mandatory_depends_on`.** Frappe v16 never evaluates `mandatory_depends_on` on the server (`frappe/model` has no reference to it), so it cannot block the insert. This also means every `mandatory_depends_on` on the request (such as `education_invoice`) is enforced only in the desk UI. The scholarship rules are therefore enforced in `validate`.

### Tests
`bench --site afif.akwad.qa run-tests --module afif.api.test_scholarship`: **15 tests, OK.** `requests.post` is patched to fail if it is ever called.
- Happy path.
- Missing registration attachment, missing consent, and missing step-5 data (5 sub-cases): each creates nothing.
- Someone else's registration, someone else's file, and a file already attached elsewhere: each raises `PermissionError`.
- Resubmitting is blocked.
- A change to the flag on either DocType raises.
- The registration cannot be submitted without its request.
- A plain insert of an `is_scholarship=1` request raises for both a non-accepted user and an accepted user.
- The normal flow is unchanged: registration Submit, and an accepted user's Tuition Fees request.

Mutation check: dropping the file-owner filter, or the insert-time flag guard, makes the tests fail.

### Browser run (temporary `bench serve` on :8010 against the same site)
`scholarship.demo.draft@example.com`:
- Home → the scholarship Draft redirects to `/scholarship`.
- Steps 1–4 and the attachments sub-step: saved, still `Draft`, no `apply_workflow` call.
- Step 5 empty → the validation popup lists all 11 items.
- Fill in, upload 8 PDFs, submit → success view.

Result:
- `SA-6616-2026` is in `New Registration`.
- `REQ3882` is Education Assistance / Scholarship, `is_scholarship=1`, `Pending Supervisor Approval`.
- All 8 files are private, owned by the user and attached to `REQ3882` by field.
- Revisiting `/scholarship` shows the blocked view.
- A user with no registration gets the 5-step wizard.

Not driven in the browser: a full step-1 insert by a brand-new user. It is the existing insert path plus `is_scholarship: 1`, which the seed and the tests also exercise.

### Demo data left on the dev site (on purpose)
Password for all of them: `Scholarship@2026`.

| User | State |
|---|---|
| `scholarship.demo.new@example.com` | no registration, to try the wizard from scratch |
| `scholarship.demo.draft@example.com` | submitted through the browser: `SA-6616-2026` + `REQ3882` |
| `scholarship.demo.draft2@example.com` | complete scholarship Draft `SA-6617-2026`, ready for step 5 |
| `scholarship.demo.submitted@example.com` | submitted through the endpoint: `SA-6618-2026` + `REQ3881` |

`bench run-tests` also committed Frappe's own standard test records on the site, such as `test@example.com` and `testperm@example.com`. Phase 1's own test data is rolled back.

## Deviations from plan
- Scholarship moved from a new `request_category` to a subcategory of Education Assistance (mentor answer). The `Categories` patch was dropped because `Education Assistance` already exists.
- `education_invoice` and `grade_transcript` are reused for the university invoice and the transcript, so 6 new Attach fields instead of 8.
- **The request is inserted with `ignore_permissions`.** Real new users only hold the `Beneficiary New Registration` role, which has no create permission on Beneficiary Request. The endpoint is the authorization point: it checks that the caller owns the registration and every file.
- **The endpoint sets `beneficiaries` itself** from the registration it submits. `before_insert_request` doesn't look it up by user.
- **Guards added beyond the plan.**
  - A scholarship registration can't leave `Draft` without its request.
  - `is_scholarship=1` can only be set on a request by the endpoint. Accepted users' Phase 4 Scholarship requests will therefore have `is_scholarship=0`, which matches D1.
- **`guardian_mobile_number`.** Phase 1 only checks the format (8 digits when set). Making it required, and showing it in the wizard, belongs to Phase 2 with the other field variants.
- **Step-5 data stays in memory** until submit and is not saved with the Draft.
- **Extra frontend changes.** A `/scholarship` website route rule was added, so a direct load or refresh works. Home sends scholarship Drafts to `/scholarship`. The wizard's 5 duplicated `docMeta` blocks were folded into `toDocMeta()`, which carries `is_scholarship`; it has to, because `frappe.client.save` rebuilds the doc from the payload.
- **Step-5 uploads accept PDF/JPG/PNG only**, because Frappe rejects other types from website users anyway.
- **OQ1b.** `request_summary` was first shown as optional; on 2026-10-19 the mentor made it required (see below).
- **Figma.** Node `723:1544` was not opened (no file key in the spec). The card follows the existing `AttachmentsCard` style.

### Phase 2
- **Module names.** The variant lives in `registrationVariant.js` (both flows), not `scholarshipVariant.js`. `validateStep` was moved to `registrationValidation.js` so Vitest can test it without mounting the wizard. The phase plan was updated to match.
- **Guardian mobile is also enforced on the server**, in `submit_scholarship_application`, not only in the wizard.
- **Hidden fields are stripped from the step-1 payload.** Without this, the card default `ben_sec_idtype = Passport` would be saved with no passport number and sent to Sanadi.
- **Labels the plan didn't specify.** The guardian-salary checkbox reads هل يوجد راتب لولي الأمر؟, the father/mother sub-fields read آلية صرف دخل الأب / مبلغ دخل الأب / ملاحظات (same for the mother), and the section titles follow the existing pattern. These need a check against Figma.
- **Obligation sub-field labels** (amount, periodicity, …) keep the normal wording; only the 5 checkbox labels change, as plan §3 lists.
- The obligation sub-field list is still duplicated between `FinancialObligationsCard` and the validation. The plan only asked to deduplicate the income list.

### Phase 4
- **New endpoint instead of `frappe.client.insert`.** The plan expected the Phase 1 validation alone to be enough, but the normal page's insert-then-upload can't pass it. Uploading first and inserting through `frappe.client.insert` would have worked too, but the endpoint keeps the Phase 1 file-ownership check and creates the request and its attachments in one transaction. A direct `frappe.client.insert` with file URLs is still possible, as for every other category (unchanged).
- **The normal path uploads only the required documents.** It used to upload every file still held in memory, so a file picked for a subcategory the user then left could be attached to the request. Only the visible documents are uploaded now.
- **Desk hiding covers 18 fields**, not only the 7 top-level ones: the children and Afif-assistance sub-fields also get the guard, because the Phase 1 demo records still have the parent answers filled in. Mandatory rules were not changed: they key on `current_step` 1/2, and a submitted registration is at step 5.
- The blocked view for a not-yet-accepted normal registration keeps the existing message.

### Phase 3
- **Cascade location.** The cascade lives in the request controller (`validate` + `on_update`), not in `hooks_call.py`. The controller's methods run before the doc_events, which gives the order D11 needs without reordering `hooks.py`.
- **Order of Sanadi calls.** `validate_subvention_request` (a read-only "active requests" search) still runs in `validate`, so it happens *before* the registration is accepted. The plan listed it after. It doesn't need `ben_id`, and running it first means a beneficiary with an active Sanadi request is rejected before a Sanadi beneficiary is created.
- **The `ben_id` check.** `create_new_beneficiary` only logs an authentication or token failure, and the registration would be Accepted without `ben_id`. The cascade therefore requires `ben_id` after accepting, and fails otherwise.
- **Rejection note.** The request has no notes field to copy, so the registration gets a fixed note naming the request.
- **Guard scope.** OQ4 is enforced while a scholarship request is pending, not for every scholarship registration. Without this, a rejected applicant who resubmits through the normal wizard (`Not Accepted` → `New Registration`) could never be approved. Recorded as OQ13.
- **Desk guard.** Changed on the server, in `check_beneficiary_id`, instead of in `beneficiary_request.js`. The JS keeps calling it, and the rule stays on the server.
- **Known risk resolved.** Frappe v16 ignores `frappe.db.commit()` inside doc_event hooks (`_disable_transaction_control`), so the commit in `create_new_beneficiary` never broke atomicity. It was removed anyway, and its raw SQL was replaced by `frappe.db.set_value`. `new_subvention_request` has the same ignored commit; it was left alone. Sanadi itself can't roll back: if the request step fails after Sanadi created the beneficiary, the beneficiary stays in Sanadi.
- **Unmapped lookup.** Uses `UnmappedAidLookupError` for every category, which also covers the normal flow (it used to crash with `UnboundLocalError`).

## Mentor answers — 2026-10-19
- **OQ6:** for now Scholarship is sent to Sanadi as `1001050` (Other Educational Assistance) under Education `10010`, for both the request and the Aid. Swap the code in `get_aid_lookup_parent_id` once Sanadi has a dedicated Scholarship code.
- **OQ1b:** the request summary is required in step 5. Done in the server validation (`get_missing_scholarship_fields`, empty or blank fails), the wizard validation and the card (asterisk; "(optional)" dropped from the placeholder). Tests: 2 new backend sub-cases (missing and blank summary) → `bench run-tests --module afif.api.test_scholarship` **18 tests, OK**; 2 new Vitest cases for step 5 → `vitest run` **12 tests, OK**. `yarn build` redone on the dev site; the Python part goes live with `bench restart`.
- **OQ3:** same as today: the office uploads the declaration, then the Supervisor approves. No workflow change (Phase 3 adds a test that approval without it is blocked).
- **OQ4:** block direct Approve/Reject on a scholarship registration (Phase 3).
- **OQ5:** the normal request rules apply to scholarship requests (Phase 4). The new-applicant submission keeps its single exception to "accepted beneficiaries only".

- **OQ10:** the 21+ age check exists, but only in the wizard (no server check, normal flow included). The scholarship keeps it; noted under blockers for the mentor to check later.
- **OQ11:** today's rule stays: the registration passport copy is required, so it is not dropped for scholarship.
- **OQ12:** today's rule stays. All 618 accepted registrations have a passport number, and none was accepted without one. So the scholarship wizard shows and requires the passport number and the secondary-ID group again (removed from the scholarship `hiddenFields`), and `submit_scholarship_application` also requires `passport_number`. Tests: Vitest **13 OK** (new: the passport number and secondary ID are required in scholarship mode; it fails if they are hidden again); backend **19 OK** (new: a missing passport number creates nothing). `yarn build` redone; the endpoint check goes live with `bench restart`.

## Open issues / blockers
- **Go-live for Phases 1–4.** `migrate` and `yarn build` are done on `afif.akwad.qa`. `bench restart` needs sudo and is **not done**, so the live gunicorn still runs the old `before_insert_request`, controllers, endpoints, income mapping and none of the Phase 3 cascade. A scholarship submit on the live site fails until it is restarted, and so does the Phase 4 request page for Scholarship (`create_scholarship_request` doesn't exist in the running code). The new fields, the desk `depends_on` and the frontend are live already.
- **Supervisor approval on the dev site.** Only `Administrator` has Sanadi Integration Settings (pointing at staging, `stgapi.raca.gov.qa`). Any other Supervisor, including the demo one, gets "Sanadi Integration Settings not available for current user." when approving any request, normal or scholarship. Approving `REQ3884` as Administrator would create a real beneficiary and request in Sanadi staging, so it was **not done**. It needs a go-ahead, or Sanadi settings for the demo Supervisor.
- **OQ13 — after a scholarship rejection (new, for the mentor).** The applicant can fix and resubmit through the normal wizard, and the registration is then reviewed as a normal one with no scholarship request. Is that intended, or should they be able to reapply through `/scholarship`?
- **OQ6 is temporary.** Scholarship shares Sanadi code `1001050` with Other Educational Assistance, so Sanadi reports can't tell the two apart until a dedicated code exists.
- Still open with the mentor: OQ10 (to check later) and OQ13. OQ14 was closed in Phase 6 (asked of everyone, as in the normal wizard).
- **Older scholarship requests and the new statements.** `REQ3881`–`REQ3888` have 8 documents; saving one in the desk now fails until the mother's and student's statements are added. Fine for demo data; check before go-live whether real requests exist by then. OQ1b, OQ3, OQ4, OQ5, OQ6 (for now), OQ11 and OQ12 are answered (see [plan.md §7](plan.md#7-open-questions)).
- **OQ10 — minimum age (note, mentor to check later).** The wizard requires the applicant to be at least 21 (`MINIMUM_AGE` in `registrationValidation.js`). There is no server-side check, in the normal flow either. The scholarship keeps the rule, so a student under 21 cannot apply as the applicant.
- **Demo record `SA-6620-2026` (Phase 2)** was submitted while the passport was hidden, so it has no passport number. If it is used to try the Phase 3 approval, add a passport number to it first.
- **Resolved in Phase 4:** the desk now hides the fields the wizard skips; the request page uploads before creating a Scholarship request.
- **Applicants can't see their scholarship request before acceptance.** `Beneficiary New Registration` has no read permission on Beneficiary Request, so the scholarship page shows the registration status instead (Phase 4). Granting read access is a permission change for the mentor to decide.
- **Browser runs on this server** need `libasound.so.2`, which is not installed. Phase 4 used a copy extracted into the session scratchpad; installing `libasound2` system-wide (sudo) would make it permanent.
- **Review notes (low).**
  - Files uploaded in step 5 stay as unattached private Files if the applicant abandons the flow. A retry reuses them.
  - `ScholarshipRequestCard` and `AttachmentsCard` emit the whole model from props. Two updates in the same tick lose the first one. Normal clicks are not affected; it showed up only with scripted clicks.
- The existing code uses DB Workflows, raw SQL and `frappe.db.commit()`. These conflict with the project rules, but this feature leaves them alone, except where Phase 3 needs atomicity.
