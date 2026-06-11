<template>
  <div class="flex flex-col min-h-screen">
    <AppNavBar />
    <main class="flex-1 overflow-y-auto">
      <router-view />
    </main>
    <AppSidebar />
    <AppFooter />
  </div>
</template>

<script setup>
import AppNavBar from '@/components/navbar/AppNavBar.vue'
import AppFooter from '@/components/footer/AppFooter.vue'
import AppSidebar from '@/components/sidebar/AppSidebar.vue'
import { useLanguage } from '@/composables/useLanguage'

useLanguage()
</script>
