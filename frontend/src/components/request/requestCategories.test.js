import { describe, expect, it } from 'vitest'
import { SUBCATEGORY_FIELDS, SUBCATEGORY_MAP, getAssistanceTypeKey, getSubcategoryOptions } from './requestCategories'

describe('getSubcategoryOptions', () => {
  it('hides Scholarship from the normal request form', () => {
    const options = getSubcategoryOptions('Education Assistance', { includeScholarship: false })
    expect(options).not.toContain('Scholarship')
    expect(options).toContain('Tuition Fees')
  })

  it('lists Scholarship when showing an existing request', () => {
    expect(getSubcategoryOptions('Education Assistance', { includeScholarship: true })).toContain('Scholarship')
  })

  it('returns every option for a category that has no scholarship', () => {
    expect(getSubcategoryOptions('Medical Assistance', { includeScholarship: false })).toEqual(
      SUBCATEGORY_MAP['Medical Assistance'].options,
    )
  })

  it('returns nothing for an unknown category', () => {
    expect(getSubcategoryOptions('', { includeScholarship: true })).toEqual([])
  })
})

describe('getAssistanceTypeKey', () => {
  it('labels a scholarship row as the scholarship', () => {
    expect(getAssistanceTypeKey({ is_scholarship: 1, request_category: 'Education Assistance', educational_assistance: 'Scholarship' }))
      .toBe('sidebar.scholarship')
  })

  it('points at the sub-category translation of the row category', () => {
    expect(getAssistanceTypeKey({ request_category: 'Medical Assistance', medical_assistance: 'Medication' }))
      .toBe('request.subtypes.medical.Medication')
  })

  it('returns an empty key when the sub-category is empty', () => {
    expect(getAssistanceTypeKey({ request_category: 'Medical Assistance', medical_assistance: null })).toBe('')
  })

  it('returns an empty key for a category without sub-categories', () => {
    expect(getAssistanceTypeKey({ request_category: 'Akwad test category' })).toBe('')
  })

  it('exposes every sub-category field name', () => {
    expect(SUBCATEGORY_FIELDS).toEqual(Object.values(SUBCATEGORY_MAP).map(({ field }) => field))
  })
})
