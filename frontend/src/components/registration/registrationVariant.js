// Field layout of the registration wizard for each flow (spec/scholarship_flow/phase-6-registration-parity.md).
// The cards and the step validation both read it, so what is shown and what is required stay in sync.

// Mirrors SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS in beneficiary_request.py; all of them are required.
export const SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS = ['education_invoice', 'grade_transcript', 'student_id_copy', 'student_passport_copy']
// The scholarship documents the registration used to hold. Old records keep them, and the wizard
// must send them back unchanged because frappe.client.save clears every field missing from the payload.
export const LEGACY_SCHOLARSHIP_ATTACHMENT_FIELDS = [
  'scholarship_university_invoice',
  'scholarship_grade_transcript',
  'scholarship_guardian_id',
  'scholarship_guardian_passport',
  'scholarship_student_id',
  'scholarship_student_passport',
  'scholarship_family_ids',
  'scholarship_guardian_bank_statement',
  'scholarship_mother_bank_statement',
  'scholarship_student_bank_statement',
]
// Stored on the Beneficiary Request.
export const SCHOLARSHIP_DECLARATION_FIELDS = ['is_data_accuracy_declared', 'is_eligibility_check_accepted']

function incomeSource(field, periodicField, amountField, noteField, keys) {
  const prefix = 'registration.incomeDetails'
  return {
    field,
    periodicField,
    amountField,
    noteField,
    labelKey: `${prefix}.${keys.label}`,
    sectionTitleKey: `${prefix}.${keys.sectionTitle}`,
    periodicLabelKey: `${prefix}.${keys.periodic}`,
    amountLabelKey: `${prefix}.${keys.amount}`,
    noteLabelKey: `${prefix}.${keys.note}`,
  }
}

// The income card and the step validation both read this list.
export const INCOME_SOURCES = [
  incomeSource('ben_income', 'ben_periodic_type', 'salary_amount', 'benficiary_note',
    { label: 'benIncomeLabel', sectionTitle: 'benIncomeTitle', periodic: 'benPeriodicLabel', amount: 'salaryAmount', note: 'benNoteLabel' }),
  incomeSource('family_income', 'family_periodic_type', 'family_income_amount', 'family_note',
    { label: 'familyIncomeLabel', sectionTitle: 'familyIncomeTitle', periodic: 'familyPeriodicLabel', amount: 'familyAmount', note: 'familyNoteLabel' }),
  incomeSource('family_extra', 'extra_periodic_type', 'family_extra_salary', 'family_extra_note',
    { label: 'familyExtraLabel', sectionTitle: 'familyExtraTitle', periodic: 'extraPeriodicLabel', amount: 'extraAmount', note: 'extraNoteLabel' }),
  incomeSource('children_income', 'children_periodic_type', 'family_children_salary', 'children_note',
    { label: 'childrenIncomeLabel', sectionTitle: 'childrenIncomeTitle', periodic: 'childrenPeriodicLabel', amount: 'childrenAmount', note: 'childrenNoteLabel' }),
  incomeSource('private_income', 'private_business_periodicity', 'private_business_amount', 'private_note',
    { label: 'privateIncomeLabel', sectionTitle: 'privateIncomeTitle', periodic: 'privatePeriodicLabel', amount: 'privateAmount', note: 'privateNoteLabel' }),
  incomeSource('stock_income', 'stock_market_periodicity', 'stock_market_income', 'stock_market_note',
    { label: 'stockIncomeLabel', sectionTitle: 'stockIncomeTitle', periodic: 'stockPeriodicLabel', amount: 'stockAmount', note: 'stockNoteLabel' }),
  incomeSource('rent_income', 'rent_periodic_type', 'rent_income_amount', 'rent_note',
    { label: 'rentIncomeLabel', sectionTitle: 'rentIncomeTitle', periodic: 'rentPeriodicLabel', amount: 'rentAmount', note: 'rentNoteLabel' }),
]

export const OBLIGATION_FIELDS = ['family_obligation', 'rent_obligation', 'treatment_obligation', 'debt_obligation', 'tuition_obligation']

const MARITAL_STATUSES = ['Married', 'Divorced', 'Widowed', 'Separated']

// The scholarship wizard has every field of the normal one, plus the guardian mobile. Its documents
// are collected with the request instead of the registration, until "Update Required" asks for the
// normal registration documents.
const REGISTRATION_VARIANT = {
  hiddenFields: new Set(['guardian_mobile_number']),
  maritalStatuses: MARITAL_STATUSES,
  hasRegistrationDocuments: true,
}

const SCHOLARSHIP_VARIANT = {
  // A scholarship applicant is always Single, so there is no partner to contact.
  hiddenFields: new Set(['partners_phone_number']),
  // The server refuses Single on a normal registration and requires it on a scholarship one.
  maritalStatuses: ['Single'],
  hasRegistrationDocuments: false,
}

export function getRegistrationVariant(flow, { hasBeenUpdateRequired = false } = {}) {
  const variant = flow === 'scholarship' ? SCHOLARSHIP_VARIANT : REGISTRATION_VARIANT
  return {
    ...variant,
    hasRegistrationDocuments: variant.hasRegistrationDocuments || hasBeenUpdateRequired,
    isShown: field => !variant.hiddenFields.has(field),
  }
}
