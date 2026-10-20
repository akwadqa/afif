import {
  INCOME_SOURCES,
  OBLIGATION_FIELDS,
  SCHOLARSHIP_ATTACHMENT_FIELDS,
  SCHOLARSHIP_DECLARATION_FIELDS,
  getRegistrationVariant,
} from './registrationVariant'

const MINIMUM_AGE = 21

function isEmpty(value) {
  return value === undefined || value === null || value === ''
}

// Collects the popup messages and the highlighted fields of one step. A field the flow hides (the
// guardian mobile in the normal flow) is never required or checked.
class StepErrors {
  constructor(variant) {
    this.variant = variant
    this.errors = []
    this.fields = []
  }

  add(field, message) {
    this.errors.push(message)
    if (field) this.fields.push(field)
  }

  require(value, field, label) {
    if (this.variant.isShown(field) && isEmpty(value)) this.add(field, label)
  }

  reject(isInvalid, field, message) {
    if (this.variant.isShown(field) && isInvalid) this.add(field, message)
  }
}

/**
 * Validate one wizard step. `step` is the visible step (1-5); step 4 has two sub-steps:
 * 1 = additional data, 2 = registration attachments.
 */
export function validateRegistrationStep({ formData, step, subStep4, flow = 'registration', t }) {
  const check = new StepErrors(getRegistrationVariant(flow))

  if (step === 1) validatePersonalStep(check, formData, t)
  if (step === 2) validateIncomeStep(check, formData.incomeDetails, t)
  if (step === 3) validateObligationsStep(check, formData.financialObligations, t)
  if (step === 4 && subStep4 === 1) validateAdditionalDataStep(check, formData.additionalData, t)
  if (step === 4 && subStep4 === 2) validateAttachmentsStep(check, formData, t)
  if (step === 5) validateScholarshipRequestStep(check, formData, t)

  return { errors: check.errors, fields: check.fields }
}

export function getAge(dateOfBirth, today = new Date()) {
  const birthDate = new Date(dateOfBirth)
  let age = today.getFullYear() - birthDate.getFullYear()
  const monthDiff = today.getMonth() - birthDate.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) age--
  return age
}

function validatePersonalStep(check, formData, t) {
  validatePersonalInfo(check, formData.personalInfo, t)
  validateAdditionalInfo(check, formData.personalInfo, formData.additionalInfo, t)
  validateFamilyDetails(check, formData.personalInfo, formData.familyDetails, t)
}

function validatePersonalInfo(check, pi, t) {
  const isResidence = Boolean(pi.ben_nationality && pi.ben_nationality !== 'Qatar')

  check.require(pi.ar_name, 'ar_name', t('registration.personalInfo.arName'))
  check.reject(pi.ar_name && /[a-zA-Z]/.test(pi.ar_name), 'ar_name', t('registration.validation.arabicOnly'))
  check.require(pi.en_name, 'en_name', t('registration.personalInfo.enName'))
  check.reject(pi.en_name && /[؀-ۿ]/.test(pi.en_name), 'en_name', t('registration.validation.englishOnly'))
  check.require(pi.ben_primary_idtype, 'ben_primary_idtype', t('registration.personalInfo.primaryIdType'))
  check.require(pi.ben_primary_idnumber, 'ben_primary_idnumber', t('registration.personalInfo.primaryIdNumber'))
  check.reject(pi.ben_primary_idnumber && pi.ben_primary_idnumber.length !== 11, 'ben_primary_idnumber', t('registration.validation.idMustBe11'))
  check.require(pi.id_expiry_date, 'id_expiry_date', t('registration.personalInfo.idExpiryDate'))
  check.require(pi.passport_number, 'passport_number', t('registration.personalInfo.passportNumber'))
  check.reject(pi.passport_number && !/^[A-Z0-9]{1,12}$/.test(pi.passport_number), 'passport_number', t('registration.validation.passportFormat'))
  check.require(pi.ben_nationality, 'ben_nationality', t('registration.personalInfo.nationality'))
  check.require(pi.gender, 'gender', t('registration.personalInfo.gender'))
  check.require(pi.date_of_birth, 'date_of_birth', t('registration.personalInfo.dob'))
  check.reject(pi.date_of_birth && getAge(pi.date_of_birth) < MINIMUM_AGE, 'date_of_birth', t('registration.validation.minimumAge'))
  check.require(pi.phone_number, 'phone_number', t('registration.personalInfo.phone'))
  check.reject(pi.phone_number && pi.phone_number.length !== 8, 'phone_number', t('registration.validation.phoneMustBe8'))
  check.require(pi.guardian_mobile_number, 'guardian_mobile_number', t('scholarship.personalInfo.guardianMobile'))
  check.reject(pi.guardian_mobile_number && pi.guardian_mobile_number.length !== 8, 'guardian_mobile_number', t('registration.validation.phoneMustBe8'))
  // Single is offered only in the scholarship flow, and a single applicant may have no partner.
  if (pi.marital_status !== 'Single') check.require(pi.partners_phone_number, 'partners_phone_number', t('registration.personalInfo.partnerPhone'))
  check.reject(pi.partners_phone_number && pi.partners_phone_number.length !== 8, 'partners_phone_number', t('registration.validation.phoneMustBe8'))
  check.require(pi.marital_status, 'marital_status', t('registration.personalInfo.maritalStatus'))
  if (pi.marital_status === 'Married') check.require(pi.partner_name, 'partner_name', t('registration.personalInfo.partnerName'))
  if (pi.marital_status === 'Divorced' || pi.marital_status === 'Widowed') check.require(pi.expartner_name, 'expartner_name', t('registration.personalInfo.exPartnerName'))
  if (isResidence) check.require(pi.visa_type, 'visa_type', t('registration.personalInfo.visaType'))
  check.require(pi.residence_years, 'residence_years', t('registration.personalInfo.residenceYears'))
}

function validateAdditionalInfo(check, pi, ai, t) {
  const isResidence = Boolean(pi.ben_nationality && pi.ben_nationality !== 'Qatar')

  // The requestor sub-fields are not validated: ben_requestor_relationtype only allows
  // "The same subvention requestor".
  check.require(ai.ben_requestor_relationtype, 'ben_requestor_relationtype', t('registration.additionalInfo.requestorRelation'))
  check.require(ai.ben_sec_idtype, 'ben_sec_idtype', t('registration.additionalInfo.secIdType'))
  if (ai.ben_sec_idtype === 'Passport') check.require(ai.ben_sec_nationality, 'ben_sec_nationality', t('registration.additionalInfo.secNationality'))
  if (ai.ben_sec_idtype === 'GCC Id') check.require(ai.ben_sec_gulf_country, 'ben_sec_gulf_country', t('registration.additionalInfo.gulfCountry'))
  check.require(ai.currently_working, 'currently_working', t('registration.additionalInfo.currentlyWorking'))
  if (ai.currently_working === 'Yes') {
    check.require(ai.employer_name, 'employer_name', t('registration.additionalInfo.employerName'))
    check.require(ai.employer_address, 'employer_address', t('registration.additionalInfo.employerAddress'))
    check.require(ai.occupation, 'occupation', t('registration.additionalInfo.occupation'))
  }
  if (isResidence && ai.currently_working === 'No') check.require(ai.worked_before, 'worked_before', t('registration.additionalInfo.workedBefore'))
  check.require(ai.education_level, 'education_level', t('registration.additionalInfo.educationLevel'))
  if (pi.ben_nationality !== 'Qatar') check.require(ai.sponsor_name, 'sponsor_name', t('registration.additionalInfo.sponsorName'))
}

function validateFamilyDetails(check, pi, fd, t) {
  const isResidence = Boolean(pi.ben_nationality && pi.ben_nationality !== 'Qatar')

  check.require(fd.family_size, 'family_size', t('registration.familyDetails.familySize'))
  check.require(fd.ben_dependent_count, 'ben_dependent_count', t('registration.familyDetails.dependentCount'))
  check.require(fd.family_visa_type, 'family_visa_type', t('registration.familyDetails.familyVisa'))
  if (isResidence) {
    check.require(fd.visa_dependent, 'visa_dependent', t('registration.familyDetails.otherDependents'))
    if (fd.visa_dependent === 'Yes') check.require(fd.names_and_relation_to_sponsored, 'names_and_relation_to_sponsored', t('registration.familyDetails.namesRelation'))
  }
  check.require(fd.have_children, 'have_children', t('registration.familyDetails.haveChildren'))
  if (pi.marital_status === 'Married') check.require(fd.partner_working, 'partner_working', t('registration.familyDetails.partnerWorking'))
  if (fd.have_children === 'Yes') {
    check.require(fd.children_above_eighteen, 'children_above_eighteen', t('registration.familyDetails.childrenAbove18'))
    check.require(fd.children_in_school, 'children_in_school', t('registration.familyDetails.childrenInSchool'))
    if (fd.children_in_school === 'Yes') {
      check.require(fd.children_school, 'children_school', t('registration.familyDetails.childrenSchoolType'))
      check.require(fd.children_school_information, 'children_school_information', t('registration.familyDetails.childrenSchoolInfo'))
    }
    check.require(fd.children_special_needs, 'children_special_needs', t('registration.familyDetails.childrenSpecialNeeds'))
  }
  check.require(fd.afif_charity_assistance, 'afif_charity_assistance', t('registration.familyDetails.afifAssistance'))
  if (fd.afif_charity_assistance === 'Yes') check.require(fd.affif_assistance, 'affif_assistance', t('registration.familyDetails.afifAssistanceAmount'))
}

function validateIncomeStep(check, incomeDetails, t) {
  if (!INCOME_SOURCES.some(src => Number(incomeDetails[src.field]) === 1)) {
    check.add(null, t('registration.validation.atLeastOneIncome'))
  }
  for (const src of INCOME_SOURCES.filter(src => Number(incomeDetails[src.field]) === 1)) {
    check.require(incomeDetails[src.periodicField], src.periodicField, t(src.periodicLabelKey))
    check.require(incomeDetails[src.amountField], src.amountField, t(src.amountLabelKey))
    check.require(incomeDetails[src.noteField], src.noteField, t(src.noteLabelKey))
  }
}

function getObligationSubFields(t) {
  const label = key => t(`registration.financialObligations.${key}`)
  return {
    family_obligation: [
      { name: 'family_obligations_installments_count', label: label('familyInstallmentsLabel'), positive: true },
      { name: 'family_obligation_periodicity',         label: label('familyPeriodicLabel') },
      { name: 'family_expenses',                       label: label('familyAmountLabel') },
      { name: 'family_obligations_note',               label: label('familyNoteLabel') },
    ],
    rent_obligation: [
      { name: 'rent_obligation_periodicity',           label: label('rentPeriodicLabel') },
      { name: 'rent_obligations_installments_count',   label: label('rentInstallmentsLabel'), positive: true },
      { name: 'rent_amount',                           label: label('rentAmountLabel') },
      { name: 'rent_obligations_note',                 label: label('rentNoteLabel') },
    ],
    treatment_obligation: [
      { name: 'treatment_obligation_periodicity',          label: label('treatmentPeriodicLabel') },
      { name: 'treatment_obligation_installments_count',   label: label('treatmentInstallmentsLabel'), positive: true },
      { name: 'treatment_amount',                          label: label('treatmentAmountLabel') },
      { name: 'treatment_obligations_note',                label: label('treatmentNoteLabel') },
    ],
    debt_obligation: [
      { name: 'debt_obligation_periodicity',           label: label('debtPeriodicLabel') },
      { name: 'debt_obligations_installments_count',   label: label('debtInstallmentsLabel'), positive: true },
      { name: 'bank_payments_amount',                  label: label('debtAmountLabel') },
      { name: 'debt_obligations_note',                 label: label('debtNoteLabel') },
    ],
    tuition_obligation: [
      { name: 'tuition_obligation_periodicity',          label: label('tuitionPeriodicLabel') },
      { name: 'tuition_obligation_installments_count',   label: label('tuitionInstallmentsLabel'), positive: true },
      { name: 'tuition_obligations_note',                label: label('tuitionNoteLabel') },
      { name: 'tuition_amount',                          label: label('tuitionAmountLabel') },
    ],
  }
}

function validateObligationsStep(check, fo, t) {
  if (!OBLIGATION_FIELDS.some(field => Number(fo[field]) === 1)) {
    check.add(null, t('registration.validation.atLeastOneObligation'))
  }
  const subFields = getObligationSubFields(t)
  for (const field of OBLIGATION_FIELDS.filter(field => Number(fo[field]) === 1)) {
    for (const f of subFields[field]) {
      check.require(fo[f.name], f.name, f.label)
      check.reject(f.positive && !isEmpty(fo[f.name]) && Number(fo[f.name]) <= 0, f.name, t('registration.validation.mustBeGreaterThanZero'))
    }
  }
}

function validateAdditionalDataStep(check, ad, t) {
  check.require(ad.housing_type, 'housing_type', t('registration.additionalData.housingType'))
  check.require(ad.housing_city, 'housing_city', t('registration.additionalData.city'))
  check.require(ad.zone_number, 'zone_number', t('registration.additionalData.zoneNumber'))
  check.require(ad.street_number, 'street_number', t('registration.additionalData.streetNumber'))
  check.require(ad.unit_number, 'unit_number', t('registration.additionalData.unitNumber'))
  check.require(ad.building_number, 'building_number', t('registration.additionalData.buildingNumber'))
  check.require(ad.housing_description, 'housing_description', t('registration.additionalData.housingDescription'))
  check.require(ad.has_afif_employee_relation, 'has_afif_employee_relation', t('registration.additionalData.afifRelation'))
  check.require(ad.has_housemates, 'has_housemates', t('registration.additionalData.housemates'))
  check.require(ad.has_bank_loans, 'has_bank_loans', t('registration.additionalData.bankLoans'))
  if (ad.has_bank_loans === 'Yes') check.require(ad.court_tried, 'court_tried', t('registration.additionalData.courtTried'))
  check.require(ad.has_other_info, 'has_other_info', t('registration.additionalData.otherInfo'))
  if (ad.has_other_info === 'Yes') {
    check.require(ad.additional_notes, 'additional_notes', t('registration.additionalData.additionalNotes'))
    check.reject(ad.additional_notes && ad.additional_notes.length > 120, 'additional_notes', t('registration.validation.additionalInfoTooLong'))
  }
}

function getRequiredRegistrationDocs({ personalInfo: pi, additionalInfo: ai, familyDetails: fd, additionalData: ad }) {
  const isMarried       = pi.marital_status === 'Married'
  const isDivorced      = pi.marital_status === 'Divorced'
  const isWidowed       = pi.marital_status === 'Widowed'
  const isResidence     = pi.visa_type === 'Residence'
  const familyResidence = fd.family_visa_type === 'Residence'
  const childrenAbove18 = fd.children_above_eighteen === 'Yes'
  const notWorking      = ai.currently_working === 'No'

  return [
    { id: 'qid',                            labelKey: 'qid',                   show: true },
    { id: 'passport',                       labelKey: 'passport',              show: true },
    { id: 'wife_id',                        labelKey: 'wifeId',                show: isMarried },
    { id: 'wife_passport',                  labelKey: 'wifePassport',          show: isMarried },
    { id: 'children_identification',        labelKey: 'childrenId',            show: fd.have_children === 'Yes' },
    { id: 'rent_contract',                  labelKey: 'rentContract',          show: ad.housing_type === 'Rental' },
    { id: 'property_deed',                  labelKey: 'property',              show: ad.housing_type === 'Private Ownership' },
    { id: 'bank_statement',                 labelKey: 'bankStatement',         show: isResidence },
    { id: 'wife_bank_statement',            labelKey: 'wifeBankStatement',     show: isMarried && familyResidence },
    { id: 'wife_credit_certificate',        labelKey: 'wifeCredit',            show: isMarried && familyResidence },
    { id: 'beneficiary_credit_certificate', labelKey: 'creditBureau',          show: isResidence },
    { id: 'children_bank_statement',        labelKey: 'childrenBankStatement', show: familyResidence && childrenAbove18 },
    { id: 'children_credit_information',    labelKey: 'childrenCredit',        show: familyResidence && childrenAbove18 },
    { id: 'social_security_certificate',    labelKey: 'socialSecurityCert',    show: pi.ben_nationality === 'Qatar' && notWorking },
    { id: 'partner_work_certificate',       labelKey: 'partnerWorkCert',       show: fd.partner_working === 'Yes' },
    { id: 'employment_certificate',         labelKey: 'employmentCert',        show: ai.currently_working === 'Yes' },
    { id: 'vehicle_certificate',            labelKey: 'trafficCar',            show: isResidence },
    { id: 'iban_picture',                   labelKey: 'ibanPhoto',             show: isResidence },
    { id: 'children_schooling_proof',       labelKey: 'childrenSchoolProof',   show: fd.children_in_school === 'Yes' },
    { id: 'special_needs_certificate',      labelKey: 'specialNeedsCert',      show: fd.children_special_needs === 'Yes' },
    { id: 'termination_letter',             labelKey: 'terminationLetter',     show: notWorking && ai.worked_before === 'Yes' },
    { id: 'nonmarriage_proof',              labelKey: 'nonmarriageProof',      show: isDivorced || isWidowed },
    { id: 'divorce_paper',                  labelKey: 'divorcePaper',          show: isDivorced },
    { id: 'partner_death_certificate',      labelKey: 'partnerDeathCert',      show: isWidowed },
    { id: 'copy_of_court_judgment',         labelKey: 'courtJudgment',         show: ad.has_bank_loans === 'Yes' && ad.court_tried === 'Yes' },
    { id: 'id_coresidents',                 labelKey: 'coresidentsId',         show: ad.has_housemates === 'Yes' },
    { id: 'id_sponsored',                   labelKey: 'sponsoredId',           show: fd.visa_dependent === 'Yes' },
    { id: 'metrash_adress',                 labelKey: 'metrashAddress',        show: true },
  ].filter(doc => doc.show)
}

function validateAttachmentsStep(check, formData, t) {
  const { files, legalClaims } = formData.attachments
  for (const doc of getRequiredRegistrationDocs(formData)) {
    if (!files[doc.id]) check.add(`attach_${doc.id}`, t(`registration.attachments.docs.${doc.labelKey}`))
  }
  if (!legalClaims.correctData)       check.add('claim_correctData', 'الإقرار بصحة البيانات')
  if (!legalClaims.verificationRight) check.add('claim_verificationRight', 'الإقرار بحق التحقق من الأهلية')
  if (!legalClaims.statusAwareness)   check.add('claim_statusAwareness', 'الإقرار بطبيعة التسجيل')
}

// Step 5 shows the request data and the scholarship documents, which are saved on the registration.
function validateScholarshipRequestStep(check, { scholarshipRequest: sr, attachments }, t) {
  if (!(Number(sr.requested_amount) > 0)) check.add('requested_amount', t('scholarship.request.requestedAmount'))
  if (!sr.request_summary?.trim()) check.add('request_summary', t('scholarship.request.summary'))
  for (const id of SCHOLARSHIP_ATTACHMENT_FIELDS) {
    if (!attachments.files[id]) check.add(`attach_${id}`, t(`scholarship.attachments.${id}`))
  }
  for (const field of SCHOLARSHIP_DECLARATION_FIELDS) {
    if (!sr.declarations[field]) check.add(`claim_${field}`, t(`scholarship.declarations.${field}`))
  }
}
