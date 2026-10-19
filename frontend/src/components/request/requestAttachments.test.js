import { describe, expect, it } from 'vitest'
import translations from '@/locales/translations'
import { SCHOLARSHIP_ATTACHMENT_FIELDS } from '@/components/registration/registrationVariant'
import { REQUEST_ATTACHMENT_FIELDS, getRequiredRequestDocs, isScholarshipSubcategory } from './requestAttachments'

function lookup(language, key) {
  return key.split('.').reduce((node, part) => node?.[part], translations[language])
}

const ids = docs => docs.map(doc => doc.id)

describe('getRequiredRequestDocs', () => {
  it('requires all 8 scholarship documents for Education Assistance → Scholarship', () => {
    expect(ids(getRequiredRequestDocs('Education Assistance', 'Scholarship'))).toEqual(SCHOLARSHIP_ATTACHMENT_FIELDS)
  })

  it('labels the scholarship documents like step 5 of the scholarship wizard', () => {
    const labels = getRequiredRequestDocs('Education Assistance', 'Scholarship').map(doc => doc.labelKey)
    expect(labels).toEqual(SCHOLARSHIP_ATTACHMENT_FIELDS.map(id => `scholarship.attachments.${id}`))
  })

  it.each(['Tuition Fees', 'Other Educational Assistance', ''])(
    'keeps the 2 normal education documents for %j',
    subcategory => {
      expect(ids(getRequiredRequestDocs('Education Assistance', subcategory))).toEqual(['education_invoice', 'grade_transcript'])
    },
  )

  it('does not treat Scholarship under another category as a scholarship', () => {
    expect(isScholarshipSubcategory('Social Assistance', 'Scholarship')).toBe(false)
    expect(ids(getRequiredRequestDocs('Housing Assistance', 'Real estate purchase'))).toEqual(
      ['rent_contract', 'onwer_qid', 'late_letter', 'estate_pruchase'],
    )
  })

  it('lists every scholarship attachment for the read-only view', () => {
    for (const field of SCHOLARSHIP_ATTACHMENT_FIELDS) expect(REQUEST_ATTACHMENT_FIELDS).toContain(field)
    expect(new Set(REQUEST_ATTACHMENT_FIELDS).size).toBe(REQUEST_ATTACHMENT_FIELDS.length)
  })
})

describe('request translations', () => {
  const keys = [
    'request.subtypes.education.Scholarship',
    ...getRequiredRequestDocs('Education Assistance', 'Scholarship').map(doc => doc.labelKey),
    ...getRequiredRequestDocs('Education Assistance', 'Tuition Fees').map(doc => doc.labelKey),
    'scholarship.declarations.is_data_accuracy_declared',
    'scholarship.declarations.is_eligibility_check_accepted',
    'scholarship.blocked.submittedTitle',
    'scholarship.blocked.statusLabel',
    'scholarship.blocked.acceptedMessage',
    'scholarship.blocked.applyButton',
  ]

  it.each(['ar', 'en'])('has every key in %s', language => {
    expect(keys.filter(key => typeof lookup(language, key) !== 'string')).toEqual([])
  })
})
