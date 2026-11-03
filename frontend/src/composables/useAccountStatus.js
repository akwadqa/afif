import { computed } from 'vue'
import { createResource } from 'frappe-ui'

// gen_response puts its payload under `data`, which frappe-ui's default fetcher drops (it keeps `message`).
async function fetchResponseData({ url }) {
  const response = await fetch(`/api/method/${url}`, { headers: { Accept: 'application/json' } })
  if (!response.ok) throw new Error(`${url} failed with ${response.status}`)
  return (await response.json()).data
}

export function useAccountStatus() {
  const accountStatus = createResource({
    url: 'afif.api.scholarship.get_account_status',
    resourceFetcher: fetchResponseData,
    auto: true,
  })

  const isRestricted = computed(() => Boolean(accountStatus.data?.is_account_restricted))

  return { isRestricted }
}
