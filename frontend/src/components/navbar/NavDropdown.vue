<template>
  <div class="relative group">
    <button
      class="flex items-center gap-1.5 text-gray-700 hover:text-sky-600 transition-colors duration-200 text-base font-medium py-2 px-1"
      :class="isRTL ? 'flex-row-reverse' : 'flex-row'"
    >
      <span>{{ item.label }}</span>
      <svg
        v-if="item.children?.length"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="2.5"
        stroke="currentColor"
        class="w-3.5 h-3.5 shrink-0 text-gray-400 group-hover:text-sky-500 transition-transform duration-200 group-hover:rotate-180"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
      </svg>
    </button>

    <div
      v-if="item.children?.length"
      class="absolute top-full start-0 pt-1 hidden group-hover:block z-50 min-w-[200px]"
    >
      <div class="bg-white border border-gray-100 rounded-xl shadow-lg py-2">
        <a
          v-for="child in item.children"
          :key="child.key"
          href="#"
          class="block px-4 py-2.5 text-sm text-gray-700 hover:bg-sky-50 hover:text-sky-600 transition-colors"
        >
          {{ child.label }}
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useLanguage } from '@/composables/useLanguage'

defineProps({
  item: {
    type: Object,
    required: true,
  },
})

const { isRTL } = useLanguage()
</script>
