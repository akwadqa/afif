# Request required attachments

## Requirement

A Beneficiary Request was saved without its required attachments. Afterwards it couldn't be saved in Desk, because the form blocks Save with "Missing Fields", and the beneficiary can only view it in the portal. Submission must be blocked until every required attachment is uploaded, with a clear message that lists what's missing.

## Root cause

1. The required attachments use only `mandatory_depends_on`, which Frappe evaluates in the browser only. The server accepts the request without them.
2. The SPA inserts the request first and uploads the files one by one afterwards (`upload_file` + `set_value` for each file). If any step after the insert fails (file too large, network, session), the request is left without its files. The "previous request is pending review" check then blocks the beneficiary from resubmitting.
3. The frontend and backend rule lists drifted apart: the SPA required `grade_transcript`, but the doctype didn't.

## Decisions

- The server is the authoritative check: `BeneficiaryRequest.validate_required_attachments()` runs **on insert only**. Existing incomplete requests stay saveable, so staff can fix or reject them.
- `grade_transcript` is required for Education when the subtype isn't Scholarship.
- Upload first, then insert once. Frappe's `attach_files_to_document` hook links the uploaded files to the request when it is saved.
- File privacy stays as it is (`is_private=0`).

## Required attachments

| Category / subtype | Fields |
|---|---|
| Medical Assistance | `medical_bill` |
| Education Assistance (not Scholarship) | `education_invoice`, `grade_transcript` |
| Social Assistance / Garmeen | `garmeen_proof`, `garmeen_disclosure` |
| Social Assistance / Travel ticket assistance | `travel_ticket_doc` |
| Housing Assistance | `rent_contract`, `onwer_qid`, `late_letter` |
| Housing Assistance / Real estate purchase | + `estate_pruchase` |

## Phases

1. [Server validation](phase-1-server-validation.md)
2. [Atomic upload in the SPA](phase-2-atomic-upload.md)

## Existing data

Incomplete requests (e.g. `REQ3887`, and the 2024 Housing/Education requests that were rejected) need no migration. Staff can attach the missing files in Desk, or reject the request through the workflow.
