# Phase 8 — Editing a scholarship application, and request rejection

Review from 2026-10-20. Constraint from the mentor: **the normal flow must not change**, in the backend or the frontend. Every change is limited to scholarship records.

## Decisions (mentor, 2026-10-20)

| # | Decision |
|---|---|
| P8-1 | **Edits happen in the profile.** For a scholarship registration only, `/beneficiary-profile` shows a 5th step after the registration attachments: the 10 scholarship documents and the latest request's details. A normal registration keeps exactly its 4 steps. |
| P8-2 | **In that step, the documents are editable and the request details are read only.** The documents are registration fields. The amount, the summary and the declarations belong to the submitted request. When a scholarship registration is edited, its final save (including the "Review" resubmit of a Not Accepted registration) happens on step 5 instead of the attachments step. |
| P8-3 | **Rejecting a scholarship request only rejects the request**, as in the normal request flow: the registration is left as it is. This **replaces D9**. Afterwards, the Supervisor decides the registration through its own workflow (the OQ4 guard applies only while the request is pending). Approval is unchanged: approving the request still accepts the registration (D11). A rejected request stays final, as in the normal flow. |
| P8-4 | **"Needs an update" before a decision** is an open question (OQ15). For now the Supervisor has only Approve/Reject on the request, and the workflows are untouched. |
| P8-5 | **Clearing the scholarship documents on the yearly "Update Required"** is on hold until the mentor's question about the yearly update is answered (OQ16). Nothing changes there in this phase. |

## Changes

- **`beneficiary_request.py`**: the cascade runs on approval only (`accept_scholarship_registration_with_request`). The rejection branch and its note on the registration are removed.
- **`BeneficiaryRegistration.vue`**
  - `hasRequestStep` is true for the scholarship wizard, or for any scholarship registration; for a normal registration it is false, so every condition reduces to today's behaviour.
  - The latest scholarship request is loaded by the component itself. It replaces the Phase 7 `scholarshipRequestName` prop.
  - Editing a submitted scholarship registration saves the attachments step without the workflow, moves to step 5, and does the final save there.
- **`ScholarshipRequestCard.vue`**: a `requestReadOnly` mode, where the amount, the summary and the declarations are locked and the documents stay editable.
- **`registrationValidation.js`**: a submitted request's fields are not re-validated, but the documents are.

## Tests

- **Backend**
  - Rejecting a scholarship request leaves the registration in New Registration, with no note, and the Supervisor can then approve the registration directly.
  - Rejecting a normal request does not touch the registration (regression).
- **Vitest**: step 5 of a submitted request requires only the documents.
- **Browser**
  - A Not Accepted scholarship registration in the profile has 5 steps; a document can be replaced, the request details are locked, and resubmitting moves it to Updated.
  - A normal registration in the profile still has 4 steps and submits on the attachments step.
