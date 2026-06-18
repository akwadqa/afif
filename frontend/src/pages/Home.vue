<template>

  <!-- Initial lookup of the user's existing registration, if any -->
  <div
    v-if="view === 'loading'"
    class="min-h-screen flex items-center justify-center"
  >
    <svg class="animate-spin w-8 h-8 text-[#34B0EE]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
    </svg>
  </div>

  <!-- Welcome / onboarding state -->
  <div
    v-else-if="view === 'welcome'"
    class="relative flex-1 flex items-center justify-center p-4 py-8 min-h-screen"
  >
    <img
      :src="bgImg"
      alt=""
      aria-hidden="true"
      fetchpriority="high"
      class="absolute inset-0 w-full h-full object-cover -z-10 select-none pointer-events-none"
    />
    <WelcomeCard @action="view = 'registration'" />
  </div>

  <!-- Registration accepted – can now submit aid requests -->
  <div
    v-else-if="view === 'accepted'"
    class="relative flex-1 flex items-center justify-center p-4 py-8 min-h-screen"
  >
    <img
      :src="bgImg"
      alt=""
      aria-hidden="true"
      fetchpriority="high"
      class="absolute inset-0 w-full h-full object-cover -z-10 select-none pointer-events-none"
    />
    <WelcomeCard
      :title="t('accepted.title')"
      :description="t('accepted.description')"
      :button-text="t('accepted.submitRequest')"
      :link-text="t('accepted.detailsLink')"
      @action="router.push({ name: 'Request' })"
    >
      <template #button-icon>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5 shrink-0">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v6m3-3H9m12 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
        </svg>
      </template>
    </WelcomeCard>
  </div>

  <!-- Multi-step beneficiary registration (new, Draft, or Not Accepted/editable) -->
  <BeneficiaryRegistration
    v-else-if="view === 'registration'"
    :registration-name="registrationName"
    @submitted="onSubmitted"
  />

  <!-- Registration success / read-only summary screen -->
  <RegistrationSuccess
    v-else-if="view === 'success'"
    :show-edit-answers="allowEditAfterSubmit"
    @view-status="view = 'dashboard'"
    @edit-answers="view = 'registration'"
  />

  <!-- Dashboard (placeholder until implemented) -->
  <div v-else class="max-w-3xl py-12 mx-auto">
    <!-- dashboard content goes here -->
  </div>

</template>

<script setup>
import { ref, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import { useRouter } from 'vue-router'
import bgImg from '@/assets/images/background.png'
import { session } from '@/data/session'
import { useLanguage } from '@/composables/useLanguage'
import WelcomeCard from '@/components/onboarding/WelcomeCard.vue'
import BeneficiaryRegistration from '@/components/registration/BeneficiaryRegistration.vue'
import RegistrationSuccess from '@/components/registration/RegistrationSuccess.vue'

const router = useRouter()
const { t } = useLanguage()

const view = ref('loading')
const registrationName = ref(null)
const allowEditAfterSubmit = ref(true)

const myRegistrations = createResource({
  url: 'frappe.client.get_list',
  onSuccess(rows) {
    if (!rows.length) {
      view.value = 'welcome'
      return
    }

    const { name, status } = rows[0]
    registrationName.value = name

    if (status === 'Draft') {
      view.value = 'registration'
    } else if (status === 'New Registration' || status === 'Not Accepted') {
      allowEditAfterSubmit.value = true
      view.value = 'success'
    } else if (status === 'Accepted') {
      view.value = 'accepted'
    } else {
      view.value = 'dashboard'
    }
  },
  onError() {
    view.value = 'welcome'
  },
})

onMounted(() => {
  myRegistrations.submit({
    doctype: 'Beneficiaries Registration',
    filters: { user: session.user },
    fields: ['name', 'status'],
    limit_page_length: 1,
  })
})

function onSubmitted(name) {
  registrationName.value = name
  allowEditAfterSubmit.value = true
  view.value = 'success'
}
</script>
