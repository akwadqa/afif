<template>
  <div>
    <button
      v-if="item.children?.length"
      @click="open = !open"
      :class="[
        'w-full flex items-center justify-between transition-colors group',
        nested
          ? 'py-2 px-3 text-sm text-gray-600 hover:bg-[#005979] hover:text-white rounded-lg'
          : 'py-3.5 text-gray-700 hover:text-[#005979] hover:underline font-medium text-sm',
      ]"
    >
      <span>{{ item.label }}</span>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="2"
        stroke="currentColor"
        class="w-4 h-4 shrink-0 transition-transform duration-200 text-gray-400 group-hover:text-white"
        :class="{ 'rotate-180': open }"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
      </svg>
    </button>

    <a
      v-else
      :href="item.route || '#'"
      target="_blank"
      rel="noopener"
      @click="$emit('close')"
      :class="[
        'transition-colors',
        nested
          ? 'block py-2 px-3 text-sm text-gray-600 hover:bg-[#005979] hover:text-white rounded-lg'
          : 'flex py-3.5 text-gray-700 hover:text-[#005979] hover:underline font-medium text-sm',
      ]"
    >
      {{ item.label }}
    </a>

    <Transition name="expand">
      <div v-if="item.children?.length && open" class="pb-2 ps-3 flex flex-col gap-0.5">
        <MobileMenuItem
          v-for="child in item.children"
          :key="child.key"
          :item="child"
          nested
          @close="$emit('close')"
        />
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  item: {
    type: Object,
    required: true,
  },
  nested: {
    type: Boolean,
    default: false,
  },
})
defineEmits(['close'])

const open = ref(false)
</script>

<style scoped>
.expand-enter-active,
.expand-leave-active {
  transition: max-height 0.2s ease, opacity 0.15s ease;
  max-height: 300px;
  overflow: hidden;
}
.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>
