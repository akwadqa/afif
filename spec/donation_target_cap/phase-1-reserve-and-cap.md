# Phase 1: Reserve and cap

## Goal

`create_donation` refuses any amount above `required − donated − reserved`, and that check is safe when several donors submit at once.

## Scope

- Donation: a `reserved_until` Datetime field (read-only, in the Payment Details section).
- `DonationProject.get_available_amount()`: returns `None` when there is no target. Otherwise it returns `max(required − donated − Σ amount of Pending donations with reserved_until > now, 0)`.
- `AmountExceedsAvailableError(frappe.ValidationError)`. Its message includes the available amount.
- `create_donation`:
  1. Lock the project row (`frappe.db.get_value(..., for_update=True)`).
  2. Raise `ProjectClosedError` if the project is closed. Raise `AmountExceedsAvailableError` if the amount is above what is available. When nothing is available because of reservations, the message says to try again in a few minutes.
  3. Insert with `reserved_until = now + 15 min`, then commit (as today).
  4. Call Dibsy. On success, set `reserved_until` to Dibsy's `expiresAt`. On failure, set `payment_status = Failed` and re-raise.
- Frontend (dialog and form): on `AmountExceedsAvailableError`, show the localized "Only {amount} QAR is available for this project" message from the server's available amount.

## Files

- `afif/afif/doctype/donation/donation.json`
- `afif/afif/doctype/donation_project/donation_project.py`
- `afif/donation_api.py`, `afif/dibsy.py`
- `frontend/src/components/donation/DonationDialog.vue`, `DonationForm.vue`, `frontend/src/data/donation.js`, `frontend/src/locales/translations.js`

## Tests

- An amount above what is left is refused, and an amount equal to it is accepted.
- An unexpired Pending donation reduces what is available. An expired, Failed or Paid one doesn't count twice.
- A project with no target has no cap.
- If Dibsy fails, the donation is marked Failed and frees its reservation. Dibsy is mocked.
- The 2026-10-18 replay: after a 10,000 reservation, a 9,996 donation is refused.

## Done when

The tests pass, a reverted fix makes them fail, the frontend builds, and a manual sandbox run shows the "only X available" message.
