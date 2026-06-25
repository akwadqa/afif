<template>

  <!-- Loading -->
  <div v-if="view === 'loading'" class="min-h-screen flex items-center justify-center">
    <svg class="animate-spin w-8 h-8 text-[#34B0EE]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
    </svg>
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
    @submitted="onSubmitted"
    @back="onBackToList"
  />

  <!-- Success after registration submission -->
  <div
    v-else-if="view === 'success'"
    class="relative flex-1 flex items-center justify-center p-4 py-8 min-h-screen"
    style="background: #EBF4FF;"
  >
    <RegistrationSuccess
      title="تم التسجيل بنجاح"
      message="تم استلام تسجيل بياناتك بنجاح. يرجى انتظار إشعار سيصلك عبر البريد الإلكتروني لاستكمال باقي الإجراءات."
      button-text="الاطلاع على حالة تسجيل الملف"
      :show-edit-answers="false"
      @view-status="onBackToList"
    />
  </div>

</template>

<script setup>
import { ref, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import { session } from '@/data/session'
import { useLanguage } from '@/composables/useLanguage'
import BeneficiaryRegistration from '@/components/registration/BeneficiaryRegistration.vue'
import RegistrationSuccess from '@/components/registration/RegistrationSuccess.vue'

const { t, isRTL } = useLanguage()

const view = ref('loading')
const registrationName = ref(null)
const registrations = ref([])

const EDITABLE_STATUSES = ['Draft', 'New Registration', 'Not Accepted', 'Update Required']

const myRegistrations = createResource({
  url: 'frappe.client.get_list',
  onSuccess(rows) {
    if (view.value === 'success') {
      registrations.value = rows
      return
    }

    if (!rows.length) {
      view.value = 'registration'
      return
    }

    registrations.value = rows
    const first = rows[0]
    registrationName.value = first.name
    view.value = 'list'
  },
  onError() {
    if (view.value !== 'success') {
      view.value = 'registration'
    }
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
  view.value = 'view'
}

function onSubmitted(name) {
  registrationName.value = name
  view.value = 'success'
  fetchRegistrations()
}

function onBackToList() {
  view.value = 'loading'
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
