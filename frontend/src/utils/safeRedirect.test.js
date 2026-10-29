import { describe, expect, it } from 'vitest'
import { getSafeRedirect } from './safeRedirect'

describe('getSafeRedirect', () => {
  it.each([
    ['/scholarship', '/scholarship'],
    ['/scholarship?x=1', '/scholarship?x=1'],
  ])('keeps %s', (value, expected) => {
    expect(getSafeRedirect(value)).toBe(expected)
  })

  it.each([
    undefined,
    '',
    'scholarship',
    '//evil.com',
    '/\\evil.com',
    'https://evil.com',
    '/signin',
    '/signin?redirect=/a',
    '/register',
    '/forgot-password',
    ['/a'],
  ])('falls back for %j', (value) => {
    expect(getSafeRedirect(value)).toBe('/beneficiary-profile')
  })

  it('uses a custom fallback', () => {
    expect(getSafeRedirect('//evil.com', '/x')).toBe('/x')
  })
})
