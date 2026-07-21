<template>
  <div class="min-h-screen flex flex-col">
    <AppNavBar />
    <main class="flex-1">
      <router-view />
    </main>
    <AppFooter />
  </div>
</template>

<script setup>
import AppNavBar from '@/components/navbar/AppNavBar.vue'
import AppFooter from '@/components/footer/AppFooter.vue'
import { useLanguage } from '@/composables/useLanguage'
import { useGoogleAnalytics } from '@/composables/useGoogleAnalytics'

// Ensures language/dir is initialised when any page using this layout loads
useLanguage()

// This layout is only used by the /donate route, so GA is scoped to donations
useGoogleAnalytics()
</script>
