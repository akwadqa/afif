# Phase 15 — More than one open scholarship request

**Goal:** An accepted scholarship student can file a new request at any time, even while earlier ones are still in review. The "Apply for a new scholarship" button never disappears. It is disabled, with the reason as a tooltip, only before the first approval (New Registration) or when the account is restricted.

**Why:** The client registered and applied, and the Supervisor approved the request. That accepted the registration but moved the request to `Pending Specialist Approval`, so "a previous request is pending review" hid the button until the Specialist decided.

**Decision (P15-1):** The pending block no longer applies to a scholarship student, for any request, like the cooldowns in P9-7. The Accepted check and the restriction stay. The normal flow keeps the pending block and both cooldowns.

## Files
- `afif/hooks_call.py` `before_insert_request`: the pending check moves under `if not registration.is_scholarship`. The dead commented-out block is removed.
- `frontend/src/components/request/requestEligibility.js`: a scholarship student gets only `restricted` or `notAccepted`.
- `frontend/src/pages/Scholarship.vue`: the button is always rendered. It uses `:disabled` with the hover tooltip from `Request.vue` and the existing `myRequests.disabledReasons` strings.

## Follow-up: the button on the profile (P15-2)
- **Why.** The button lived only on `/scholarship`, so after طلباتي → profile (`/beneficiary-profile`) the student had no way to file a new request.
- **Shared button.** `ScholarshipApplyButton.vue` (prop `status`) holds the button, its disabled state and the tooltip. `Scholarship.vue` and `Home.vue` both use it.
- **Profile.** `Home.vue` shows it for a submitted scholarship registration (`isSubmittedScholarship`) in the header of the registrations list and of the read-only view.
- **Click.** The profile button goes to `/scholarship?apply=1`, which opens the new request form directly for an Accepted registration.

## Tests
- `afif/api/test_scholarship_accepted.py`:
  - A pending request does not block a scholarship request.
  - A pending scholarship request does not block the next one.
  - A pending request still blocks a normal beneficiary.
- `requestEligibility.test.js`:
  - A scholarship request with one pending gives `''`.
  - The normal flow with one pending gives `'pending'`.
- The flipped tests fail before the fix.
- `isSubmittedScholarship`: true for a submitted or accepted scholarship registration; false for a draft, a normal registration, or none.

## Done when
- `test_scholarship_accepted`, `test_scholarship` and `test_scholarship_decision` pass.
- `yarn test:run` and `yarn lint` pass.
- `progress.md` has the Phase 15 log.
