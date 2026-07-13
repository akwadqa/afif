<template>
  <div class="min-h-screen flex items-center justify-center p-4 py-12" style="background: #EBF4FF;">
    <div
      class="bg-white shadow-xl max-w-xl w-full p-8 md:p-12 flex flex-col items-center justify-center text-center"
      style="border-radius: 32px;"
      :dir="isRTL ? 'rtl' : 'ltr'"
    >
      <div v-if="checking" class="py-10">
        <svg class="animate-spin w-8 h-8 text-[#34B0EE] mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
        </svg>
        <p class="text-gray-500">{{ t('donation.success.checkingTitle') }}</p>
      </div>

      <template v-else>
        <div class="w-24 h-24 rounded-2xl flex items-center justify-center mb-6" :class="iconWrapClass">
          <svg v-if="statusKey === 'paid'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="#10b981" class="w-12 h-12">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
          </svg>
          <svg v-else-if="statusKey === 'pending'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="#d97706" class="w-12 h-12">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="#ef4444" class="w-12 h-12">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 9.75l4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
          </svg>
        </div>

        <h2 class="text-2xl font-bold mb-4" :class="titleClass">{{ statusTitle }}</h2>
        <p class="text-gray-500 text-base leading-relaxed max-w-md mb-8">{{ statusMessage }}</p>

        <div v-if="donation" class="w-full bg-gray-50 rounded-xl p-4 mb-8 text-sm text-gray-600 space-y-2">
          <div class="flex justify-between">
            <span>{{ t('donation.success.amountLabel') }}</span>
            <span class="font-semibold text-gray-800">{{ donation.amount }} {{ donation.currency || t('donation.currency') }}</span>
          </div>
          <div v-if="donation.donor_name" class="flex justify-between">
            <span>{{ t('donation.success.donorLabel') }}</span>
            <span class="font-semibold text-gray-800">{{ donation.donor_name }}</span>
          </div>
          <div class="flex justify-between" dir="ltr">
            <span>{{ t('donation.success.referenceLabel') }}</span>
            <span class="font-mono text-xs text-gray-500">{{ referenceId }}</span>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
          <router-link
            v-if="statusKey !== 'paid'"
            to="/donate"
            class="min-w-[200px] flex items-center justify-center text-white py-3.5 px-6 rounded-xl font-medium shadow-md transition-all hover:opacity-90 active:scale-[0.99]"
            style="background-color: #34B0EE;"
          >
            {{ t('donation.success.tryAgain') }}
          </router-link>
          <router-link
            to="/"
            class="min-w-[200px] flex items-center justify-center border border-gray-200 text-gray-600 py-3.5 px-6 rounded-xl font-medium transition-all hover:bg-gray-50"
          >
            {{ t('donation.success.backHome') }}
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

const iconWrapClass = computed(() => ({
  'bg-green-50': statusKey.value === 'paid',
  'bg-amber-50': statusKey.value === 'pending',
  'bg-red-50': statusKey.value === 'failed' || statusKey.value === 'not-found',
}))

const titleClass = computed(() => ({
  'text-green-600': statusKey.value === 'paid',
  'text-amber-600': statusKey.value === 'pending',
  'text-red-600': statusKey.value === 'failed' || statusKey.value === 'not-found',
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
