<template>
  <div class="min-h-screen flex items-center justify-center p-4 py-12" style="background: #EBF4FF;">
    <div class="result-card" :dir="isRTL ? 'rtl' : 'ltr'">
      <div v-if="checking" class="py-10 text-center">
        <svg class="animate-spin w-8 h-8 text-[#34B0EE] mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
        </svg>
        <p class="text-gray-500">{{ t('donation.success.checkingTitle') }}</p>
      </div>

      <template v-else>
        <div class="badge-icon">
          <svg v-if="statusKey === 'paid'" viewBox="0 0 186 186" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="successBadgeGradient" x1="15%" y1="0%" x2="85%" y2="100%">
                <stop offset="28.01%" stop-color="#BBE6A8" />
                <stop offset="56.48%" stop-color="#38B502" />
                <stop offset="75.03%" stop-color="#319F01" />
                <stop offset="93.52%" stop-color="#2D9101" />
                <stop offset="100%" stop-color="#2B8C01" />
              </linearGradient>
            </defs>
            <circle cx="93" cy="93" r="88" fill="url(#successBadgeGradient)" />
            <path d="M56 96 82 122 132 68" fill="none" stroke="#FFFFFF" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <svg v-else-if="statusKey === 'pending'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="#d97706" class="w-24 h-24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
          </svg>
          <svg v-else viewBox="0 0 186 186" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="failureBadgeGradient" x1="10%" y1="0%" x2="90%" y2="100%">
                <stop offset="19.78%" stop-color="#E68C7A" />
                <stop offset="46.32%" stop-color="#FA0303" />
                <stop offset="54.59%" stop-color="#EA0A02" />
                <stop offset="69.59%" stop-color="#D21502" />
                <stop offset="83.6%" stop-color="#C41C01" />
                <stop offset="100%" stop-color="#BF1E01" />
              </linearGradient>
            </defs>
            <circle cx="93" cy="93" r="88" fill="url(#failureBadgeGradient)" />
            <path d="M65 65 121 121M121 65 65 121" fill="none" stroke="#FFFFFF" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </div>

        <h2 class="result-title" :class="titleClass">{{ statusTitle }}</h2>
        <p class="result-message">{{ statusMessage }}</p>

        <div v-if="donation" class="donation-summary" dir="ltr">
          <div class="summary-row">
            <span>{{ t('donation.success.amountLabel') }}</span>
            <span class="summary-value">{{ donation.amount }} {{ donation.currency || t('donation.currency') }}</span>
          </div>
          <div v-if="donation.donor_name" class="summary-row">
            <span>{{ t('donation.success.donorLabel') }}</span>
            <span class="summary-value">{{ donation.donor_name }}</span>
          </div>
          <div class="summary-row">
            <span>{{ t('donation.success.referenceLabel') }}</span>
            <span class="summary-value font-mono">{{ referenceId }}</span>
          </div>
        </div>

        <div class="actions-col">
          <router-link v-if="statusKey !== 'paid'" to="/donate" class="action-btn action-btn-primary">
            <span>{{ t('donation.success.tryAgain') }}</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-[22px] h-[22px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
            </svg>
          </router-link>
          <router-link
            to="/"
            class="action-btn"
            :class="statusKey === 'paid' ? 'action-btn-primary' : 'action-btn-secondary'"
          >
            <span>{{ t('donation.success.backHome') }}</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-[22px] h-[22px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
            </svg>
          </router-link>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { createResource } from 'frappe-ui'
import { useLanguage } from '@/composables/useLanguage'

const { t, isRTL } = useLanguage()
const route = useRoute()

const referenceId = computed(() => route.query.ref || '')
const checking = ref(true)
const notFound = ref(false)
const donation = ref(null)

const POLL_INTERVAL_MS = 3000
const MAX_POLLS = 5
let pollCount = 0
let pollTimer = null

const statusResource = createResource({
  url: 'afif.donation_api.get_status',
  method: 'GET',
  onSuccess(data) {
    donation.value = data
    if (data.payment_status === 'Pending' && pollCount < MAX_POLLS) {
      pollCount += 1
      pollTimer = setTimeout(fetchStatus, POLL_INTERVAL_MS)
    } else {
      checking.value = false
    }
  },
  onError() {
    notFound.value = true
    checking.value = false
  },
})

function fetchStatus() {
  statusResource.submit({ reference_id: referenceId.value })
}

onMounted(() => {
  if (!referenceId.value) {
    notFound.value = true
    checking.value = false
    return
  }
  fetchStatus()
})

onBeforeUnmount(() => {
  if (pollTimer) clearTimeout(pollTimer)
})

const statusKey = computed(() => {
  if (notFound.value) return 'not-found'
  if (donation.value?.payment_status === 'Paid') return 'paid'
  if (donation.value?.payment_status === 'Failed') return 'failed'
  return 'pending'
})

const titleClass = computed(() => ({
  'title-success': statusKey.value === 'paid',
  'title-pending': statusKey.value === 'pending',
  'title-failed': statusKey.value === 'failed' || statusKey.value === 'not-found',
}))

const statusTitle = computed(() => {
  switch (statusKey.value) {
    case 'paid': return t('donation.success.paidTitle')
    case 'pending': return t('donation.success.pendingTitle')
    case 'failed': return t('donation.success.failedTitle')
    default: return t('donation.success.notFoundTitle')
  }
})

const statusMessage = computed(() => {
  switch (statusKey.value) {
    case 'paid': return t('donation.success.paidMessage')
    case 'pending': return t('donation.success.pendingMessage')
    case 'failed': return t('donation.success.failedMessage')
    default: return t('donation.success.notFoundMessage')
  }
})
</script>

<style scoped>
.result-card {
  @apply w-full flex flex-col items-center text-center;
  max-width: 809px;
  background: #ffffff;
  border-radius: 32px;
  padding: 36px 24px;
  gap: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

@media (min-width: 640px) {
  .result-card {
    padding: 50px 64px;
    gap: 30px;
  }
}

.badge-icon {
  @apply flex items-center justify-center shrink-0;
  width: 120px;
  height: 120px;
}

.badge-icon svg {
  @apply w-full h-full;
}

@media (min-width: 640px) {
  .badge-icon {
    width: 150px;
    height: 150px;
  }
}

.result-title {
  font-weight: 500;
  font-size: 26px;
  line-height: 1.25;
}

@media (min-width: 640px) {
  .result-title {
    font-size: 32px;
  }
}

.title-success {
  color: #14903a;
}

.title-pending {
  color: #d97706;
}

.title-failed {
  color: #c94545;
}

.result-message {
  max-width: 509px;
  font-weight: 400;
  font-size: 16px;
  line-height: 1.55;
  color: #3e4850;
}

@media (min-width: 640px) {
  .result-message {
    font-size: 20px;
  }
}

.donation-summary {
  @apply w-full bg-gray-50 rounded-xl p-4 text-sm text-gray-600 space-y-2;
}

.summary-row {
  @apply flex justify-between;
}

.summary-value {
  @apply font-semibold text-gray-800;
}

.actions-col {
  @apply w-full flex flex-col items-stretch;
  gap: 16px;
  max-width: 550px;
}

.action-btn {
  @apply w-full flex items-center justify-center transition-opacity hover:opacity-90 active:scale-[0.99];
  height: 60px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 18px;
  letter-spacing: -0.35px;
  gap: 8px;
}

.action-btn-primary {
  background: #34b0ee;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.25);
  color: #ffffff;
}

.action-btn-secondary {
  background: #ffffff;
  border: 1px solid #d3d3d3;
  box-shadow: 0 3px 4px rgba(0, 0, 0, 0.07);
  color: #0284c7;
}
</style>
