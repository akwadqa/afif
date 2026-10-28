# Phase 2: Flag payments received after the target was met

## Goal

Any paid donation that pushes its project over the Required Amount is visibly flagged for finance.

## Scope

- Donation: an `is_over_target` Check field (read-only, in list view and standard filter), labelled "Received After Target Met".
- `Donation.on_update`: when a donation becomes Paid, lock the project row, and set `is_over_target` if `required > 0` and `donated + amount > required`. The money is still credited, because it was really received.

## Files

- `afif/afif/doctype/donation/donation.json`, `donation.py`

## Tests

- A payment that overflows the target is flagged, and one that lands exactly on the target is not.
- A project with no target never flags.

## Done when

The tests pass, a reverted fix makes them fail, and the flag shows in the Donation list filter.
