# Scholarship Flow — Progress

| Phase | Status | Commits |
|---|---|---|
| [1 — Tracer: end-to-end submit](phase-1-tracer.md) | done (live site still needs `bench restart`) | `41fc2c0`, `e77431a`, `5448fe2`, `d8c9642` |
| [2 — Field variants](phase-2-field-variants.md) | todo | |
| [3 — Approval/rejection cascade](phase-3-approval-cascade.md) | todo (needs OQ3, OQ6; OQ4 has a default) | |
| [4 — Accepted users + desk polish](phase-4-accepted-users-desk.md) | todo (OQ5 has a default) | |

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
- **OQ1b default.** `request_summary` is shown as optional.
- **Figma.** Node `723:1544` was not opened (no file key in the spec). The card follows the existing `AttachmentsCard` style.

## Open issues / blockers
- **Go-live for Phase 1.** `migrate` and `yarn build` are done on `afif.akwad.qa`. `bench restart` needs sudo and is **not done**, so the live gunicorn still runs the old `before_insert_request` and controllers, and a scholarship submit on the live site fails until it is restarted.
- Still open with the mentor: OQ3, OQ4, OQ5 and OQ6 (see [plan.md §7](plan.md#7-open-questions)). OQ1b uses its default (optional).
- **Phase 4 input.**
  - The scholarship validation needs the attachments at insert time. The normal `BeneficiaryRequest.vue` inserts first and uploads afterwards, so it must change before `Scholarship` is offered there.
  - `Beneficiary New Registration` has no read permission on Beneficiary Request, so an applicant cannot list their scholarship request until they are accepted.
- **Review notes (low).**
  - Files uploaded in step 5 stay as unattached private Files if the applicant abandons the flow. A retry reuses them.
  - `ScholarshipRequestCard` and `AttachmentsCard` emit the whole model from props. Two updates in the same tick lose the first one. Normal clicks are not affected; it showed up only with scripted clicks.
- The existing code uses DB Workflows, raw SQL and `frappe.db.commit()`. These conflict with the project rules, but this feature leaves them alone, except where Phase 3 needs atomicity.
