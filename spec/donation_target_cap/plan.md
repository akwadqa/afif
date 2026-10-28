# Donation target cap

## Requirement

A Donation Project must never collect more than its Required Amount.

Closing the project once it is funded (already shipped, `fe32494`) is not enough on its own. A donor who is already on Dibsy's hosted payment page can still pay after the project closes. This happened on 2026-10-18: project `plj3hv17l4` (target 10,000 QAR) collected 20,000, because DON-00055 (10,000) was paid 35 seconds after DON-00056 and DON-00057 had already met the target.

## Decisions

- **Reserve before paying.** An unpaid checkout counts against the target until Dibsy expires it. A new donation is accepted only if it fits in what is left: `required − donated − reserved`.
- **Never accept more than what is left** (confirmed by the product owner). A 500 QAR donation with 300 QAR left is refused, and the donor is told 300 QAR is available.
- **Serialize the check.** `create_donation` locks the project row (`SELECT … FOR UPDATE`) before computing what is left. Two donors clicking at the same moment can't both reserve the last part.
- **Reservation window.** It starts at insert as `now + 15 min`, which is Dibsy's checkout lifetime, so the donation is reserved before the Dibsy call commits. It is then replaced by the `expiresAt` Dibsy returns. If the Dibsy call fails, the donation is marked Failed so it releases its reservation.
- **Safety net.** A payment that still makes the project go over its target is flagged `Received After Target Met`, so finance can refund or reallocate it. This covers an admin lowering the Required Amount, delayed webhooks and similar cases. Automatic refunds wait until Dibsy confirms a refund API.
- Projects with no Required Amount (0) have no cap, as today.

## Data model

| DocType | Field | Type | Notes |
|---|---|---|---|
| Donation | `reserved_until` | Datetime, read-only | End of the checkout reservation; only counted while `payment_status = Pending` |
| Donation | `is_over_target` | Check, read-only, in list view and filters | Label "Received After Target Met" |

## Affected areas

- `afif/donation_api.py` (`create_donation`): lock, available-amount check, `reserved_until`, mark Failed on a Dibsy error
- `afif/dibsy.py` (`create_payment`): return Dibsy's `expiresAt`
- `afif/afif/doctype/donation_project/donation_project.py`: `get_available_amount()` and a new `AmountExceedsAvailableError`
- `afif/afif/doctype/donation/donation.py` (`on_update`): set `is_over_target` when crediting
- Frontend `DonationDialog.vue` and `DonationForm.vue`: a localized "only X QAR available" message
- Donation Report: not changed in this feature

## Phases

1. [Phase 1: Reserve and cap](phase-1-reserve-and-cap.md)
2. [Phase 2: Flag payments received after the target was met](phase-2-over-target-flag.md)

## Open items

- Dibsy: manual capture, cancelling open payments, a shorter `expiresAt` and a refund API. Questions have been sent. If Dibsy supports a refund API, phase 2 can later refund automatically.
- DON-00055 (already overpaid, sandbox) and the still-pending DON-00051 and DON-00054 are left as they are. Finance decides what to do with them.
- Hiding preset amounts above what is left (a UI hint) is out of scope. The server rule and the error message are enough for now.
