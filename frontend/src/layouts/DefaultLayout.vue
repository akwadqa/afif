<template>
  <div class="min-h-screen flex flex-col">
    <AppNavBar />
    <main class="flex-1">
      <slot />
    </main>
    <AppFooter />
  </div>
</template>

<script setup>
import AppNavBar from '@/components/navbar/AppNavBar.vue'
import AppFooter from '@/components/footer/AppFooter.vue'
import { useLanguage } from '@/composables/useLanguage'

// Ensures language/dir is initialised when any page using this layout loads
useLanguage()
</script>
