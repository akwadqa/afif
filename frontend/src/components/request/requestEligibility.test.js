import { describe, expect, it } from 'vitest'
import translations from '@/locales/translations'
import { getRequestBlockReason } from './requestEligibility'

const now = new Date('2026-10-20T12:00:00')
const accepted = { isAccepted: true, now }

describe('getRequestBlockReason', () => {
  it('allows the first request of an accepted beneficiary', () => {
    expect(getRequestBlockReason([], accepted)).toBe('')
  })

  it('blocks a beneficiary who is not accepted, even with no requests', () => {
    expect(getRequestBlockReason([], { isAccepted: false, now })).toBe('notAccepted')
  })

  it('blocks while the last request is open', () => {
    expect(getRequestBlockReason([{ status: 'Pending Supervisor Approval' }], accepted)).toBe('pending')
  })

  it.each([
    ['rejected 2 months ago', { status: 'Rejected', rejected_date: '2026-08-20' }, 'cooldownRejected'],
    ['rejected 4 months ago', { status: 'Rejected', rejected_date: '2026-06-19' }, ''],
    ['approved for aid 5 months ago', { status: 'Approved For Aid', approved_for_aid_date: '2026-05-21' }, 'cooldownApproved'],
    ['approved for aid 7 months ago', { status: 'Approved For Aid', approved_for_aid_date: '2026-03-19' }, ''],
  ])('applies the cooldown when the last request was %s', (_case, last, reason) => {
    expect(getRequestBlockReason([last, { status: 'Pending Supervisor Approval' }], accepted)).toBe(reason)
  })

  it.each([
    ['rejected', { status: 'Rejected', rejected_date: '2026-10-19' }],
    ['approved for aid', { status: 'Approved For Aid', approved_for_aid_date: '2026-10-19' }],
  ])('ignores the cooldowns for a scholarship request last %s yesterday', (_case, last) => {
    expect(getRequestBlockReason([last], { ...accepted, isScholarship: true })).toBe('')
  })

  it('still blocks a scholarship request while one is pending', () => {
    const pending = [{ status: 'Pending Supervisor Approval' }]
    expect(getRequestBlockReason(pending, { ...accepted, isScholarship: true })).toBe('pending')
  })

  it.each(['ar', 'en'])('has a message in %s for every reason', language => {
    const reasons = ['notAccepted', 'pending', 'cooldownRejected', 'cooldownApproved']
    expect(reasons.filter(reason => typeof translations[language].myRequests.disabledReasons[reason] !== 'string')).toEqual([])
  })
})
