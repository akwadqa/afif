<template>
  <!-- Loading -->
  <div v-if="view === 'loading'" class="min-h-screen flex items-center justify-center">
    <svg class="animate-spin w-8 h-8 text-[#34B0EE]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
    </svg>
  </div>

  <!-- Blocked — registration not accepted -->
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
      <h2 class="text-lg font-bold text-gray-800">{{ t('request.notAcceptedTitle') }}</h2>
      <p class="text-sm text-gray-500 leading-relaxed">{{ t('request.notAcceptedMessage') }}</p>
      <button
        @click="$router.push({ name: 'Home' })"
        class="px-6 py-3 bg-[#34B0EE] text-white rounded-2xl font-bold hover:opacity-90 active:scale-[0.98] transition-all"
      >
        {{ t('request.backToHome') }}
      </button>
    </div>
  </div>

  <!-- Requests list table -->
  <div
    v-else-if="view === 'list'"
    class="p-6 min-h-screen"
    style="background: #EBF4FF;"
    :dir="isRTL ? 'rtl' : 'ltr'"
  >
    <div class="max-w-5xl mx-auto">
      <div class="flex justify-between items-center mb-6">
        <div>
          <h1 class="text-2xl font-bold text-sky-900">{{ t('myRequests.title') }}</h1>
          <p class="text-sm text-gray-500 mt-1">{{ t('myRequests.subtitle') }}</p>
        </div>
        <div class="relative group">
          <button
            :disabled="!canCreateRequest"
            @click="view = 'form'"
            class="bg-sky-500 hover:bg-sky-600 text-white font-medium py-2 px-4 rounded-xl flex items-center gap-2 shadow-sm transition disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-sky-500"
          >
            <span class="text-lg">+</span>
            {{ t('myRequests.createNew') }}
          </button>
          <div
            v-if="!canCreateRequest && disabledReason"
            class="absolute top-full mt-2 bg-gray-800 text-white text-xs rounded-lg px-3 py-2 max-w-xs opacity-0 group-hover:opacity-100 transition-opacity z-10 shadow-lg"
            :class="isRTL ? 'right-0' : 'left-0'"
          >
            {{ disabledReason }}
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h3 class="text-md font-semibold text-sky-800 mb-4">{{ t('myRequests.listTitle') }}</h3>

        <div v-if="!requests.length" class="text-center text-gray-400 py-8 text-sm">
          {{ t('myRequests.noRequests') }}
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-right border-collapse">
            <thead>
              <tr class="bg-sky-50/50 text-gray-700 font-semibold text-sm border-b border-gray-100">
                <th class="p-4">{{ t('myRequests.columns.index') }}</th>
                <th class="p-4">{{ t('myRequests.columns.serial') }}</th>
                <th class="p-4">{{ t('myRequests.columns.beneficiary') }}</th>
                <th class="p-4">{{ t('myRequests.columns.type') }}</th>
                <th class="p-4">{{ t('myRequests.columns.date') }}</th>
                <th class="p-4">{{ t('myRequests.columns.status') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(req, index) in requests"
                :key="req.name"
                class="border-b border-gray-50 last:border-0 text-gray-600 hover:bg-slate-50/50 transition text-sm cursor-pointer"
                @click="openRequest(req)"
              >
                <td class="p-4">{{ index + 1 }}</td>
                <td class="p-4 font-mono text-xs" dir="ltr">{{ req.request_fullserial || req.name }}</td>
                <td class="p-4">{{ beneficiaryDisplayName }}</td>
                <td class="p-4">{{ translateCategory(req.request_category) }}</td>
                <td class="p-4 font-mono text-xs" dir="ltr">{{ formatDate(req.request_date) }}</td>
                <td class="p-4">
                  <span :class="getReqStatusClass(req.status)" class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium">
                    <span class="w-1.5 h-1.5 rounded-full" :class="getReqStatusDotClass(req.status)"></span>
                    {{ t(`statuses.request.${req.status}`) || req.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <!-- Create new request form -->
  <BeneficiaryRequest
    v-else-if="view === 'form'"
    :beneficiary-name="beneficiaryName"
    @submitted="onRequestSubmitted"
    @back="onBackToList"
  />

  <!-- View existing request (read-only) -->
  <BeneficiaryRequest
    v-else-if="view === 'view'"
    :beneficiary-name="beneficiaryName"
    :request-name="selectedRequestName"
    :read-only="true"
    @back="onBackToList"
  />

  <!-- Success after submission -->
  <div
    v-else-if="view === 'success'"
    class="relative flex-1 flex items-center justify-center p-4 py-8 min-h-screen"
  >
    <img :src="bgImg" alt="" aria-hidden="true" fetchpriority="high"
      class="absolute inset-0 w-full h-full object-cover -z-10 select-none pointer-events-none" />
    <RegistrationSuccess
      title="نجاح تسجيل الطلب"
      message="طلبك الآن بإنتظار تقديم الاقرار. يجب زيارة موقع جمعية عفيف الخيرية خلال 3 ايام لتوقيع الاقرار المطلوب. في حال لم يتم زيارة الموقع خلال المدة هذه، سيتم الغاء الطلب."
      button-text="الاطلاع على حالة طلباتي"
      :show-edit-answers="false"
      @view-status="onBackToList"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import { session } from '@/data/session'
import { useLanguage } from '@/composables/useLanguage'
import bgImg from '@/assets/images/background.png'
import BeneficiaryRequest from '@/components/request/BeneficiaryRequest.vue'
import RegistrationSuccess from '@/components/registration/RegistrationSuccess.vue'

const { t, isRTL } = useLanguage()

const view = ref('loading')
const beneficiaryName = ref('')
const beneficiaryDisplayName = ref('')
const requests = ref([])
const selectedRequestName = ref('')

const PENDING_STATUSES = ['Pending Supervisor Approval', 'Pending Specialist Approval', 'Saved']
const FINAL_STATUSES = ['Rejected by Supervisor', 'Rejected', 'Approved', 'Approved For Aid']

const CATEGORY_KEYS = {
  'Medical Assistance': 'request.categories.medical',
  'Education Assistance': 'request.categories.education',
  'Social Assistance': 'request.categories.social',
  'Family Assistance': 'request.categories.family',
  'Housing Assistance': 'request.categories.housing',
  'Training Assistance': 'request.categories.training',
  'Awareness Assistance': 'request.categories.awareness',
}

const canCreateRequest = computed(() => {
  if (!requests.value.length) return true

  const last = requests.value[0]

  if (!FINAL_STATUSES.includes(last.status)) return false

  if (last.rejected_date) {
    const rejectedDate = new Date(last.rejected_date)
    const threeMonthsLater = new Date(rejectedDate)
    threeMonthsLater.setMonth(threeMonthsLater.getMonth() + 3)
    if (new Date() < threeMonthsLater) return false
  }

  if (last.approved_for_aid_date) {
    const approvedDate = new Date(last.approved_for_aid_date)
    const sixMonthsLater = new Date(approvedDate)
    sixMonthsLater.setMonth(sixMonthsLater.getMonth() + 6)
    if (new Date() < sixMonthsLater) return false
  }

  return true
})

const disabledReason = computed(() => {
  if (!requests.value.length) return ''

  const last = requests.value[0]

  if (!FINAL_STATUSES.includes(last.status)) {
    return t('myRequests.disabledReasons.pending')
  }

  if (last.rejected_date) {
    const rejectedDate = new Date(last.rejected_date)
    const threeMonthsLater = new Date(rejectedDate)
    threeMonthsLater.setMonth(threeMonthsLater.getMonth() + 3)
    if (new Date() < threeMonthsLater) {
      return t('myRequests.disabledReasons.cooldownRejected')
    }
  }

  if (last.approved_for_aid_date) {
    const approvedDate = new Date(last.approved_for_aid_date)
    const sixMonthsLater = new Date(approvedDate)
    sixMonthsLater.setMonth(sixMonthsLater.getMonth() + 6)
    if (new Date() < sixMonthsLater) {
      return t('myRequests.disabledReasons.cooldownApproved')
    }
  }

  return ''
})

const myRegistration = createResource({
  url: 'frappe.client.get_list',
  onSuccess(rows) {
    if (!rows.length || rows[0].status !== 'Accepted') {
      view.value = 'blocked'
      return
    }

    beneficiaryName.value = rows[0].name
    beneficiaryDisplayName.value = rows[0].ar_name || rows[0].en_name || ''
    fetchRequests()
  },
  onError() {
    view.value = 'blocked'
  },
})

const myRequests = createResource({
  url: 'frappe.client.get_list',
  onSuccess(rows) {
    requests.value = rows
    view.value = 'list'
  },
  onError() {
    requests.value = []
    view.value = 'list'
  },
})

function fetchRequests() {
  myRequests.submit({
    doctype: 'Beneficiary Request',
    filters: { beneficiaries: beneficiaryName.value },
    fields: [
      'name', 'request_fullserial', 'request_category', 'request_date',
      'status', 'rejected_date', 'approved_for_aid_date',
    ],
    order_by: 'creation desc',
    limit_page_length: 50,
  })
}

onMounted(() => {
  myRegistration.submit({
    doctype: 'Beneficiaries Registration',
    filters: { user: session.user },
    fields: ['name', 'status', 'ar_name', 'en_name'],
    limit_page_length: 1,
  })
})

function openRequest(req) {
  selectedRequestName.value = req.name
  view.value = 'view'
}

function onRequestSubmitted() {
  view.value = 'success'
}

function onBackToList() {
  fetchRequests()
}

function translateCategory(category) {
  const key = CATEGORY_KEYS[category]
  return key ? t(key) : category || '—'
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  const day = String(d.getDate()).padStart(2, '0')
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const year = d.getFullYear()
  return `${day}-${month}-${year}`
}

function getReqStatusClass(status) {
  switch (status) {
    case 'Approved':
    case 'Approved For Aid':
      return 'bg-green-50 text-green-700'
    case 'Pending Supervisor Approval':
    case 'Pending Specialist Approval':
    case 'Saved':
      return 'bg-amber-50 text-amber-700'
    case 'Rejected':
    case 'Rejected by Supervisor':
      return 'bg-red-50 text-red-700'
    default:
      return 'bg-gray-50 text-gray-700'
  }
}

function getReqStatusDotClass(status) {
  switch (status) {
    case 'Approved':
    case 'Approved For Aid':
      return 'bg-green-500'
    case 'Pending Supervisor Approval':
    case 'Pending Specialist Approval':
    case 'Saved':
      return 'bg-amber-500'
    case 'Rejected':
    case 'Rejected by Supervisor':
      return 'bg-red-500'
    default:
      return 'bg-gray-500'
  }
}
</script>
