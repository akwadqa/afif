# Phase 5 — Review edits to the scholarship wizard

Edits requested after review (2026-10-19). Scholarship flow only; the normal registration wizard is unchanged.

## Scope
1. **Marital status: add `Single` (أعزب).**
   - `marital_status` gets the option `Single` in `beneficiaries_registration.json`. Sanadi already maps it (`get_marital_status`: Single → 1).
   - The scholarship wizard offers it first; the normal wizard keeps its 4 options (variant `maritalStatuses`).
   - Server: a non-scholarship registration can't be saved with `Single` (`validate`), so the normal flow stays as it is.
   - `Single` adds no partner fields or partner documents (same as today's non-married statuses).
2. **Years of residence for Qatari applicants.** Not changed; recorded as OQ14 (see plan §7).
3. **Income, first option: the applicant's own income.** The scholarship wizard asks "هل لديك (دخل/راتب)؟" and uses the beneficiary wording for its sub-fields (آلية صرف دخل المستفيد / راتب المستفيد / ملاحظة دخل المستفيد), instead of the guardian wording from Phase 2. The field stays `ben_income` (Sanadi income type 1); father and mother income keep their own fields.
4. **Additional data: bank debts question.** In the scholarship wizard, `bank_loans` reads "هل لديك أو لدى رب الأسرة التزامات بنكية ومديونيات؟" (variant label key, also used in the validation popup). Same field and options.
5. **Step 5: two more required attachments.** New Attach fields on Beneficiary Request, shown and required for Education / Scholarship like the other 8:
   - `scholarship_mother_bank_statement` — كشف حساب الأم
   - `scholarship_student_bank_statement` — كشف حساب الطالب

   They join `SCHOLARSHIP_ATTACHMENT_FIELDS` (server and frontend), so both entry points (the wizard's step 5 and the request page's Scholarship option) require 10 documents.

## Files
- `beneficiaries_registration.json`, `beneficiaries_registration.py`
- `beneficiary_request.json`, `beneficiary_request.py`
- `frontend/src/components/registration/registrationVariant.js`, `registrationValidation.js`, `PersonalInfoCard.vue`, `AdditionalDataCard.vue`, `BeneficiaryRegistration.vue`
- `frontend/src/locales/translations.js`

## Tests
- **Backend:** a scholarship submission or an accepted user's Scholarship request missing either new statement → incomplete, nothing created; `Single` is accepted on a scholarship registration and sent to Sanadi as 1; a normal registration with `Single` is refused.
- **Vitest:** marital options per flow; the scholarship income and bank-debts labels; step 5 requires the 2 new documents; AR/EN keys.
- **Browser:** a scholarship Draft through steps 1–5 with `Single`, the new labels and 10 documents; the normal wizard still has no `Single`.

## Done when
The tests pass and the wizard has been walked through in the browser.
