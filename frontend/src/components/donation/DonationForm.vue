<template>
  <div class="min-h-screen flex justify-center p-4 py-12" style="background: #EBF4FF;">
  <div class="w-full max-w-xl mx-auto" :dir="isRTL ? 'rtl' : 'ltr'">

    <button
      type="button"
      class="flex items-center gap-1.5 text-sm text-gray-500 hover:text-sky-600 font-medium mb-4 transition-colors"
      @click="goBack"
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4" :class="{ 'rotate-180': !isRTL }">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
      </svg>
      <span>{{ t('donation.back') }}</span>
    </button>

    <!-- Coverage / progress card -->
    <div class="form-card">
      <h3 class="section-title">{{ t('donation.coverageTitle') }}</h3>

      <div class="metrics-grid">
        <div class="metric-item">
          <span class="label">{{ t('donation.collectedAmount') }}</span>
          <span class="value">{{ selectedProjectData?.donated_amount || 0 }} {{ t('donation.currency') }}</span>
        </div>
        <div class="metric-item border-center">
          <span class="label">{{ t('donation.targetAmount') }}</span>
          <span class="value">{{ selectedProjectData?.required_amount || 0 }} {{ t('donation.currency') }}</span>
        </div>
      </div>

      <div class="progress-bar-container">
        <div
          class="progress-bar-fill"
          :style="{ width: coveragePercentage + '%' }"
          :class="{ 'fully-funded': coveragePercentage >= 100 }"
        >
          <span class="progress-text">
            {{ coveragePercentage >= 100 ? t('donation.fullyFunded') : t('donation.partiallyFundedLabel') }}
          </span>
        </div>
        <span class="progress-percentage-label" v-if="coveragePercentage < 100">{{ coveragePercentage }}%</span>
      </div>

      <p class="status-subtext">
        <span v-if="coveragePercentage >= 100" class="success-badge">✓ {{ t('donation.fullyFunded') }}</span>
        <span v-else>{{ t('donation.raisedPrefix') }} {{ coveragePercentage }}{{ t('donation.raisedSuffix') }}</span>
      </p>
    </div>

    <!-- Program / project selection -->
    <div class="form-card">
      <div class="input-group">
        <label class="input-label">{{ t('donation.program') }} <span class="text-red-500">*</span></label>
        <select v-model="selectedProgram" class="custom-select" :disabled="programs.loading || isLocked">
          <option value="" disabled>{{ t('donation.selectProgram') }}</option>
          <option v-for="program in programsList" :key="program.name" :value="program.name">{{ program.title }}</option>
        </select>
      </div>

      <div class="input-group">
        <label class="input-label">{{ t('donation.project') }} <span class="text-red-500">*</span></label>
        <select v-model="selectedProject" class="custom-select" :disabled="!selectedProgram || projects.loading || isLocked">
          <option value="" disabled>{{ t('donation.selectProject') }}</option>
          <option v-for="project in projectsList" :key="project.name" :value="project.name">{{ project.title }}</option>
        </select>
        <p v-if="selectedProgram && !projects.loading && !projectsList.length" class="text-xs text-gray-400 mt-2">
          {{ t('donation.noProjects') }}
        </p>
      </div>

      <template v-if="selectedProject">
        <div v-if="selectedProgramData?.intro" class="info-notice-box" v-html="selectedProgramData.intro"></div>
        <div v-if="selectedProjectData?.body" class="secondary-notice-box" v-html="selectedProjectData.body"></div>
      </template>
    </div>

    <!-- Amount -->
    <div class="form-card">
      <label class="input-label">{{ t('donation.amountLabel') }} <span class="text-red-500">*</span></label>
      <div class="presets-row">
        <button
          v-for="amount in presetAmounts"
          :key="amount"
          type="button"
          class="preset-btn"
          :class="{ active: donationAmount === amount && !isCustomAmount }"
          @click="setPresetAmount(amount)"
        >
          {{ amount }}
        </button>
        <button
          type="button"
          class="preset-btn"
          :class="{ active: isCustomAmount }"
          @click="activateCustomAmount"
        >
          {{ t('donation.customAmount') }}
        </button>
      </div>

      <div class="input-group margin-top-sm">
        <label class="input-label">{{ t('donation.enterAmount') }} <span class="text-red-500">*</span></label>
        <input
          type="number"
          min="1"
          v-model.number="donationAmount"
          class="custom-input text-left"
          :placeholder="t('donation.amountPlaceholder')"
          :disabled="!isCustomAmount"
        />
      </div>

      <div class="license-note">
        <p>{{ t('donation.licenseText') }}</p>
        <span class="no-admin-fee-badge">{{ t('donation.noAdminFee') }}</span>
      </div>
    </div>

    <!-- Donor info + submit -->
    <div class="form-card">
      <div class="checkbox-container">
        <input id="donation-anonymous" type="checkbox" v-model="donorForm.isAnonymous" class="custom-checkbox" />
        <label for="donation-anonymous" class="checkbox-label">{{ t('donation.anonymousLabel') }}</label>
      </div>

      <Transition name="fade-slide">
        <div v-if="!donorForm.isAnonymous" class="space-y-4 mb-4">
          <div class="input-group">
            <label class="input-label">{{ t('donation.donorName') }}</label>
            <input type="text" v-model="donorForm.fullName" class="custom-input" :placeholder="t('donation.donorNamePlaceholder')" />
          </div>
          <div class="input-group">
            <label class="input-label">{{ t('donation.donorPhone') }}</label>
            <input type="tel" v-model="donorForm.phone" class="custom-input text-left" :placeholder="t('donation.donorPhonePlaceholder')" />
          </div>
          <div class="input-group">
            <label class="input-label">{{ t('donation.donorEmail') }}</label>
            <input type="email" v-model="donorForm.email" class="custom-input text-left" :placeholder="t('donation.donorEmailPlaceholder')" />
          </div>
        </div>
      </Transition>

      <p v-if="errorMessage" class="text-sm text-red-500 mb-3">{{ errorMessage }}</p>

      <button
        type="button"
        class="submit-donation-btn"
        :disabled="!canSubmit || createDonation.loading"
        @click="submitDonation"
      >
        {{ createDonation.loading ? t('donation.submitting') : `${t('donation.confirmDonate')} ${donationAmount || 0} ${t('donation.currency')}` }}
      </button>
    </div>

  </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import { useLanguage } from '@/composables/useLanguage'

const route = useRoute()
const router = useRouter()

const { t, isRTL, currentLang } = useLanguage()

const presetAmounts = [10, 50, 100, 1000]

const initialProjectQuery = typeof route.query.project === 'string' ? route.query.project : ''
const preselectedProject = ref(initialProjectQuery)
const isLocked = computed(() => !!initialProjectQuery)

const selectedProgram = ref('')
const selectedProject = ref('')
const donationAmount = ref(0)
const isCustomAmount = ref(false)
const errorMessage = ref('')

function goBack() {
  if (initialProjectQuery) {
    router.push({ name: 'DonationProject', params: { name: initialProjectQuery } })
  } else {
    router.push({ name: 'Donate' })
  }
}

const donorForm = reactive({
  isAnonymous: false,
  fullName: '',
  phone: '',
  email: '',
})

function extractError(err) {
  if (err._server_messages) {
    try {
      const parsed = JSON.parse(err._server_messages)
      const first = typeof parsed[0] === 'string' ? JSON.parse(parsed[0]) : parsed[0]
      if (first.message) return first.message
    } catch { /* fall through */ }
  }
  if (err.messages?.length) {
    const msg = err.messages[0]
    return typeof msg === 'string' ? msg : msg.message || JSON.stringify(msg)
  }
  return err.message || err.exc_type || t('donation.submitError')
}

const programs = createResource({ url: 'afif.donation_api.get_programs', method: 'GET' })
const projects = createResource({ url: 'afif.donation_api.get_projects', method: 'GET' })
const projectDetail = createResource({
  url: 'afif.donation_api.get_project_detail',
  method: 'GET',
  onSuccess(data) {
    selectedProgram.value = data.program
  },
})
const createDonation = createResource({
  url: 'afif.donation_api.create_donation',
  onSuccess(data) {
    window.location.href = data.payment_url
  },
  onError(err) {
    errorMessage.value = extractError(err)
  },
})

const programsList = computed(() => programs.data || [])
const projectsList = computed(() => projects.data || [])
const selectedProgramData = computed(
  () => programsList.value.find((program) => program.name === selectedProgram.value) || null
)
const selectedProjectData = computed(
  () => projectsList.value.find((project) => project.name === selectedProject.value) || null
)

const coveragePercentage = computed(() => {
  if (!selectedProjectData.value) return 0
  return Math.min(Math.round(selectedProjectData.value.percentage || 0), 100)
})

const canSubmit = computed(
  () => !!selectedProject.value && !!donationAmount.value && donationAmount.value > 0
)

function fetchPrograms() {
  programs.submit({ lang: currentLang.value })
}

function fetchProjects() {
  if (!selectedProgram.value) return Promise.resolve()
  return projects.submit({ program: selectedProgram.value, lang: currentLang.value })
}

onMounted(() => {
  fetchPrograms()
  if (preselectedProject.value) {
    projectDetail.submit({ project_name: preselectedProject.value, lang: currentLang.value })
  }
})

watch(selectedProgram, () => {
  const keepProject = preselectedProject.value
  selectedProject.value = ''
  donationAmount.value = 0
  isCustomAmount.value = false
  if (selectedProgram.value) {
    fetchProjects().then(() => {
      if (keepProject) {
        selectedProject.value = keepProject
        preselectedProject.value = ''
      }
    })
  }
})

watch(currentLang, () => {
  fetchPrograms()
  if (selectedProgram.value) fetchProjects()
})

function setPresetAmount(amount) {
  isCustomAmount.value = false
  donationAmount.value = amount
}

function activateCustomAmount() {
  isCustomAmount.value = true
  donationAmount.value = 0
}

function submitDonation() {
  if (!canSubmit.value) return
  errorMessage.value = ''
  createDonation.submit({
    donation_project: selectedProject.value,
    amount: donationAmount.value,
    donor_name: donorForm.isAnonymous ? null : donorForm.fullName || null,
    donor_mobile: donorForm.isAnonymous ? null : donorForm.phone || null,
    donor_email: donorForm.isAnonymous ? null : donorForm.email || null,
  })
}
</script>

<style scoped>
.form-card {
  @apply bg-white rounded-[24px] p-6 shadow-sm border border-gray-100 mb-5;
}

.section-title {
  @apply text-sky-600 text-base font-bold mb-4;
}

.input-group {
  @apply mb-4 last:mb-0;
}

.input-label {
  @apply text-xs font-semibold text-gray-700 block leading-relaxed mb-2;
}

.custom-input,
.custom-select {
  @apply w-full px-4 py-3 bg-gray-50/60 border border-gray-100/70 rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all placeholder:text-gray-300;
}

.custom-input:disabled,
.custom-select:disabled {
  @apply opacity-75 cursor-default;
  background-color: #f9fafb;
}

.custom-select {
  @apply appearance-none bg-no-repeat text-gray-700;
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23a0aec0%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
  background-size: 12px 12px;
  background-position: left 1rem center;
}

.text-left {
  text-align: left;
}

.metrics-grid {
  @apply flex justify-between mb-4;
}

.metric-item {
  @apply flex-1 flex items-center justify-between gap-2;
}

.border-center {
  border-inline-start: 1px solid #e5e7eb;
  padding-inline-start: 16px;
}

.metric-item .label {
  @apply text-xs text-gray-400;
}

.metric-item .value {
  @apply text-sm font-bold text-gray-800;
}

.progress-bar-container {
  @apply bg-gray-100 rounded-full h-9 relative overflow-hidden flex items-center;
}

.progress-bar-fill {
  background-color: #34b0ee;
  @apply h-full rounded-full flex items-center px-3 transition-all;
}

.progress-bar-fill.fully-funded {
  background-color: #34b0ee;
  width: 100% !important;
}

.progress-text {
  @apply text-white text-xs font-semibold whitespace-nowrap;
}

.progress-percentage-label {
  position: absolute;
  inset-inline-end: 16px;
  @apply text-xs font-bold text-gray-600;
}

.status-subtext {
  @apply text-center text-[13px] text-gray-600 mt-3;
}

.success-badge {
  @apply text-green-500 font-semibold;
}

.info-notice-box {
  border-inline-start: 4px solid #34b0ee;
  @apply bg-sky-50 p-3 rounded-lg mt-4 text-[13px] text-sky-700 leading-relaxed;
}

.secondary-notice-box {
  @apply bg-gray-50 border border-gray-100 p-3 rounded-lg mt-3 text-xs text-gray-500 leading-relaxed;
}

.presets-row {
  @apply flex gap-2 mb-3;
}

.preset-btn {
  @apply flex-1 bg-gray-50/60 border border-gray-100/70 py-2.5 rounded-lg font-semibold text-gray-800 text-sm transition-colors;
}

.preset-btn.active {
  @apply bg-sky-50 text-sky-600;
  border-color: #34b0ee;
}

.margin-top-sm {
  @apply mt-3;
}

.license-note {
  @apply text-center mt-4;
}

.license-note p {
  @apply text-[11px] text-gray-400 leading-relaxed;
}

.no-admin-fee-badge {
  @apply inline-block mt-2 px-4 py-1.5 rounded-full text-xs font-bold text-gray-500 bg-gray-100 border border-gray-200 cursor-default select-none;
}

.checkbox-container {
  @apply flex items-center gap-2 mb-4;
}

.custom-checkbox {
  width: 18px;
  height: 18px;
  accent-color: #34b0ee;
}

.checkbox-label {
  @apply text-sm font-semibold text-gray-800;
}

.submit-donation-btn {
  @apply w-full text-white border-none py-3.5 text-base font-bold rounded-xl transition-transform;
  background-color: #34b0ee;
  box-shadow: 0 4px 12px rgba(52, 176, 238, 0.25);
}

.submit-donation-btn:active {
  transform: scale(0.99);
}

.submit-donation-btn:disabled {
  @apply opacity-50 cursor-not-allowed;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
