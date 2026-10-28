# Phase 1: Server validation

## Goal

The server rejects a new Beneficiary Request that is missing any required attachment, and its error message lists the labels of the missing documents.

## Files

- `afif/afif/doctype/beneficiary_request/beneficiary_request.py`: `get_missing_required_attachments()` and `validate_required_attachments()` (insert only)
- `afif/afif/doctype/beneficiary_request/test_beneficiary_request.py`

## Tests

- A Medical request without `medical_bill` is rejected, and the error names the label.
- A Housing / Real estate purchase request missing `estate_pruchase` is rejected; the complete request inserts.
- An Education / Scholarship request needs no invoice or transcript.
- An existing incomplete request can still be saved (regression test for the deadlock).

## Done when

The tests pass, and the first test fails when the fix is reverted.
