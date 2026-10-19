import { describe, expect, it } from 'vitest'
import translations from '@/locales/translations'
import { SCHOLARSHIP_ATTACHMENT_FIELDS, SCHOLARSHIP_DECLARATION_FIELDS, getRegistrationVariant } from './registrationVariant'
import { validateRegistrationStep } from './registrationValidation'

function lookup(language, key) {
  return key.split('.').reduce((node, part) => node?.[part], translations[language])
}

const t = key => lookup('ar', key) ?? key

const SCHOLARSHIP_HIDDEN_STEP_1_FIELDS = [
  'passport_number', 'id_expiry_date', 'partners_phone_number', 'ben_sec_nationality',
  'family_visa_type', 'have_children', 'afif_charity_assistance',
]

// Step 1 filled in the way the scholarship wizard leaves it: the hidden fields are empty.
function makeScholarshipStep1() {
  return {
    personalInfo: {
      ar_name: 'طالب المنحة',
      en_name: 'Scholarship Student',
      ben_primary_idtype: 'Qatari Id',
      ben_primary_idnumber: '28763400001',
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
      currently_working: 'No',
      education_level: 'High Education Level',
    },
    familyDetails: { family_size: '4', ben_dependent_count: '0' },
  }
}

function validate(formData, step, flow, subStep4) {
  return validateRegistrationStep({ formData, step, subStep4, flow, t })
}

describe('step 1 (personal data)', () => {
  it('passes in scholarship mode with the hidden fields empty', () => {
    expect(validate(makeScholarshipStep1(), 1, 'scholarship')).toEqual({ errors: [], fields: [] })
  })

  it('still requires the hidden fields in normal mode', () => {
    const { fields } = validate(makeScholarshipStep1(), 1, 'registration')

    expect(fields).toEqual(expect.arrayContaining(SCHOLARSHIP_HIDDEN_STEP_1_FIELDS))
  })

  it('requires an 8-digit guardian mobile number only in scholarship mode', () => {
    const missing = makeScholarshipStep1()
    missing.personalInfo.guardian_mobile_number = ''
    const tooShort = makeScholarshipStep1()
    tooShort.personalInfo.guardian_mobile_number = '5512'

    expect(validate(missing, 1, 'scholarship').fields).toEqual(['guardian_mobile_number'])
    expect(validate(tooShort, 1, 'scholarship').fields).toEqual(['guardian_mobile_number'])
    expect(validate(missing, 1, 'registration').fields).not.toContain('guardian_mobile_number')
  })

  it('accepts the normal flow once the hidden fields are filled in', () => {
    const formData = makeScholarshipStep1()
    Object.assign(formData.personalInfo, {
      passport_number: 'A1234567',
      id_expiry_date: '2030-01-01',
      partners_phone_number: '55111222',
    })
    formData.additionalInfo.ben_sec_nationality = 'Qatar'
    Object.assign(formData.familyDetails, { family_visa_type: 'Residence', have_children: 'No', afif_charity_assistance: 'No' })

    expect(validate(formData, 1, 'registration')).toEqual({ errors: [], fields: [] })
  })
})

describe('step 2 (income)', () => {
  it('requires the details of a checked parent income in scholarship mode', () => {
    const { fields } = validate({ incomeDetails: { father_income: 1 } }, 2, 'scholarship')

    expect(fields).toEqual(['father_income_periodicity', 'father_income_amount', 'father_income_note'])
  })

  it('does not count incomes the flow hides', () => {
    const scholarship = validate({ incomeDetails: { family_income: 1 } }, 2, 'scholarship')
    const normal = validate({ incomeDetails: { father_income: 1 } }, 2, 'registration')

    expect(scholarship.errors).toEqual([t('registration.validation.atLeastOneIncome')])
    expect(normal.errors).toEqual([t('registration.validation.atLeastOneIncome')])
  })

  it('uses the scholarship labels in the error popup', () => {
    const { errors } = validate({ incomeDetails: { ben_income: 1 } }, 2, 'scholarship')

    expect(errors).toContain('راتب ولي الأمر')
  })
})

describe('step 4 (registration attachments)', () => {
  it('does not require documents that only hidden fields can trigger', () => {
    const formData = {
      ...makeScholarshipStep1(),
      additionalData: { housing_type: 'Government' },
      attachments: {
        files: { qid: '/f/qid.pdf', passport: '/f/p.pdf', metrash_adress: '/f/m.pdf', bank_statement: '/f/b.pdf',
          beneficiary_credit_certificate: '/f/c.pdf', vehicle_certificate: '/f/v.pdf', iban_picture: '/f/i.pdf',
          social_security_certificate: '/f/s.pdf' },
        legalClaims: { correctData: true, verificationRight: true, statusAwareness: true },
      },
    }

    expect(validate(formData, 4, 'scholarship', 2)).toEqual({ errors: [], fields: [] })
  })
})

describe('step 5 (scholarship request data)', () => {
  const completeRequest = () => ({
    scholarshipRequest: {
      requested_amount: '20000',
      request_summary: 'Tuition for the next semester',
      files: Object.fromEntries(SCHOLARSHIP_ATTACHMENT_FIELDS.map(id => [id, `/private/files/${id}.pdf`])),
      declarations: Object.fromEntries(SCHOLARSHIP_DECLARATION_FIELDS.map(field => [field, true])),
    },
  })

  it('passes when everything is filled in', () => {
    expect(validate(completeRequest(), 5, 'scholarship')).toEqual({ errors: [], fields: [] })
  })

  it('requires the request summary', () => {
    for (const summary of ['', '   ']) {
      const formData = completeRequest()
      formData.scholarshipRequest.request_summary = summary

      expect(validate(formData, 5, 'scholarship').fields).toEqual(['request_summary'])
    }
  })
})

describe('variant translations', () => {
  const keys = ['registration', 'scholarship'].flatMap(flow => {
    const variant = getRegistrationVariant(flow)
    return [
      ...variant.incomeSources.flatMap(src => [src.labelKey, src.sectionTitleKey, src.periodicLabelKey, src.amountLabelKey, src.noteLabelKey]),
      ...Object.values(variant.obligationLabelKeys),
    ]
  })

  it.each(['ar', 'en'])('has every label key in %s', language => {
    expect(keys.filter(key => typeof lookup(language, key) !== 'string')).toEqual([])
  })
})
