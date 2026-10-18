# Phase 1 — Tracer: end-to-end scholarship submit

## Goal
A new user opens **منحة الشيخ خالد بن ناصر** from the sidebar and completes the existing registration steps plus step 5 (بيانات الطلب), then submits. The result is:

- a `Beneficiaries Registration` in `New Registration` with `is_scholarship=1`;
- a `Beneficiary Request` in `Pending Supervisor Approval` with `request_category="Education Assistance"`, `educational_assistance="Scholarship"` and `is_scholarship=1`.

Field variants (hidden or relabelled fields) are **not** part of this phase. The wizard shows the normal registration fields.

## Scope

### Backend
1. **DocType JSON**
   - Add `is_scholarship` to both DocTypes.
   - Add `guardian_mobile_number` to the registration.
   - Request:
     - add the `Scholarship` option to `educational_assistance`;
     - add the 6 new `scholarship_*` Attach fields;
     - add `is_data_accuracy_declared` and `is_eligibility_check_accepted`;
     - the existing `education_invoice` and `grade_transcript` are reused.
   - Aid: add the `Scholarship` option to `beneficiary_aid.json` → `educational_assistance`, so the committee can pick it when filling in the Aid by hand.
   - The father and mother income fields are added in Phase 2.
2. **Flag immutability**: `validate` on both DocTypes throws if `is_scholarship` changes on an existing document.
3. **Scholarship request validation** (request `validate`): when `educational_assistance == "Scholarship"`, require `requested_amount` (> 0), all 8 attachments and both declarations. This also covers accepted users in Phase 4.
4. **`afif/api/scholarship.py` → `submit_scholarship_application(registration: str, request: dict)`**
   - **Input.** `request` carries the requested amount, the optional `request_summary` (OQ1b), the 8 attachment URLs keyed by fieldname, and the two declarations.
   - **Guards.** The registration's `user` is the session user, `is_scholarship=1`, and the status is `Draft`.
   - **Completeness.** Registration completeness reuses `is_registration_complete` (`hooks_call.py:155`). The request data is checked by the request validation in item 3. Throw a specific `frappe.ValidationError` subclass listing what is missing.
   - **File ownership.** Each attachment URL must belong to a `File` owned by the session user that is not yet attached to anything. This blocks attaching other people's files.
   - **Submit.** Run `apply_workflow(registration, "Submit")` to move it to `New Registration`.
   - **Request.** Insert a `Beneficiary Request` with `request_category="Education Assistance"`, `educational_assistance="Scholarship"`, `is_scholarship=1` and the step-5 data. Before insert, set `doc.flags.is_scholarship_submission = True`. Clients cannot set `doc.flags`, so this is safe.
   - **Link files.** Point each `File` at the request (`attached_to_doctype` / `attached_to_name` / `attached_to_field`).
   - **Return** `{registration, request}` through `gen_response(...)`, as the app's CLAUDE.md requires. That helper doesn't exist in the app yet, so add it in a small `afif/api/response.py`.
   - **Transaction.** No `frappe.db.commit()`. The request transaction makes the whole thing atomic.
5. **`before_insert_request`** (`hooks_call.py:748`): skip the "registration must be Accepted" check when `doc.flags.is_scholarship_submission` is set. The beneficiary link and `request_date` are still set the same way.
6. **Checks to run:**
   - Confirm that no hook on the Submit path (`updated_status`, `create_new_beneficiary` for New Registration, `link_user`) calls `frappe.db.commit()`.
   - Confirm that `declaration`'s `mandatory_depends_on` (`workflow_state==="Pending Supervisor Approval"`) doesn't block the insert. The normal portal insert passes today.

   Record the findings in `progress.md`.

### Frontend (`frontend/src`)
1. Add a `/scholarship` route (`Scholarship`) under `DashboardLayout` in `router.js`.
2. Add a sidebar item (`sidebar.scholarship`) in `AppSidebar.vue`, `MobileMenu.vue` and `NavLinks.vue`.
3. `pages/Scholarship.vue`:
   - loads the user's registrations;
   - if there are none, or there is a scholarship Draft, renders `<BeneficiaryRegistration flow="scholarship" :registration-name>`;
   - otherwise shows a blocked message, which is refined in Phase 4;
   - shows a success view after submit.
4. `BeneficiaryRegistration.vue`:
   - Add a `flow` prop, `'registration'` by default.
   - Scholarship mode adds a 5th step to `stepsList`, so there are 6 logical steps.
   - Send `is_scholarship: 1` on the first insert.
   - On the registration attachments sub-step, **save and advance** instead of `apply_workflow`.
   - On step 5, upload the request files unattached (private) and call the endpoint.
5. New `components/registration/ScholarshipRequestCard.vue` (Figma design):
   - the requested amount (numeric only, like `BeneficiaryRequest.vue`);
   - the optional summary (OQ1b);
   - 8 required upload rows, following the `AttachmentsCard` pattern and `utils/fileValidation.js`;
   - 2 declaration checkboxes.
6. Add AR/EN keys to `locales/translations.js`:
   - `request.subtypes.education.Scholarship`
   - `sidebar.scholarship`
   - `scholarship.title` and `scholarship.subtitle`
   - `scholarship.steps.request`
   - `scholarship.attachments.*`
   - `scholarship.declarations.*`
   - `scholarship.success.*`
   - `scholarship.blocked.*`

## Tests (`test_scholarship.py` under `afif/api/` or the request DocType)
- **Happy path:** the registration moves to `New Registration`; the request is created as Education Assistance / Scholarship with `is_scholarship=1`; the files are re-attached to the request.
- **Missing registration attachment:** raises and creates nothing. No request exists and the registration is still `Draft`.
- **Missing step-5 data:** a missing request attachment, a missing amount, or an unchecked declaration raises and creates nothing.
- **Other people's data:** someone else's registration, or someone else's `File`, raises `PermissionError`.
- **Flag change:** changing `is_scholarship` on an existing document raises.
- **No bypass:** a plain `frappe.client.insert` of a request with `is_scholarship=1` from a non-accepted user is still blocked.

Mock Sanadi calls (`requests.post`) wherever hooks reach them.

## Done when
- The tests above pass.
- A manual run through the browser produces both documents in the expected states.
- The normal registration and request flows still work: register, submit, then submit an aid request as an accepted user.
