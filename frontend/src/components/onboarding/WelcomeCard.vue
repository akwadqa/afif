<template>
  <div
    class="bg-white shadow-xl max-w-xl w-full p-8 md:p-12 flex flex-col items-center justify-center text-center"
    style="border-radius: 32px;"
    :dir="isRTL ? 'rtl' : 'ltr'"
  >

    <div class="w-24 h-24 bg-sky-50 rounded-2xl flex items-center justify-center mb-6">
      <span class=" select-none animate-bounce-slow" style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">👋</span>
    </div>

    <h2 class="text-2xl font-bold text-sky-600 mb-4">
      {{ title || t('welcome.title') }}
    </h2>

    <p class="text-gray-500 text-base leading-relaxed max-w-md mb-8">
      {{ description || t('welcome.description') }}
    </p>

    <button
      @click="$emit('action')"
      class="w-full sm:w-auto min-w-[240px] flex items-center justify-center gap-2 text-white py-3.5 px-6 rounded-xl font-medium shadow-md transition-all hover:opacity-90 active:scale-[0.99] mb-6"
      style="background-color: #34B0EE;"
    >
      <slot name="button-icon">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5 shrink-0">
          <path stroke-linecap="round" stroke-linejoin="round" d="M18 7.5v3m0 0v3m0-3h3m-3 0h-3m-2.25-4.125a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0ZM3 19.235v-.11a6.375 6.375 0 0 1 12.75 0v.109A12.318 12.318 0 0 1 9.374 21c-2.331 0-4.512-.645-6.374-1.766Z" />
        </svg>
      </slot>
      <span>{{ buttonText || t('welcome.createProfile') }}</span>
    </button>

    <a
      href="#"
      class="flex items-center gap-1.5 text-xs text-sky-600 font-semibold hover:underline transition-all"
      @click.prevent="$emit('link-action')"
    >
      <span>{{ linkText || t('welcome.termsLink') }}</span>
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="w-3.5 h-3.5 shrink-0">
        <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
      </svg>
    </a>

  </div>
</template>

<script setup>
import { useLanguage } from '@/composables/useLanguage'

defineProps({
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  buttonText: { type: String, default: '' },
  linkText: { type: String, default: '' },
})
defineEmits(['action', 'link-action'])

const { t, isRTL } = useLanguage()
</script>

<style scoped>
.animate-bounce-slow {
  animation: bounce-slow 3s infinite;
}

@keyframes bounce-slow {
  0%, 100% {
    transform: translateY(0);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: translateY(-5px);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
}
</style>
