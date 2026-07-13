<template>
  <div
    class="bg-white shadow-xl max-w-xl w-full p-8 md:p-12 flex flex-col items-center justify-center text-center"
    style="border-radius: 32px;"
    :dir="isRTL ? 'rtl' : 'ltr'"
  >

    <div class="w-24 h-24 bg-sky-50 rounded-2xl flex items-center justify-center mb-6">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="#34B0EE" class="w-12 h-12">
        <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
      </svg>
    </div>

    <h2 class="text-2xl font-bold text-sky-600 mb-4">
      {{ title || t('donation.title') }}
    </h2>

    <p class="text-gray-500 text-base leading-relaxed max-w-md mb-8">
      {{ description || t('donation.description') }}
    </p>

    <button
      @click="$emit('action')"
      class="w-full sm:w-auto min-w-[240px] flex items-center justify-center gap-2 text-white py-3.5 px-6 rounded-xl font-medium shadow-md transition-all hover:opacity-90 active:scale-[0.99] mb-6"
      style="background-color: #34B0EE;"
    >
      <slot name="button-icon">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5 shrink-0">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
        </svg>
      </slot>
      <span>{{ buttonText || t('donation.donateNow') }}</span>
    </button>

  </div>
</template>

<script setup>
import { useLanguage } from '@/composables/useLanguage'

defineProps({
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  buttonText: { type: String, default: '' },
})
defineEmits(['action'])

const { t, isRTL } = useLanguage()
</script>
