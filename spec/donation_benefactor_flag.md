# Donation Benefactor Flag — Plan

**Goal:** The backend decides whether donor details are required. A donation marked "فاعل خير" (benefactor) may leave name, mobile and email empty. Any other donation must have all three. The dialog and the full-page form follow the same rules, so a donation that passes the frontend never fails these checks on the server.

## 1. New field on `Donation`

| Label | Fieldname | Type | Default | Placement |
|---|---|---|---|---|
| Benefactor (فاعل خير) | `is_anonymous` | Check | `0` | Donor section, above Donor Name |

- Description: "Donor chose to donate as a benefactor. Name, mobile and email are optional."
- `donor_name`, `donor_mobile` and `donor_email` get `mandatory_depends_on: eval:!doc.is_anonymous`, so the desk form shows the red asterisk and blocks saving.

## 2. Validation (`donation.py` → `validate`)

- If `is_anonymous` is off: throw an error unless name, mobile and email are all filled in. The message names the missing fields.
- If `is_anonymous` is on: the fields are optional. Anything entered is still validated and saved.
- An empty name is still saved as "فاعل خير", as today. This only happens when `is_anonymous` is on, because otherwise the name is required.
- Mobile check (decided): a Qatar mobile number, meaning 8 digits starting with 3, 5, 6 or 7, with or without `+974`. Spaces are stripped, and it's saved as `+974XXXXXXXX`.
- Email check: Frappe's built-in Email field validation.

## 3. Existing data (no patch, decided)

There are 27 existing donations, and 26 of them have no mobile or email. Instead of backfilling them, the required-fields check runs only on new donations, or when the donor fields or `is_anonymous` change. A status update from the Dibsy webhook (`donation.save()` in `dibsy.py`) on an older donation therefore still saves.

## 4. API (`afif/donation_api.py` → `create_donation`)

- New parameter `is_anonymous=0`, cast with `frappe.utils.cint`, and passed to the Donation doc.
- No separate checks in the API: the doctype's `validate` is the single source of truth, so the desk, the API and any future caller apply the same rules.
- Errors come back as a normal `frappe.throw` message, which both frontends already display.

## 5. Frontend

The same changes go in `components/donation/DonationDialog.vue` and `components/donation/DonationForm.vue`:

- Send `is_anonymous: donorForm.isAnonymous ? 1 : 0`.
- Mobile check before submit, using the same rule as the backend: after removing spaces and an optional `+974`, it must be exactly 8 digits. When the mobile is required it must pass. When it's optional it is checked only if filled in.
- Email check: only when it's filled in, if the donor is a benefactor.
- New translation key `donation.donorPhoneInvalid` (AR/EN): "Please enter a valid Qatar mobile number (8 digits)."
- Use `inputmode="tel"` on the mobile input.

## 6. Donation Report

- New filter "Benefactor" (Select: blank / Yes / No) that filters on `is_anonymous`.

## 7. Deploy

- `bench --site afif.akwad.qa migrate` adds the field.
- `bench restart` is needed (sudo), because the API and controller changes only go live after it.
- `yarn build` for the frontend.

## Decisions

1. No patch for existing donations (see section 3).
2. Mobile numbers must use a Qatar mobile prefix: 3, 5, 6 or 7.
3. `is_anonymous` is shown in the Donation Report as a filter.
