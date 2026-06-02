<template>
  <div class="bg-white rounded-[32px] p-6 border border-gray-100 shadow-sm flex items-center justify-between relative overflow-hidden" :dir="isRTL ? 'rtl' : 'ltr'">
    <div v-for="(step, index) in steps" :key="step.number" class="flex-1 flex items-center relative z-10">
      <div class="flex items-center space-x-3 space-x-reverse">
        <div
          :class="[
            'w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm transition-all',
            currentStep === step.number
              ? 'bg-[#34B0EE] text-white ring-4 ring-sky-100'
              : currentStep > step.number ? 'bg-sky-500 text-white' : 'bg-gray-100 text-gray-400'
          ]"
        >
          <svg v-if="currentStep > step.number" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="w-4 h-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
          </svg>
          <span v-else>{{ step.number }}</span>
        </div>
        <span
          :class="[
            'text-sm font-medium hidden md:inline',
            currentStep === step.number ? 'text-sky-600 font-bold' : 'text-gray-400'
          ]"
        >
          {{ step.label }}
        </span>
      </div>
      <div
        v-if="index !== steps.length - 1"
        class="flex-1 h-[2px] mx-4 min-w-[30px] transition-colors duration-300"
        :class="currentStep > step.number ? 'bg-sky-400' : 'bg-gray-100'"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { useLanguage } from '@/composables/useLanguage'

defineProps({ currentStep: Number, steps: Array })
const { isRTL } = useLanguage()
</script>
