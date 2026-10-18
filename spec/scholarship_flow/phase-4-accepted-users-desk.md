# Phase 4 — Accepted users and desk polish

## Goal
Beneficiaries who are already accepted can apply for the scholarship as a normal request: Education Assistance → Scholarship. The edge cases in the portal and desk are tidied up.

## Scope
1. **Scholarship subcategory for accepted users.** In `components/request/BeneficiaryRequest.vue`:
   - add `Scholarship` to `SUBCATEGORY_MAP['Education Assistance'].options`;
   - when it is selected, `requiredDocs` adds the 6 `scholarship_*` docs on top of the existing `education_invoice` and `grade_transcript`, reusing the `scholarship.attachments.*` keys;
   - show the 2 declarations.

   The server-side validation from Phase 1 enforces all of it. Apply the cooldown rules in `before_insert_request` according to OQ5 (default: they apply). These requests have `is_scholarship=0`, because the registration is already accepted, so the cascade doesn't run.
2. **`pages/Scholarship.vue` blocked state.**
   - A user with a normal registration sees a message. If they are Accepted, the message links to `/request` with Education Assistance → Scholarship preselected.
   - A user with a submitted scholarship registration sees its status.
3. **`pages/Home.vue`.** A scholarship Draft opens in the scholarship wizard, not the normal one.
4. **Desk.** Confirm that the list view columns and standard filters for `is_scholarship` are set in both DocType JSONs.

## Tests
- An Education / Scholarship request from an accepted user with a missing attachment or declaration → error.
- An accepted user can create an Education / Scholarship request, subject to the cooldown rules in OQ5, and no cascade runs.

## Done when
- The tests pass.
- Both entry points have been checked manually.
