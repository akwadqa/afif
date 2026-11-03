# Phase 7 — What the applicant sees after submitting

Review from 2026-10-20, after trying Phase 6 in the browser:

- After submitting, `/scholarship` only says "submitted". It should show the full application: the registration and the request.
- `/request` says the user can't make a request and lists none, although the scholarship request exists.
- After approval, `/scholarship` shows an empty request form instead of the submitted data.
- The partner phone must not be required for a Single applicant.

The profile page (`/beneficiary-profile`) stays as it is: it shows the registration only.

## Decisions (mentor, 2026-10-20)

| # | Decision |
|---|---|
| P7-1 | **Two separate flows.** The normal flow (registration only, from the profile) is unchanged. The scholarship flow is always a registration **and** a request. A beneficiary who registered through the normal flow gets nothing on `/scholarship`. This **replaces P6-7**: an accepted normal beneficiary can no longer apply there. |
| P7-2 | **A scholarship applicant always sees the full application on `/scholarship`**, read only, with any status: the registration steps, then step 5 with the latest scholarship request (amount, summary, declarations, documents) and its status. |
| P7-3 | **New scholarship request: same rules as the request page.** Once the registration is Accepted, the last request is closed and the 3- or 6-month wait has passed, `/scholarship` offers a new scholarship request (step 5 only). The server keeps enforcing the rules. |
| P7-4 | **`/request` lists the user's requests before the registration is accepted**, with "create new" disabled. The pending-registration roles get read access to their own requests. |
| P7-5 | **The partner phone is optional for a Single applicant.** Single exists only in the scholarship flow, so every other marital status keeps it required. |

## Backend

- **Patch** `afif/patches/allow_applicants_to_read_their_requests.py`: Custom DocPerm on Beneficiary Request, `read` + `if_owner`, for `Beneficiary New Registration` and `Beneficiary Not Accepted`. Requests from the scholarship submission are owned by the applicant.
- **`create_scholarship_request`** refuses a caller whose registration is not a scholarship registration (P7-1).
- **`partners_phone_number`**: `mandatory_depends_on` skips Single.

## Frontend

- **`components/request/requestEligibility.js`** (new): `getRequestBlockReason(requests, isAccepted)`, moved out of `Request.vue` so `/scholarship` applies the same rules. It also adds the "not accepted" reason.
- **`pages/Request.vue`**: a registration that is not Accepted still sees its requests, with create disabled. It stays blocked only when it has none.
- **`pages/Scholarship.vue`**
  - No registration or a scholarship Draft → wizard.
  - Normal registration → blocked message.
  - Submitted scholarship registration → read-only application, plus a "new scholarship request" button when P7-3 allows it, which opens `ScholarshipApplyForm`.
- **`BeneficiaryRegistration.vue`**: a `scholarshipRequestName` prop loads the request into step 5 for the read-only view. Read-only navigation reaches step 5, and the Edit button is hidden there (edits go through the profile page).
- **`ScholarshipRequestCard.vue`**: an optional request status badge.
- **`registrationValidation.js` / `PersonalInfoCard.vue`**: the partner phone is not required for Single.

## Tests

- **Backend**
  - An accepted normal beneficiary calling `create_scholarship_request` → refused.
  - An accepted scholarship beneficiary can file a new scholarship request after the cooldown; the documents go to the registration.
  - After the patch, a new applicant can read their own request but not someone else's.
- **Vitest**
  - `getRequestBlockReason`: no requests, pending, the cooldowns, not accepted.
  - The partner phone is optional for Single and required for the other statuses.
- **Browser**
  - Submit as a new applicant → `/scholarship` shows the full application with the request data; `/request` lists the request with create disabled.
  - Approve in the desk → `/scholarship` still shows the data, not an empty form.
  - A normal beneficiary on `/scholarship` → blocked.

## Done when

The tests pass, `migrate` and `yarn build` are done, and the paths above have been walked through in the browser.
