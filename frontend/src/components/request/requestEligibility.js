// The request page and the scholarship page apply the same rules; before_insert_request enforces them.
const FINAL_STATUSES = ['Rejected by Supervisor', 'Rejected', 'Approved', 'Approved For Aid']

function addMonths(date, months) {
  const result = new Date(date)
  result.setMonth(result.getMonth() + months)
  return result
}

/**
 * Why the beneficiary cannot create a request now, or '' when they can.
 * `requests` is newest first; a scholarship student has no cooldowns, for any request, like before_insert_request; the reason is a key under myRequests.disabledReasons.
 */
export function getRequestBlockReason(requests, { isAccepted, isScholarship = false, isRestricted = false, now = new Date() }) {
  if (isRestricted) return 'restricted'
  if (!isAccepted) return 'notAccepted'

  const last = requests[0]
  if (!last) return ''
  if (!FINAL_STATUSES.includes(last.status)) return 'pending'
  if (isScholarship) return ''
  if (last.rejected_date && now < addMonths(last.rejected_date, 3)) return 'cooldownRejected'
  if (last.approved_for_aid_date && now < addMonths(last.approved_for_aid_date, 6)) return 'cooldownApproved'
  return ''
}
