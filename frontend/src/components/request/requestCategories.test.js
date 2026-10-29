import { describe, expect, it } from 'vitest'
import { SUBCATEGORY_MAP, getSubcategoryOptions } from './requestCategories'

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
