<template>
  <Dialog v-model="isOpen" :options="{ size: '3xl', position: 'top', paddingTop: dialogPaddingTop }" @close="handleClose">
    <template #body>
      <div class="donation-dialog" :dir="isRTL ? 'rtl' : 'ltr'">
        <div class="dialog-header">
          <button type="button" class="close-btn" :aria-label="t('donation.dialog.close')" @click="close">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
            </svg>
          </button>
          <h2 class="dialog-title">{{ t('donation.dialog.title') }}</h2>
        </div>

        <!-- Amount selection -->
        <div class="dialog-card">
          <div class="field-label">
            <span>{{ t('donation.amountLabel') }}</span>
            <span class="required-star">*</span>
          </div>

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
            <button type="button" class="preset-btn" :class="{ active: isCustomAmount }" @click="activateCustomAmount">
              {{ t('donation.customAmount') }}
            </button>
          </div>

          <div class="amount-field">
            <div class="field-label">
              <span>{{ t('donation.enterAmount') }}</span>
              <span class="required-star">*</span>
            </div>
            <input
              type="number"
              min="1"
              v-model.number="donationAmount"
              class="amount-input"
              :placeholder="t('donation.amountPlaceholder')"
              :disabled="!isCustomAmount"
            />
          </div>

          <span class="no-admin-fee-badge">{{ t('donation.noAdminFee') }}</span>
        </div>

        <!-- Recurrence -->
        <div class="dialog-card">
          <div class="frequency-row">
            <button type="button" class="frequency-toggle" @click="toggleFrequency('Monthly')">
              <span class="radio-circle" :class="{ checked: donationFrequency === 'Monthly' }" />
              <span class="frequency-label">{{ t('donation.frequency.monthly') }}</span>
            </button>
            <p class="frequency-desc">{{ t('donation.frequency.monthlyDesc') }}</p>
          </div>

          <div class="frequency-row">
            <button type="button" class="frequency-toggle" @click="toggleFrequency('Annual')">
              <span class="radio-circle" :class="{ checked: donationFrequency === 'Annual' }" />
              <span class="frequency-label">{{ t('donation.frequency.annual') }}</span>
            </button>
            <p class="frequency-desc">{{ t('donation.frequency.annualDesc') }}</p>
          </div>

          <div class="frequency-row">
            <button type="button" class="frequency-toggle" @click="toggleFrequency('Daily')">
              <span class="radio-circle" :class="{ checked: donationFrequency === 'Daily' }" />
              <span class="frequency-label">{{ t('donation.frequency.daily') }}</span>
            </button>
            <p class="frequency-desc">{{ t('donation.frequency.dailyDesc') }}</p>
          </div>
        </div>

        <!-- Donor info + submit -->
        <div class="dialog-card">
          <div class="checkbox-container">
            <input id="dialog-anonymous" type="checkbox" v-model="donorForm.isAnonymous" class="custom-checkbox" />
            <label for="dialog-anonymous" class="checkbox-label">{{ t('donation.anonymousLabel') }}</label>
          </div>

          <Transition name="fade-slide">
            <div v-if="!donorForm.isAnonymous" class="donor-fields">
              <div class="field-group">
                <label class="field-label-plain">{{ t('donation.donorName') }}</label>
                <input type="text" v-model="donorForm.fullName" class="text-input" :placeholder="t('donation.donorNamePlaceholder')" />
              </div>
              <div class="field-group">
                <label class="field-label-plain">{{ t('donation.donorPhone') }}</label>
                <input type="tel" v-model="donorForm.phone" class="text-input" :placeholder="t('donation.donorPhonePlaceholder')" />
              </div>
              <div class="field-group">
                <label class="field-label-plain">{{ t('donation.donorEmail') }}</label>
                <input type="email" v-model="donorForm.email" class="text-input" :placeholder="t('donation.donorEmailPlaceholder')" />
              </div>
            </div>
          </Transition>

          <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

          <button type="button" class="submit-btn" :disabled="!canSubmit || createDonation.loading" @click="submitDonation">
            {{ createDonation.loading ? t('donation.submitting') : `${t('donation.confirmDonate')} ${donationAmount || 0} ${t('donation.currency')}` }}
          </button>

          <p class="license-text">{{ t('donation.licenseText') }}</p>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { reactive, ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { createResource } from 'frappe-ui'
import { useLanguage } from '@/composables/useLanguage'
import { useDonationDialog } from '@/composables/useDonationDialog'

const { t, isRTL } = useLanguage()
const { isOpen, activeProject, closeDonationDialog } = useDonationDialog()

const viewportWidth = ref(window.innerWidth)
function updateViewportWidth() {
  viewportWidth.value = window.innerWidth
}
onMounted(() => window.addEventListener('resize', updateViewportWidth))
onUnmounted(() => window.removeEventListener('resize', updateViewportWidth))
const dialogPaddingTop = computed(() => (viewportWidth.value < 640 ? '24px' : '130px'))

const presetAmounts = [1000, 100, 50, 10]

const donationAmount = ref(0)
const isCustomAmount = ref(false)
const donationFrequency = ref('One-Time')
const errorMessage = ref('')

const donorForm = reactive({
  isAnonymous: false,
  fullName: '',
  phone: '',
  email: '',
})

function resetForm() {
  donationAmount.value = 0
  isCustomAmount.value = false
  donationFrequency.value = 'One-Time'
  errorMessage.value = ''
  donorForm.isAnonymous = false
  donorForm.fullName = ''
  donorForm.phone = ''
  donorForm.email = ''
}

watch(isOpen, (open) => {
  if (!open) resetForm()
})

function setPresetAmount(amount) {
  isCustomAmount.value = false
  donationAmount.value = amount
}

function activateCustomAmount() {
  isCustomAmount.value = true
  donationAmount.value = 0
}

function toggleFrequency(frequency) {
  donationFrequency.value = donationFrequency.value === frequency ? 'One-Time' : frequency
}

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

const createDonation = createResource({
  url: 'afif.donation_api.create_donation',
  onSuccess(data) {
    window.location.href = data.payment_url
  },
  onError(err) {
    errorMessage.value = extractError(err)
  },
})

const canSubmit = computed(
  () => !!activeProject.value?.name && !!donationAmount.value && donationAmount.value > 0
)

function submitDonation() {
  if (!canSubmit.value) return
  errorMessage.value = ''
  createDonation.submit({
    donation_project: activeProject.value.name,
    amount: donationAmount.value,
    donor_name: donorForm.isAnonymous ? null : donorForm.fullName || null,
    donor_mobile: donorForm.isAnonymous ? null : donorForm.phone || null,
    donor_email: donorForm.isAnonymous ? null : donorForm.email || null,
  })
}

function close() {
  closeDonationDialog()
}

function handleClose() {
  closeDonationDialog()
}
</script>

<style scoped>
.donation-dialog {
  @apply flex flex-col items-stretch;
  background: #ebf4ff;
  padding: 32px 20px;
  gap: 24px;
  animation: donation-dialog-in 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes donation-dialog-in {
  from {
    opacity: 0;
    transform: scale(0.96) translateY(12px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@media (min-width: 640px) {
  .donation-dialog {
    padding: 50px 40px;
    gap: 30px;
  }
}

.dialog-header {
  @apply flex items-center;
  gap: 12px;
}

.dialog-title {
  @apply flex-1;
  font-weight: 700;
  font-size: 20px;
  line-height: 32px;
  text-align: start;
  color: #0570b6;
}

@media (min-width: 640px) {
  .dialog-title {
    font-size: 24px;
  }
}

.close-btn {
  @apply flex items-center justify-center shrink-0 w-7 h-7 rounded-full transition-colors hover:bg-white/60;
  color: #3e4850;
}

.dialog-card {
  @apply w-full flex flex-col items-stretch;
  background: #ffffff;
  border: 1px solid #f3f3f3;
  border-radius: 24px;
  padding: 24px 20px;
  gap: 16px;
}

@media (min-width: 640px) {
  .dialog-card {
    border-radius: 32px;
    padding: 40px;
  }
}

.field-label {
  @apply flex items-center justify-start;
  gap: 2px;
  font-weight: 700;
  font-size: 16px;
  line-height: 20px;
  letter-spacing: 0.28px;
  color: #141d23;
}

.required-star {
  font-weight: 600;
  font-size: 14px;
  color: #ba1a1a;
}

.presets-row {
  @apply flex flex-wrap items-center justify-center gap-2 sm:gap-3;
}

.preset-btn {
  @apply flex-1 flex items-center justify-center transition-colors;
  min-width: 62px;
  padding: 10px 12px;
  background: #f8fafc;
  border: 1px solid #e1e1e1;
  box-shadow: 0 0 4px rgba(201, 231, 244, 0.25);
  border-radius: 12px;
  font-weight: 600;
  font-size: 14px;
  letter-spacing: 0.28px;
  color: #141d23;
}

.preset-btn.active {
  background: #0570b6;
  border-color: #0570b6;
  color: #ffffff;
}

@media (min-width: 640px) {
  .preset-btn {
    min-width: 70px;
    padding: 11px 16px;
  }
}

.amount-field {
  @apply flex flex-col items-stretch;
  gap: 16px;
}

.amount-input {
  @apply w-full outline-none transition-colors;
  padding: 11px 16px;
  background: #f8fafc;
  border: 1px solid #f3f3f3;
  border-radius: 12px;
  font-size: 16px;
  color: #141d23;
}

.amount-input:focus {
  border-color: #0570b6;
}

.amount-input:disabled {
  @apply opacity-70;
}

.text-left {
  text-align: left;
}

.no-admin-fee-badge {
  @apply self-center;
  padding: 12px 24px;
  background: #235977;
  border-radius: 57px;
  font-weight: 700;
  font-size: 14px;
  letter-spacing: 0.28px;
  color: #ffffff;
}

.frequency-row {
  @apply flex flex-col items-start;
  gap: 8px;
}

.frequency-toggle {
  @apply flex items-center;
  gap: 12px;
}

.frequency-label {
  font-weight: 700;
  font-size: 14px;
  letter-spacing: 0.28px;
  color: #141d23;
}

.radio-circle {
  @apply inline-block shrink-0;
  width: 20px;
  height: 20px;
  background: #ecf5fe;
  border: 1px solid #bdc8d1;
  border-radius: 19px;
  transition: background-color 0.15s, border-color 0.15s;
}

.radio-circle.checked {
  background: #0570b6;
  border-color: #0570b6;
  box-shadow: inset 0 0 0 3px #ecf5fe;
}

.frequency-desc {
  font-weight: 500;
  font-size: 14px;
  letter-spacing: 0.28px;
  color: #6b7280;
}

.checkbox-container {
  @apply flex items-center justify-start;
  gap: 12px;
}

.custom-checkbox {
  width: 20px;
  height: 20px;
  accent-color: #0570b6;
}

.checkbox-label {
  font-weight: 700;
  font-size: 14px;
  letter-spacing: 0.28px;
  color: #141d23;
}

.donor-fields {
  @apply flex flex-col items-stretch;
  gap: 20px;
}

.field-group {
  @apply flex flex-col items-stretch;
  gap: 4px;
}

.field-label-plain {
  font-weight: 700;
  font-size: 14px;
  letter-spacing: 0.28px;
  color: #3e4850;
  text-align: start;
}

.text-input {
  @apply w-full outline-none transition-colors;
  padding: 11px 16px;
  background: #f8fafc;
  border: 1px solid #f3f3f3;
  border-radius: 12px;
  font-size: 16px;
  color: #141d23;
}

.text-input:focus {
  border-color: #0570b6;
}

.error-text {
  @apply text-sm text-red-500;
}

.submit-btn {
  @apply w-full flex items-center justify-center transition-opacity;
  padding: 16px 20px;
  background: #00adef;
  border-radius: 12px;
  font-weight: 700;
  font-size: 14px;
  letter-spacing: 0.28px;
  color: #ffffff;
}

@media (min-width: 640px) {
  .submit-btn {
    padding: 20px 40px;
  }
}

.submit-btn:active {
  opacity: 0.9;
}

.submit-btn:disabled {
  @apply opacity-50 cursor-not-allowed;
}

.license-text {
  @apply text-center;
  font-weight: 700;
  font-size: 12px;
  line-height: 20px;
  letter-spacing: 0.28px;
  color: #6b7280;
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

<style>
/* Unscoped: targets frappe-ui's own DialogOverlay wrapper, which sits above
   this component's slot content and otherwise has no z-index, so the sticky
   navbar's z-50 paints over it. */
.dialog-overlay {
  z-index: 60;
}
</style>
