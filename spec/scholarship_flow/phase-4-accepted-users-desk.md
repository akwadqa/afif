# Phase 4 — Accepted users and desk polish

> OQ5 answered: the normal request rules apply to scholarship requests from accepted users.

## Goal
Beneficiaries who are already accepted can apply for the scholarship as a normal request: Education Assistance → Scholarship. The edge cases in the portal and desk are tidied up.

## Scope
1. **Scholarship subcategory for accepted users.** In `components/request/BeneficiaryRequest.vue`:
   - add `Scholarship` to `SUBCATEGORY_MAP['Education Assistance'].options`;
   - when it is selected, the required docs are the 8 scholarship docs (`education_invoice` and `grade_transcript` plus the 6 `scholarship_*` fields), labelled with the `scholarship.attachments.*` keys;
   - show the 2 declarations, required;
   - the read-only view shows the scholarship attachments and declarations.

   The required-docs rule moves to `components/request/requestAttachments.js` so Vitest can cover it without mounting the page.
2. **Submit path for the Scholarship subcategory.** The normal page inserts the request first and uploads the files afterwards, but the Phase 1 validation needs all 8 attachments at insert time. For Scholarship only, the page uploads the files first as private, unattached files and calls a new endpoint `afif.api.scholarship.create_scholarship_request(request)`:
   - it builds the Education / Scholarship request with `is_scholarship=0` (the registration is already accepted, so there is no cascade);
   - it checks that every file was uploaded by the caller and is not attached anywhere (`get_unattached_own_files`, as in Phase 1);
   - it inserts the request with **normal permissions**, so `before_insert_request` applies unchanged: accepted beneficiaries only, one open request, the 3-month cooldown after a rejection and the 6-month cooldown after an approval (OQ5);
   - it attaches the files to the request, all in one transaction.

   The other subcategories keep today's insert-then-upload path.
3. **`/request` preselection.** `/request?category=Education Assistance&subcategory=Scholarship` opens the new-request form with both values preselected, if the user may create a request; otherwise the list shows, with the existing disabled reason.
4. **`pages/Scholarship.vue` blocked state.**
   - A user with a normal registration sees a message. If they are Accepted, it links to `/request` with Education Assistance → Scholarship preselected.
   - A user with a submitted scholarship registration sees its status (and the same link once Accepted).
5. **`pages/Home.vue`.** A scholarship Draft opens in the scholarship wizard, not the normal one (done in Phase 1; checked again).
6. **Desk.**
   - `is_scholarship` is in the list view and a standard filter in both DocTypes (set in Phase 1; checked again).
   - The registration fields the scholarship wizard hides are hidden in the desk form of a scholarship registration too: `id_expiry_date`, `partners_phone_number`, `worked_before`, `family_visa_type`, `visa_dependent`, `have_children`, `afif_charity_assistance` and the `family_income`, `family_extra`, `children_income`, `rent_income` Checks (their sub-fields already depend on them). Done with `depends_on`, so normal registrations are unchanged.

## Files
- `afif/api/scholarship.py`, `afif/api/test_scholarship_accepted.py` (new)
- `afif/afif/doctype/beneficiaries_registration/beneficiaries_registration.json`
- `frontend/src/components/request/BeneficiaryRequest.vue`, `requestAttachments.js` + test (new)
- `frontend/src/pages/Request.vue`, `pages/Scholarship.vue`, `locales/translations.js`

## Tests
- **Backend** (`afif/api/test_scholarship_accepted.py`, Sanadi patched to fail if called):
  - An accepted user creates an Education / Scholarship request: `Pending Supervisor Approval`, `is_scholarship=0`, files attached, the registration unchanged.
  - A missing attachment, amount, summary or declaration → `IncompleteScholarshipRequestError`, nothing created.
  - Someone else's file, or a file already attached elsewhere → `PermissionError`, nothing created.
  - A non-accepted user → blocked.
  - Cooldowns (OQ5): a pending request, a request rejected less than 3 months ago, or approved less than 6 months ago blocks it; an approved scholarship request blocks the next request for 6 months; once the cooldown has passed, it is allowed.
  - Supervisor approval of an accepted user's scholarship request leaves the registration alone (no cascade).
- **Frontend (Vitest):** the Scholarship subcategory requires the 8 scholarship docs, the other Education subcategories keep their 2 docs, and every label key exists in AR and EN.
- **Browser:** the scholarship page for a normal accepted user links to `/request` with Scholarship preselected; the request form shows 8 docs and 2 declarations, validates them, and submits; the blocked view shows a submitted scholarship's status.

## Done when
- The tests pass.
- Both entry points have been checked manually.
