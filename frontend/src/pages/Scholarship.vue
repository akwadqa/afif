<template>
  <!-- Loading -->
  <div v-if="view === 'loading'" class="min-h-screen flex items-center justify-center">
    <svg class="animate-spin w-8 h-8 text-[#34B0EE]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
    </svg>
  </div>

  <!-- Blocked: the user already has a non-scholarship or submitted registration -->
  <div
    v-else-if="view === 'blocked'"
    class="min-h-screen flex items-center justify-center p-4"
    style="background: #EBF4FF;"
    :dir="isRTL ? 'rtl' : 'ltr'"
  >
    <div class="bg-white rounded-[32px] shadow-lg max-w-md w-full p-8 text-center space-y-6 border border-gray-100">
      <div class="w-16 h-16 bg-amber-50 rounded-full flex items-center justify-center mx-auto">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8 text-amber-500">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
        </svg>
      </div>
      <h2 class="text-lg font-bold text-gray-800">{{ t('scholarship.blocked.title') }}</h2>
      <p class="text-sm text-gray-500 leading-relaxed">{{ t('scholarship.blocked.message') }}</p>
      <button
        @click="goHome"
        class="px-6 py-3 bg-[#34B0EE] text-white rounded-2xl font-bold hover:opacity-90 active:scale-[0.98] transition-all"
      >
        {{ t('scholarship.blocked.button') }}
      </button>
    </div>
  </div>

  <BeneficiaryRegistration
    v-else-if="view === 'wizard'"
    flow="scholarship"
    :registration-name="registrationName"
    @submitted="view = 'success'"
  />

  <div
    v-else-if="view === 'success'"
    class="relative flex-1 flex items-center justify-center p-4 py-8 min-h-screen"
    style="background: #EBF4FF;"
  >
    <RegistrationSuccess
      :title="t('scholarship.success.title')"
      :message="t('scholarship.success.message')"
      :button-text="t('scholarship.success.button')"
      :show-edit-answers="false"
      @view-status="goHome"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import { session } from '@/data/session'
import { useLanguage } from '@/composables/useLanguage'
import BeneficiaryRegistration from '@/components/registration/BeneficiaryRegistration.vue'
import RegistrationSuccess from '@/components/registration/RegistrationSuccess.vue'

const { t, isRTL } = useLanguage()
const router = useRouter()

const view = ref('loading')
const registrationName = ref(null)

const myRegistrations = createResource({
  url: 'frappe.client.get_list',
  onSuccess(rows) {
    if (!rows.length) {
      view.value = 'wizard'
      return
    }
    const draft = rows.find(row => row.is_scholarship && row.status === 'Draft')
    if (draft) {
      registrationName.value = draft.name
      view.value = 'wizard'
    } else {
      view.value = 'blocked'
    }
  },
  onError() {
    view.value = 'blocked'
  },
})

onMounted(() => {
  myRegistrations.submit({
    doctype: 'Beneficiaries Registration',
    filters: { user: session.user },
    fields: ['name', 'status', 'is_scholarship'],
    order_by: 'creation desc',
    limit_page_length: 20,
  })
})

function goHome() {
  router.push({ name: 'Home' })
}
</script>
