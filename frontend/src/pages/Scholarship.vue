<template>
  <!-- Loading -->
  <div v-if="view === 'loading'" class="min-h-screen flex items-center justify-center">
    <svg class="animate-spin w-8 h-8 text-[#34B0EE]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
    </svg>
  </div>

  <!-- Blocked: the user registered through the normal flow, which has no scholarship (plan Phase 7) -->
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

  <!-- A submitted application: the registration and the latest scholarship request, read only -->
  <template v-else-if="view === 'application'">
    <div v-if="isRestricted" class="px-4 md:px-8 pt-6" style="background: #EBF4FF;" :dir="isRTL ? 'rtl' : 'ltr'">
      <Alert theme="red" :title="t('scholarship.restricted')" class="max-w-5xl mx-auto" />
    </div>
    <BeneficiaryRegistration
      flow="scholarship"
      read-only
      :registration-name="registration.name"
      @back="goHome"
    >
      <template #actions>
        <ScholarshipApplyButton :status="registration.status" @apply="view = 'apply'" />
      </template>
    </BeneficiaryRegistration>
  </template>

  <!-- A new scholarship request, once the request rules allow it -->
  <ScholarshipApplyForm v-else-if="view === 'apply'" @submitted="view = 'appliedSuccess'" />

  <div
    v-else-if="view === 'success' || view === 'appliedSuccess'"
    class="relative flex-1 flex items-center justify-center p-4 py-8 min-h-screen"
    style="background: #EBF4FF;"
  >
    <RegistrationSuccess
      :title="t('scholarship.success.title')"
      :message="t(view === 'appliedSuccess' ? 'scholarship.success.acceptedMessage' : 'scholarship.success.message')"
      :button-text="t('scholarship.success.button')"
      :show-edit-answers="false"
      @view-status="goHome"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Alert, createResource } from 'frappe-ui'
import { session } from '@/data/session'
import { useLanguage } from '@/composables/useLanguage'
import { useAccountStatus } from '@/composables/useAccountStatus'
import BeneficiaryRegistration from '@/components/registration/BeneficiaryRegistration.vue'
import RegistrationSuccess from '@/components/registration/RegistrationSuccess.vue'
import ScholarshipApplyButton from '@/components/registration/ScholarshipApplyButton.vue'
import ScholarshipApplyForm from '@/components/registration/ScholarshipApplyForm.vue'

const { t, isRTL } = useLanguage()
const route = useRoute()
const router = useRouter()
const { isRestricted } = useAccountStatus()

const view = ref('loading')
const registrationName = ref(null)
// The user's submitted scholarship registration.
const registration = ref(null)

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
    } else if (rows[0].is_scholarship) {
      registration.value = rows[0]
      // The profile's apply button links here with ?apply=1; the server refuses a request it shouldn't take.
      view.value = route.query.apply && rows[0].status === 'Accepted' ? 'apply' : 'application'
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
