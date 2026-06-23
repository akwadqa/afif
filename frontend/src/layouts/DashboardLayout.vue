<template>
  <div class="flex flex-col min-h-screen">
    <AppNavBar />
    <div class="flex flex-1 overflow-hidden relative">
      <main
        :class="[
          'flex-1 overflow-y-auto transition-[margin] duration-300',
          sidebarOpen ? (isRTL ? 'sm:mr-80' : 'sm:ml-80') : '',
        ]"
      >
        <router-view />
      </main>
      <AppSidebar />
    </div>
    <AppFooter />
  </div>
</template>

<script setup>
import AppNavBar from '@/components/navbar/AppNavBar.vue'
import AppFooter from '@/components/footer/AppFooter.vue'
import AppSidebar from '@/components/sidebar/AppSidebar.vue'
import { useLanguage } from '@/composables/useLanguage'
import { useSidebar } from '@/composables/useSidebar'

const { isRTL } = useLanguage()
const { sidebarOpen } = useSidebar()
</script>
