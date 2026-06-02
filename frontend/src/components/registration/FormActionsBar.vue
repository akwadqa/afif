<template>
  <div
    class="bg-white rounded-[32px] px-4 md:px-6 py-4 border border-gray-100 shadow-sm flex items-center justify-between gap-2"
    :dir="isRTL ? 'rtl' : 'ltr'"
  >
    <!-- Back button -->
    <button
      @click="$emit('prev')"
      :disabled="currentStep === 1"
      class="border border-gray-100 text-gray-400 hover:text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:hover:bg-transparent disabled:hover:text-gray-400 px-3 md:px-5 py-2.5 rounded-xl text-xs md:text-sm font-medium flex items-center gap-1 transition-all shrink-0"
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="w-3.5 h-3.5 shrink-0">
        <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
      </svg>
      <span class="hidden xs:inline sm:inline">{{ t('registration.back') }}</span>
    </button>

    <!-- Step dots -->
    <div class="flex items-center gap-1 md:gap-1.5">
      <div
        v-for="i in totalSteps"
        :key="i"
        :class="[
          'h-1 rounded-full transition-all duration-300',
          currentStep === i ? 'w-6 md:w-8 bg-[#34B0EE]' : 'w-3 md:w-4 bg-gray-100'
        ]"
      ></div>
    </div>

    <!-- Next / Submit button -->
    <button
      @click="$emit('next')"
      :disabled="loading"
      class="text-white font-medium text-xs md:text-sm py-2.5 px-4 md:px-8 rounded-xl shadow-md transition-all hover:opacity-95 active:scale-[0.98] disabled:opacity-60 flex items-center gap-2 shrink-0"
      style="background-color: #34B0EE;"
    >
      <svg v-if="loading" class="animate-spin w-4 h-4 shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
      </svg>
      {{ currentStep === totalSteps ? t('registration.submit') : t('registration.next') }}
    </button>
  </div>
</template>

<script setup>
import { useLanguage } from '@/composables/useLanguage'

defineProps({
  currentStep: Number,
  totalSteps: Number,
  loading: { type: Boolean, default: false },
})
defineEmits(['next', 'prev'])

const { t, isRTL } = useLanguage()
</script>
