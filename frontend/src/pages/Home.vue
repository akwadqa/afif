<template>

  <!-- Loading -->
  <div v-if="view === 'loading'" class="min-h-screen flex items-center justify-center">
    <svg class="animate-spin w-8 h-8 text-[#34B0EE]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
    </svg>
  </div>

  <!-- Welcome / onboarding — no registration yet -->
  <div
    v-else-if="view === 'welcome'"
    class="relative flex-1 flex items-center justify-center p-4 py-8 min-h-screen"
  >
    <img :src="bgImg" alt="" aria-hidden="true" fetchpriority="high"
      class="absolute inset-0 w-full h-full object-cover -z-10 select-none pointer-events-none" />
    <WelcomeCard @action="view = 'registration'" />
  </div>

  <!-- Registration accepted — congrats card -->
  <div
    v-else-if="view === 'accepted'"
    class="relative flex-1 flex items-center justify-center p-4 py-8 min-h-screen"
  >
    <img :src="bgImg" alt="" aria-hidden="true" fetchpriority="high"
      class="absolute inset-0 w-full h-full object-cover -z-10 select-none pointer-events-none" />
    <WelcomeCard
      :title="t('accepted.title')"
      :description="t('accepted.description')"
      :button-text="t('accepted.submitRequest')"
      :link-text="t('accepted.detailsLink')"
      @action="router.push({ name: 'Request' })"
      @link-action="view = 'list'"
    >
      <template #button-icon>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5 shrink-0">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v6m3-3H9m12 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
        </svg>
      </template>
    </WelcomeCard>
  </div>

  <!-- Registration submitted — success card (New Registration, Not Accepted statuses) -->
  <div
    v-else-if="view === 'success'"
    class="relative flex-1 flex items-center justify-center p-4 py-8 min-h-screen"
  >
    <img :src="bgImg" alt="" aria-hidden="true" fetchpriority="high"
      class="absolute inset-0 w-full h-full object-cover -z-10 select-none pointer-events-none" />
    <RegistrationSuccess
      :show-edit-answers="allowEditAfterSubmit"
      @view-status="view = 'list'"
      @edit-answers="view = 'registration'"
    />
  </div>

  <!-- Registration list table -->
  <div
    v-else-if="view === 'list'"
    class="p-6 min-h-screen"
    style="background: #EBF4FF;"
    :dir="isRTL ? 'rtl' : 'ltr'"
  >
    <div class="max-w-5xl mx-auto">
      <div class="flex justify-between items-center mb-6">
        <div>
          <h1 class="text-2xl font-bold text-sky-900">{{ t('beneficiaryList.title') }}</h1>
          <p class="text-sm text-gray-500 mt-1">{{ t('beneficiaryList.subtitle') }}</p>
        </div>
      </div>

      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h3 class="text-md font-semibold text-sky-800 mb-4">{{ t('beneficiaryList.listTitle') }}</h3>

        <div class="overflow-x-auto">
          <table class="w-full text-right border-collapse">
            <thead>
              <tr class="bg-sky-50/50 text-gray-700 font-semibold text-sm border-b border-gray-100">
                <th class="p-4">{{ t('beneficiaryList.columns.index') }}</th>
                <th class="p-4">{{ t('beneficiaryList.columns.name') }}</th>
                <th class="p-4">{{ t('beneficiaryList.columns.status') }}</th>
                <th class="p-4">{{ t('beneficiaryList.columns.nationalId') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(reg, index) in registrations"
                :key="reg.name"
                class="border-b border-gray-50 last:border-0 text-gray-600 hover:bg-slate-50/50 transition text-sm cursor-pointer"
                @click="openRegistration(reg)"
              >
                <td class="p-4">{{ index + 1 }}</td>
                <td class="p-4">{{ reg.ar_name || reg.en_name || '—' }}</td>
                <td class="p-4">
                  <span :class="getRegStatusClass(reg.status)" class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium">
                    <span class="w-1.5 h-1.5 rounded-full" :class="getRegStatusDotClass(reg.status)"></span>
                    {{ t(`statuses.registration.${reg.status}`) || reg.status }}
                  </span>
                </td>
                <td class="p-4 font-mono text-xs" dir="ltr">{{ reg.ben_primary_idnumber || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <!-- Registration form (new or editable existing) -->
  <BeneficiaryRegistration
    v-else-if="view === 'registration'"
    :registration-name="registrationName"
    @submitted="onSubmitted"
    @back="onBackToList"
  />

  <!-- Registration form (read-only view) -->
  <BeneficiaryRegistration
    v-else-if="view === 'view'"
    :registration-name="registrationName"
    :read-only="true"
    @back="onBackToList"
  />

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
const { t, isRTL } = useLanguage()

const view = ref('loading')
const registrationName = ref(null)
const registrations = ref([])
const allowEditAfterSubmit = ref(true)

const EDITABLE_STATUSES = ['Draft', 'New Registration', 'Not Accepted', 'Update Required']

const myRegistrations = createResource({
  url: 'frappe.client.get_list',
  onSuccess(rows) {
    if (!rows.length) {
      view.value = 'welcome'
      return
    }

    registrations.value = rows
    const first = rows[0]
    registrationName.value = first.name

    if (first.status === 'Accepted') {
      const seenKey = `afif_accepted_seen_${session.user}`
      if (!localStorage.getItem(seenKey)) {
        localStorage.setItem(seenKey, '1')
        view.value = 'accepted'
      } else {
        view.value = 'list'
      }
    } else {
      view.value = 'list'
    }
  },
  onError() {
    view.value = 'welcome'
  },
})

function fetchRegistrations() {
  myRegistrations.submit({
    doctype: 'Beneficiaries Registration',
    filters: { user: session.user },
    fields: ['name', 'ar_name', 'en_name', 'status', 'ben_primary_idnumber'],
    limit_page_length: 20,
  })
}

onMounted(fetchRegistrations)

function openRegistration(reg) {
  registrationName.value = reg.name
  if (EDITABLE_STATUSES.includes(reg.status)) {
    view.value = 'registration'
  } else {
    view.value = 'view'
  }
}

function onSubmitted(name) {
  registrationName.value = name
  allowEditAfterSubmit.value = true
  view.value = 'success'
}

function onBackToList() {
  fetchRegistrations()
}

function getRegStatusClass(status) {
  switch (status) {
    case 'Accepted':
    case 'Updated beneficiary':
      return 'bg-green-50 text-green-700'
    case 'New Registration':
    case 'Updated':
      return 'bg-blue-50 text-blue-700'
    case 'Not Accepted':
      return 'bg-red-50 text-red-700'
    case 'Update Required':
      return 'bg-amber-50 text-amber-700'
    case 'Draft':
    default:
      return 'bg-gray-50 text-gray-700'
  }
}

function getRegStatusDotClass(status) {
  switch (status) {
    case 'Accepted':
    case 'Updated beneficiary':
      return 'bg-green-500'
    case 'New Registration':
    case 'Updated':
      return 'bg-blue-500'
    case 'Not Accepted':
      return 'bg-red-500'
    case 'Update Required':
      return 'bg-amber-500'
    case 'Draft':
    default:
      return 'bg-gray-500'
  }
}
</script>
