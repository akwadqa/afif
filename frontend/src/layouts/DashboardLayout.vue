<template>
  <div class="flex flex-col min-h-screen">
    <AppNavBar />
    <!-- Mobile sidebar toggle strip (hidden on desktop) -->
    <div class="md:hidden bg-white border-b border-gray-100 px-4 py-2 flex justify-end items-center">
      <button
        @click="mobileOpen = !mobileOpen"
        class="p-2 rounded-lg text-gray-600 hover:text-sky-600 hover:bg-sky-50 transition-colors"
        aria-label="فتح القائمة الجانبية"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
        </svg>
      </button>
    </div>
    <div class="flex flex-1 overflow-hidden">
      <main class="flex-1 overflow-y-auto">
        <router-view />
      </main>
      <AppSidebar :mobile-open="mobileOpen" @close="mobileOpen = false" />
    </div>
    <AppFooter />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppNavBar from '@/components/navbar/AppNavBar.vue'
import AppFooter from '@/components/footer/AppFooter.vue'
import AppSidebar from '@/components/sidebar/AppSidebar.vue'
import { useLanguage } from '@/composables/useLanguage'

useLanguage()
const mobileOpen = ref(false)
</script>
