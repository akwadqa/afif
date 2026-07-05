<template>
  <div
    class="relative"
    :class="isNested ? 'group/nested' : 'group/top'"
    :dir="isRTL ? 'rtl' : 'ltr'"
  >
    <a
      v-if="!item.children?.length"
      :href="item.route || '#'"
      target="_blank"
      rel="noopener"
      class="flex items-center gap-1.5 text-gray-700 hover:text-[#005979] hover:underline transition-colors duration-200 text-base font-medium py-2 px-1"
    >
      {{ item.label }}
    </a>
    <button
      v-else
      class="flex items-center gap-1.5 w-full text-gray-700 transition-colors duration-200 text-base font-medium py-2 px-1"
      :class="isNested ? 'justify-between px-4 py-2.5 text-sm hover:bg-[#005979] hover:text-white' : 'hover:text-[#005979] hover:underline'"
    >
      <span>{{ item.label }}</span>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="2.5"
        stroke="currentColor"
        :class="[
          'w-3.5 h-3.5 shrink-0 text-gray-400 transition-transform duration-200',
          isNested ? '-rotate-90 rtl:rotate-90 group-hover/nested:text-white' : 'group-hover/top:rotate-180 group-hover/top:text-[#005979]',
        ]"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
      </svg>
    </button>

    <div
      v-if="item.children?.length"
      :class="[
        'absolute hidden z-50 min-w-[220px]',
        isNested
          ? 'start-full top-0 ps-1 group-hover/nested:block'
          : 'start-0 top-full pt-1 group-hover/top:block',
      ]"
    >
      <div class="bg-white border border-gray-100 rounded-xl shadow-lg py-2">
        <template v-for="child in item.children" :key="child.key">
          <NavDropdown v-if="child.children?.length" :item="child" is-nested />
          <a
            v-else
            :href="child.route || '#'"
            target="_blank"
            rel="noopener"
            class="block px-4 py-2.5 text-sm text-gray-700 hover:bg-[#005979] hover:text-white transition-colors text-start"
          >
            {{ child.label }}
          </a>
        </template>
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
  isNested: {
    type: Boolean,
    default: false,
  },
})

const { isRTL } = useLanguage()
</script>
