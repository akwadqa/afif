import { ref, computed } from 'vue'
import { createResource } from 'frappe-ui'
import { session } from '@/data/session'
import { useLanguage } from './useLanguage'

const beneficiary = ref(null)

const resource = createResource({
  url: 'frappe.client.get_list',
  onSuccess(rows) {
    beneficiary.value = rows.length ? rows[0] : null
  },
})

let fetched = false

export function useBeneficiaryName() {
  const { currentLang } = useLanguage()

  if (!fetched && session.user) {
    fetched = true
    resource.submit({
      doctype: 'Beneficiaries Registration',
      filters: { user: session.user },
      fields: ['ar_name', 'en_name'],
      limit_page_length: 1,
    })
  }

  const displayName = computed(() => {
    const data = beneficiary.value
    if (data) {
      const name = currentLang.value === 'ar' ? data.ar_name : data.en_name
      if (name) return name
    }
    const user = session.user
    if (!user) return ''
    return user.includes('@') ? user.split('@')[0] : user
  })

  return { displayName }
}
