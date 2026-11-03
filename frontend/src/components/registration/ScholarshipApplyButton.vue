<template>
  <div class="relative group">
    <button
      :disabled="!canApply"
      @click="emit('apply')"
      class="bg-[#34B0EE] text-white hover:opacity-90 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100"
    >
      {{ t('scholarship.applyAgain') }}
    </button>
    <div
      v-if="blockReason"
      class="absolute top-full mt-2 bg-gray-800 text-white text-xs rounded-lg px-3 py-2 w-64 max-w-xs opacity-0 group-hover:opacity-100 transition-opacity z-10 shadow-lg"
      :class="isRTL ? 'left-0' : 'right-0'"
    >
      {{ t(`myRequests.disabledReasons.${blockReason}`) }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useLanguage } from '@/composables/useLanguage'
import { useAccountStatus } from '@/composables/useAccountStatus'
import { getRequestBlockReason } from '@/components/request/requestEligibility'

// The status of a submitted scholarship registration.
const props = defineProps({
  status: { type: String, required: true },
})
const emit = defineEmits(['apply'])

const { t, isRTL } = useLanguage()
const { isRestricted } = useAccountStatus()

// A scholarship student's earlier requests never block a new one (P15-1); the server enforces the rules again.
const blockReason = computed(() =>
  getRequestBlockReason([], {
    isAccepted: props.status === 'Accepted',
    isScholarship: true,
    isRestricted: isRestricted.value,
  }),
)
const canApply = computed(() => !blockReason.value)
</script>
