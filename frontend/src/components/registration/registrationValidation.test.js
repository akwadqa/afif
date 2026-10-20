import { describe, expect, it } from 'vitest'
import translations from '@/locales/translations'
import {
  INCOME_SOURCES,
  SCHOLARSHIP_ATTACHMENT_FIELDS,
  SCHOLARSHIP_DECLARATION_FIELDS,
  getRegistrationVariant,
} from './registrationVariant'
import { validateRegistrationStep } from './registrationValidation'

function lookup(language, key) {
  return key.split('.').reduce((node, part) => node?.[part], translations[language])
}

const t = key => lookup('ar', key) ?? key

// The fields Phases 2-5 hid in the scholarship wizard; Phase 6 brings them back.
const FORMERLY_HIDDEN_STEP_1_FIELDS = [
  'id_expiry_date', 'partners_phone_number',
  'family_visa_type', 'have_children', 'afif_charity_assistance',
]

// Step 1 without the fields Phases 2-5 hid.
function makeScholarshipStep1() {
  return {
    personalInfo: {
      ar_name: 'طالب المنحة',
      en_name: 'Scholarship Student',
      ben_primary_idtype: 'Qatari Id',
      ben_primary_idnumber: '28763400001',
      passport_number: 'A1234567',
      ben_nationality: 'Qatar',
      gender: 'Male',
      date_of_birth: '1990-01-01',
      phone_number: '55123456',
      guardian_mobile_number: '55654321',
      marital_status: 'Separated',
      visa_type: 'Residence',
      residence_years: '10',
    },
    additionalInfo: {
      ben_requestor_relationtype: 'The same subvention requestor',
      ben_sec_idtype: 'Passport',
      ben_sec_nationality: 'Qatar',
      currently_working: 'No',
      education_level: 'High Education Level',
    },
    familyDetails: { family_size: '4', ben_dependent_count: '0' },
  }
}

function validate(formData, step, flow, subStep4) {
  return validateRegistrationStep({ formData, step, subStep4, flow, t })
}

function fillFormerlyHiddenFields(formData) {
  Object.assign(formData.personalInfo, { id_expiry_date: '2030-01-01', partners_phone_number: '55111222' })
  Object.assign(formData.familyDetails, { family_visa_type: 'Residence', have_children: 'No', afif_charity_assistance: 'No' })
  return formData
}

describe('step 1 (personal data)', () => {
  it.each(['scholarship', 'registration'])('requires every normal field in the %s flow', flow => {
    const { fields } = validate(makeScholarshipStep1(), 1, flow)

    expect(fields).toEqual(FORMERLY_HIDDEN_STEP_1_FIELDS)
  })

  it.each(['scholarship', 'registration'])('passes in the %s flow once they are filled in', flow => {
    expect(validate(fillFormerlyHiddenFields(makeScholarshipStep1()), 1, flow)).toEqual({ errors: [], fields: [] })
  })

  it('requires an 8-digit guardian mobile number only in scholarship mode', () => {
    const missing = fillFormerlyHiddenFields(makeScholarshipStep1())
    missing.personalInfo.guardian_mobile_number = ''
    const tooShort = fillFormerlyHiddenFields(makeScholarshipStep1())
    tooShort.personalInfo.guardian_mobile_number = '5512'

    expect(validate(missing, 1, 'scholarship').fields).toEqual(['guardian_mobile_number'])
    expect(validate(tooShort, 1, 'scholarship').fields).toEqual(['guardian_mobile_number'])
    expect(validate(missing, 1, 'registration').fields).not.toContain('guardian_mobile_number')
  })
})

describe('step 2 (income)', () => {
  it.each(['scholarship', 'registration'])('offers the normal income sources in the %s flow', flow => {
    const { errors } = validate({ incomeDetails: { family_income: 1 } }, 2, flow)

    expect(errors).toEqual([
      t('registration.incomeDetails.familyPeriodicLabel'),
      t('registration.incomeDetails.familyAmount'),
      t('registration.incomeDetails.familyNoteLabel'),
    ])
  })

  it('no longer has the father and mother incomes', () => {
    expect(INCOME_SOURCES.map(src => src.field)).toEqual([
      'ben_income', 'family_income', 'family_extra', 'children_income', 'private_income', 'stock_income', 'rent_income',
    ])
    expect(validate({ incomeDetails: { father_income: 1 } }, 2, 'scholarship').errors).toEqual([
      t('registration.validation.atLeastOneIncome'),
    ])
  })
})

describe('marital status options', () => {
  it('offers Single only in the scholarship flow', () => {
    expect(getRegistrationVariant('scholarship').maritalStatuses).toEqual(['Single', 'Married', 'Divorced', 'Widowed', 'Separated'])
    expect(getRegistrationVariant('registration').maritalStatuses).not.toContain('Single')
  })

  it('needs no partner details for a single applicant', () => {
    const formData = fillFormerlyHiddenFields(makeScholarshipStep1())
    formData.personalInfo.marital_status = 'Single'
    formData.personalInfo.partners_phone_number = ''

    expect(validate(formData, 1, 'scholarship')).toEqual({ errors: [], fields: [] })
  })

  it.each(['Married', 'Divorced', 'Widowed', 'Separated'])('still requires the partner phone when %s', status => {
    const formData = fillFormerlyHiddenFields(makeScholarshipStep1())
    Object.assign(formData.personalInfo, { marital_status: status, partners_phone_number: '' })

    expect(validate(formData, 1, 'scholarship').fields).toContain('partners_phone_number')
  })

  it('still checks the format of a partner phone given by a single applicant', () => {
    const formData = fillFormerlyHiddenFields(makeScholarshipStep1())
    Object.assign(formData.personalInfo, { marital_status: 'Single', partners_phone_number: '5511' })

    expect(validate(formData, 1, 'scholarship').fields).toEqual(['partners_phone_number'])
  })
})

describe('step 4 (additional data)', () => {
  it.each(['scholarship', 'registration'])('uses the normal bank debts question in the %s flow', flow => {
    expect(validate({ additionalData: {} }, 4, flow, 1).errors).toContain('هل لديك قروض بنكية ومديونيات؟')
  })
})

describe('step 4 (registration attachments)', () => {
  it('requires the same documents in both flows', () => {
    const formData = {
      ...fillFormerlyHiddenFields(makeScholarshipStep1()),
      familyDetails: { family_visa_type: 'Residence', have_children: 'Yes', visa_dependent: 'Yes' },
      additionalData: { housing_type: 'Government' },
      attachments: { files: {}, legalClaims: { correctData: true, verificationRight: true, statusAwareness: true } },
    }

    const scholarship = validate(formData, 4, 'scholarship', 2).fields
    expect(scholarship).toEqual(validate(formData, 4, 'registration', 2).fields)
    expect(scholarship).toEqual(expect.arrayContaining(['attach_children_identification', 'attach_id_sponsored']))
  })
})

describe('step 5 (scholarship request data)', () => {
  // The documents are registration fields, kept with the other registration files.
  const completeRequest = () => ({
    scholarshipRequest: {
      requested_amount: '20000',
      request_summary: 'Tuition for the next semester',
      declarations: Object.fromEntries(SCHOLARSHIP_DECLARATION_FIELDS.map(field => [field, true])),
    },
    attachments: {
      files: Object.fromEntries(SCHOLARSHIP_ATTACHMENT_FIELDS.map(id => [id, `/private/files/${id}.pdf`])),
    },
  })

  it('passes when everything is filled in', () => {
    expect(validate(completeRequest(), 5, 'scholarship')).toEqual({ errors: [], fields: [] })
  })

  it('requires every scholarship document from the registration files', () => {
    const formData = completeRequest()
    formData.attachments.files.scholarship_university_invoice = null
    formData.attachments.files.scholarship_student_bank_statement = undefined

    expect(validate(formData, 5, 'scholarship').errors).toEqual(['فاتورة الجامعة', 'كشف حساب الطالب'])
  })

  it('requires the request summary', () => {
    for (const summary of ['', '   ']) {
      const formData = completeRequest()
      formData.scholarshipRequest.request_summary = summary

      expect(validate(formData, 5, 'scholarship').fields).toEqual(['request_summary'])
    }
  })
})

describe('scholarship translations', () => {
  const keys = [
    ...INCOME_SOURCES.flatMap(src => [src.labelKey, src.sectionTitleKey, src.periodicLabelKey, src.amountLabelKey, src.noteLabelKey]),
    ...getRegistrationVariant('scholarship').maritalStatuses.map(status => `registration.personalInfo.${status.toLowerCase()}`),
    ...SCHOLARSHIP_ATTACHMENT_FIELDS.map(id => `scholarship.attachments.${id}`),
    'scholarship.acceptedSubtitle',
    'scholarship.success.acceptedMessage',
    'scholarship.applyAgain',
    'scholarship.request.status',
  ]

  it.each(['ar', 'en'])('has every label key in %s', language => {
    expect(keys.filter(key => typeof lookup(language, key) !== 'string')).toEqual([])
  })
})
