# Phase 4 — Accepted users and desk polish

## Goal
Beneficiaries who are already accepted can apply for the scholarship as a normal request. The edge cases in the portal and desk are tidied up.

## Scope
1. **Scholarship category for accepted users.** In `components/request/BeneficiaryRequest.vue`:
   - add `Scholarship` to `categories`;
   - add the 8 docs to `requiredDocs` (reuse the `scholarship.attachments.*` keys);
   - the server validates that all 8 are present for this category.
   - Apply the cooldown rules in `before_insert_request` according to OQ5.
2. **`pages/Scholarship.vue` blocked state.**
   - A user with a normal registration sees a message. If they are Accepted, the message links to `/request` with the Scholarship category preselected.
   - A user with a submitted scholarship registration sees its status.
3. **`pages/Home.vue`.** A scholarship Draft opens in the scholarship wizard, not the normal one.
4. **Desk.** Confirm that the list view columns and standard filters for `is_scholarship` are set in both DocType JSONs.

## Tests
- A request with category `Scholarship` from an accepted user, missing an attachment → error.
- An accepted user can create a Scholarship request, subject to the cooldown rules in OQ5.

## Done when
- The tests pass.
- Both entry points have been checked manually.
