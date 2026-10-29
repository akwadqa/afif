import { describe, expect, it } from 'vitest'
import translations from '@/locales/translations'
import { REQUEST_ATTACHMENT_FIELDS, getRequiredRequestDocs, isScholarshipSubcategory } from './requestAttachments'

function lookup(language, key) {
  return key.split('.').reduce((node, part) => node?.[part], translations[language])
}

const ids = docs => docs.map(doc => doc.id)

describe('getRequiredRequestDocs', () => {
  it('lists the 4 student documents for a scholarship request, so its read-only view shows them', () => {
    const docs = getRequiredRequestDocs('Education Assistance', 'Scholarship')
    const scholarshipIds = ['education_invoice', 'grade_transcript', 'student_id_copy', 'student_passport_copy']

    expect(ids(docs)).toEqual(scholarshipIds)
    expect(scholarshipIds.filter(id => !REQUEST_ATTACHMENT_FIELDS.includes(id))).toEqual([])
    for (const language of ['ar', 'en']) {
      expect(docs.filter(doc => typeof lookup(language, doc.labelKey) !== 'string')).toEqual([])
    }
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
})

describe('request translations', () => {
  // Shown when an existing scholarship request is viewed.
  const keys = [
    'request.subtypes.education.Scholarship',
    'scholarship.declarations.is_data_accuracy_declared',
    'scholarship.declarations.is_eligibility_check_accepted',
  ]

  it.each(['ar', 'en'])('has every key in %s', language => {
    expect(keys.filter(key => typeof lookup(language, key) !== 'string')).toEqual([])
  })
})
