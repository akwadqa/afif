# Phase 1 — Tracer: end-to-end scholarship submit

## Goal
A new user opens **منحة الشيخ خالد بن ناصر** from the sidebar and completes the existing registration steps plus step 5 (بيانات الطلب), then submits. The result is:

- a `Beneficiaries Registration` in `New Registration` with `is_scholarship=1`;
- a `Beneficiary Request` in `Pending Supervisor Approval` with category `Scholarship` and `is_scholarship=1`.

Field variants (hidden or relabelled fields) are **not** part of this phase. The wizard shows the normal registration fields.

## Scope

### Backend
1. **DocType JSON**
   - Add `is_scholarship` to both DocTypes.
   - Add `guardian_mobile_number` to the registration.
   - Add the `Scholarship` option, the 8 `scholarship_*` Attach fields and `is_scholarship_declaration_accepted` to the request.
   - The father and mother income fields are added in Phase 2.
2. **`Categories` record**: add `afif/patches/add_scholarship_category.py` under `[post_model_sync]` in `patches.txt`. It creates a top-level `Scholarship` record (`category_name="Scholarship"`, `is_group=1`, under the tree root like the others). It does nothing if the record or the `Categories` DocType doesn't exist, so it is safe on fresh sites.
3. **Flag immutability**: `validate` on both DocTypes throws if `is_scholarship` changes on an existing document.
4. **`afif/api/scholarship.py` → `submit_scholarship_application(registration: str, attachments: dict, is_declaration_accepted: bool)`**
   - **Guards.** The registration's `user` is the session user, `is_scholarship=1`, and the status is `Draft`.
   - **Completeness.** Registration completeness reuses `is_registration_complete` (`hooks_call.py:155`). It also checks that all 8 attachment URLs are present and that the declaration is accepted. Throw a specific `frappe.ValidationError` subclass listing what is missing.
   - **File ownership.** Each attachment URL must belong to a `File` owned by the session user that is not yet attached to anything. This blocks attaching other people's files.
   - **Submit.** Run `apply_workflow(registration, "Submit")` to move it to `New Registration`.
   - **Request.** Insert a `Beneficiary Request` with `request_category="Scholarship"`, `is_scholarship=1`, the attachments and the declaration. Before insert, set `doc.flags.is_scholarship_submission = True`. Clients cannot set `doc.flags`, so this is safe.
   - **Link files.** Point each `File` at the request (`attached_to_doctype` / `attached_to_name` / `attached_to_field`).
   - **Return** `{registration, request}` through `gen_response(...)`, as the app's CLAUDE.md requires. That helper doesn't exist in the app yet, so add it in a small `afif/api/response.py`.
   - **Transaction.** No `frappe.db.commit()`. The request transaction makes the whole thing atomic.
5. **`before_insert_request`** (`hooks_call.py:748`): skip the "registration must be Accepted" check when `doc.flags.is_scholarship_submission` is set. The beneficiary link and `request_date` are still set the same way.
6. **Atomicity check:** confirm that no hook on the Submit path (`updated_status`, `create_new_beneficiary` for New Registration, `link_user`) calls `frappe.db.commit()`. If one does, document it in `progress.md` and handle it.

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
5. New `components/registration/ScholarshipRequestCard.vue`:
   - 8 required upload rows (Figma design), following the `AttachmentsCard` pattern and `utils/fileValidation.js`;
   - one declaration checkbox.
6. Add `Scholarship` to the category label map in `pages/Request.vue`, so scholarship requests show a translated type in the requests list. Adding it to the `categories` dropdown in `BeneficiaryRequest.vue` is Phase 4.
7. Add AR/EN keys to `locales/translations.js`:
   - `request.categories.scholarship`
   - `sidebar.scholarship`
   - `scholarship.title` and `scholarship.subtitle`
   - `scholarship.steps.request`
   - `scholarship.attachments.*`
   - `scholarship.declaration`
   - `scholarship.success.*`
   - `scholarship.blocked.*`

## Tests (`test_scholarship.py` under `afif/api/` or the request DocType)
- Happy path: registration → `New Registration`; request created with category `Scholarship` and `is_scholarship=1`; files re-attached to the request.
- A missing registration attachment raises and creates nothing (no request; registration still `Draft`).
- A missing request attachment or an unaccepted declaration raises and creates nothing.
- Someone else's registration, or someone else's `File`, raises `PermissionError`.
- Changing `is_scholarship` on an existing document raises.
- A plain `frappe.client.insert` of a request with `is_scholarship=1` from a non-accepted user is still blocked.

Mock Sanadi calls (`requests.post`) wherever hooks reach them.

## Done when
- The tests above pass.
- A manual run through the browser produces both documents in the expected states.
- The normal registration and request flows still work: register, submit, then submit an aid request as an accepted user.
