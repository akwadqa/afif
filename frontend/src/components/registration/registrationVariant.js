// Field layout of the registration wizard for each flow (spec/scholarship_flow/plan.md §3).
// The cards and the step validation both read it, so what is shown and what is required stay in sync.

// Mirrors the server lists in beneficiary_request.py; all of them are required.
export const SCHOLARSHIP_ATTACHMENT_FIELDS = [
  'education_invoice',
  'grade_transcript',
  'scholarship_guardian_id',
  'scholarship_guardian_passport',
  'scholarship_student_id',
  'scholarship_student_passport',
  'scholarship_family_ids',
  'scholarship_guardian_bank_statement',
]
export const SCHOLARSHIP_DECLARATION_FIELDS = ['is_data_accuracy_declared', 'is_eligibility_check_accepted']

const REGISTRATION_INCOME = 'registration.incomeDetails'
const SCHOLARSHIP_INCOME = 'scholarship.incomeDetails'

function incomeSource(field, periodicField, amountField, noteField, keys, prefix = REGISTRATION_INCOME) {
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

const INCOME = {
  ben_income: incomeSource('ben_income', 'ben_periodic_type', 'salary_amount', 'benficiary_note',
    { label: 'benIncomeLabel', sectionTitle: 'benIncomeTitle', periodic: 'benPeriodicLabel', amount: 'salaryAmount', note: 'benNoteLabel' }),
  family_income: incomeSource('family_income', 'family_periodic_type', 'family_income_amount', 'family_note',
    { label: 'familyIncomeLabel', sectionTitle: 'familyIncomeTitle', periodic: 'familyPeriodicLabel', amount: 'familyAmount', note: 'familyNoteLabel' }),
  family_extra: incomeSource('family_extra', 'extra_periodic_type', 'family_extra_salary', 'family_extra_note',
    { label: 'familyExtraLabel', sectionTitle: 'familyExtraTitle', periodic: 'extraPeriodicLabel', amount: 'extraAmount', note: 'extraNoteLabel' }),
  children_income: incomeSource('children_income', 'children_periodic_type', 'family_children_salary', 'children_note',
    { label: 'childrenIncomeLabel', sectionTitle: 'childrenIncomeTitle', periodic: 'childrenPeriodicLabel', amount: 'childrenAmount', note: 'childrenNoteLabel' }),
  private_income: incomeSource('private_income', 'private_business_periodicity', 'private_business_amount', 'private_note',
    { label: 'privateIncomeLabel', sectionTitle: 'privateIncomeTitle', periodic: 'privatePeriodicLabel', amount: 'privateAmount', note: 'privateNoteLabel' }),
  stock_income: incomeSource('stock_income', 'stock_market_periodicity', 'stock_market_income', 'stock_market_note',
    { label: 'stockIncomeLabel', sectionTitle: 'stockIncomeTitle', periodic: 'stockPeriodicLabel', amount: 'stockAmount', note: 'stockNoteLabel' }),
  rent_income: incomeSource('rent_income', 'rent_periodic_type', 'rent_income_amount', 'rent_note',
    { label: 'rentIncomeLabel', sectionTitle: 'rentIncomeTitle', periodic: 'rentPeriodicLabel', amount: 'rentAmount', note: 'rentNoteLabel' }),
}

const SCHOLARSHIP_ONLY_INCOME = {
  father_income: incomeSource('father_income', 'father_income_periodicity', 'father_income_amount', 'father_income_note',
    { label: 'fatherIncomeLabel', sectionTitle: 'fatherIncomeTitle', periodic: 'fatherPeriodicLabel', amount: 'fatherAmount', note: 'fatherNoteLabel' },
    SCHOLARSHIP_INCOME),
  mother_income: incomeSource('mother_income', 'mother_income_periodicity', 'mother_income_amount', 'mother_income_note',
    { label: 'motherIncomeLabel', sectionTitle: 'motherIncomeTitle', periodic: 'motherPeriodicLabel', amount: 'motherAmount', note: 'motherNoteLabel' },
    SCHOLARSHIP_INCOME),
}

export const OBLIGATION_FIELDS = ['family_obligation', 'rent_obligation', 'treatment_obligation', 'debt_obligation', 'tuition_obligation']

const OBLIGATION_LABEL_KEYS = {
  family_obligation: 'familyLabel',
  rent_obligation: 'rentLabel',
  treatment_obligation: 'treatmentLabel',
  debt_obligation: 'debtLabel',
  tuition_obligation: 'tuitionLabel',
}

const REGISTRATION_VARIANT = {
  hiddenFields: new Set(['guardian_mobile_number']),
  incomeSources: Object.values(INCOME),
  obligationLabelKeys: Object.fromEntries(
    OBLIGATION_FIELDS.map(field => [field, `registration.financialObligations.${OBLIGATION_LABEL_KEYS[field]}`]),
  ),
}

const SCHOLARSHIP_VARIANT = {
  hiddenFields: new Set([
    'passport_number', 'id_expiry_date', 'partners_phone_number',
    'ben_sec_idtype', 'ben_sec_nationality', 'ben_sec_gulf_country',
    'worked_before',
    'family_visa_type', 'visa_dependent', 'names_and_relation_to_sponsored',
    'have_children', 'children_above_eighteen', 'children_in_school', 'children_school',
    'children_school_information', 'children_special_needs',
    'afif_charity_assistance', 'affif_assistance',
  ]),
  incomeSources: [
    {
      ...INCOME.ben_income,
      labelKey: `${SCHOLARSHIP_INCOME}.benIncomeLabel`,
      sectionTitleKey: `${SCHOLARSHIP_INCOME}.benIncomeTitle`,
      periodicLabelKey: `${SCHOLARSHIP_INCOME}.benPeriodicLabel`,
      amountLabelKey: `${SCHOLARSHIP_INCOME}.salaryAmount`,
      noteLabelKey: `${SCHOLARSHIP_INCOME}.benNoteLabel`,
    },
    SCHOLARSHIP_ONLY_INCOME.father_income,
    SCHOLARSHIP_ONLY_INCOME.mother_income,
    { ...INCOME.private_income, labelKey: `${SCHOLARSHIP_INCOME}.privateIncomeLabel` },
    INCOME.stock_income,
  ],
  obligationLabelKeys: Object.fromEntries(
    OBLIGATION_FIELDS.map(field => [field, `scholarship.financialObligations.${OBLIGATION_LABEL_KEYS[field]}`]),
  ),
}

export function getRegistrationVariant(flow) {
  const variant = flow === 'scholarship' ? SCHOLARSHIP_VARIANT : REGISTRATION_VARIANT
  return {
    ...variant,
    isShown: field => !variant.hiddenFields.has(field),
  }
}
