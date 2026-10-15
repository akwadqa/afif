import { arabicToWestern } from './inputHelpers'

// Mirrors Donation.normalize_mobile on the backend: 8 digits starting with 3, 5, 6 or 7,
// optionally prefixed with +974 / 00974
const QATAR_MOBILE = /^[3567]\d{7}$/
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function normalizeMobile(value) {
  const digits = arabicToWestern(value || '').replace(/[\s-]/g, '')
  return digits.replace(/^(\+|00)974/, '')
}

// Returns the translation key of the first problem, or '' when the donor details are valid.
// Benefactor donations may leave fields empty, but anything entered must still be valid.
export function validateDonor({ isAnonymous, fullName, phone, email }) {
  const name = (fullName || '').trim()
  const mobile = normalizeMobile(phone)
  const mail = (email || '').trim()

  if (!isAnonymous && (!name || !mobile || !mail)) return 'donation.donorRequired'
  if (mobile && !QATAR_MOBILE.test(mobile)) return 'donation.donorPhoneInvalid'
  if (mail && !EMAIL.test(mail)) return 'donation.donorEmailInvalid'
  return ''
}

// Payload fields for afif.donation_api.create_donation
export function donorPayload({ isAnonymous, fullName, phone, email }) {
  return {
    is_anonymous: isAnonymous ? 1 : 0,
    donor_name: (fullName || '').trim() || null,
    donor_mobile: normalizeMobile(phone) || null,
    donor_email: (email || '').trim() || null,
  }
}
