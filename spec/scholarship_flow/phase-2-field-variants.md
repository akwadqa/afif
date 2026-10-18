# Phase 2 — Scholarship field variants

## Goal
In scholarship mode, the wizard hides, relabels and adds the fields listed in plan §3. Validation only requires the fields that are actually shown.

## Scope

### Backend
- Registration JSON: add the `father_income*` and `mother_income*` fields (plan §3).
- `get_beneficiary_income_set` (`hooks_call.py:670`): map `father_income` and `mother_income` to Sanadi income type 5.

### Frontend
- **One variant config.** Add `components/registration/registrationVariant.js`. `getRegistrationVariant(flow)` returns the hidden field names, the income sources (with label keys) and the obligation label keys for the normal and the scholarship flow. The cards and the step validation must both read this one object so they can't drift apart.
- **Testable validation.** Move `validateStep` into `components/registration/registrationValidation.js` (`validateRegistrationStep`), a plain module that Vitest can import without mounting the wizard.
- **Cards:**
  - `PersonalInfoCard.vue`: add a `flow` prop. Hide `passport_number`, `id_expiry_date`, `partners_phone_number`, the `ben_sec_*` group and `worked_before`. Show `guardian_mobile_number` (8 digits, required).
  - `FamilyDetailsCard.vue`: hide `family_visa_type`, `visa_dependent` and its names field, `have_children` and the children sub-fields, and `afif_charity_assistance` with its amount.
  - `IncomeDetailsCard.vue`: in `incomeSources`, drop `family_income`, `family_extra`, `children_income` and `rent_income`, add `father_income` and `mother_income`, and relabel `ben_income` and `private_income`.
  - `FinancialObligationsCard.vue`: relabel the 5 entries in `obligationSources`.
- **Wizard** (`BeneficiaryRegistration.vue`):
  - `validateStep` skips hidden fields and validates the new ones. The income list duplicated at lines 770-778 should come from the config.
  - `populateFromDoc` and `buildStepPayload` handle the new fields.
- **i18n:** add `scholarship.personalInfo.*`, `scholarship.incomeDetails.*` and `scholarship.financialObligations.*` in AR and EN.

## Tests
- Backend: `get_beneficiary_income_set` returns type-5 rows for the father and mother incomes.
- Backend: `submit_scholarship_application` refuses a registration without `guardian_mobile_number`.
- Frontend (Vitest): a scholarship-mode `validateStep` with the hidden fields empty passes step 1. Normal mode with the same data still fails. This guards the shared validation.

## Done when
- The scholarship wizard matches the Figma screens and the field list.
- The normal wizard is unchanged.
- The tests pass.
