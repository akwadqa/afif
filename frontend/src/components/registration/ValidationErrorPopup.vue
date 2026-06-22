<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/20 backdrop-blur-sm p-4 dir-rtl">

    <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden border border-gray-100 flex flex-col">

      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-50">
        <div class="flex items-center space-x-2 space-x-reverse text-red-500">
          <span class="text-lg font-bold font-arabic">خطأ</span>
          <div class="bg-red-50 rounded-full p-0.5">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
              <path fill-rule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12ZM12 8.25a.75.75 0 0 1 .75.75v3.75a.75.75 0 0 1-1.5 0V9a.75.75 0 0 1 .75-.75Zm0 6.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>

        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="px-8 py-6 text-right max-h-80 overflow-y-auto">
        <div class="space-y-4">
          <h3 class="text-lg font-bold text-gray-800 font-arabic">
            الحقول الإلزامية المطلوبة:
          </h3>
          <ul class="space-y-2 pr-2">
            <li
              v-for="field in missingFields"
              :key="field"
              class="flex items-start space-x-2 space-x-reverse text-gray-600 font-arabic text-sm"
            >
              <span class="w-1.5 h-1.5 bg-red-500 rounded-full flex-shrink-0 mt-1.5"></span>
              <span>{{ field }}</span>
            </li>
          </ul>
        </div>
      </div>

      <div class="px-6 py-4 bg-[#F0F7FC] border-t border-gray-50 flex items-center justify-end">
        <button
          @click="$emit('close')"
          class="bg-[#34B0EE] text-white px-10 py-2 rounded-xl font-bold font-arabic text-sm shadow-md shadow-sky-100 hover:opacity-90 active:scale-95 transition-all"
        >
          موافق
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
defineProps({
  missingFields: { type: Array, required: true },
})
defineEmits(['close'])
</script>

<style scoped>
.font-arabic {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
.dir-rtl {
  direction: rtl;
}
.shadow-2xl {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
}
</style>
