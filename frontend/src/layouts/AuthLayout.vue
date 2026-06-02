<template>
  <div class="flex flex-col">
    <router-view />
    <AppFooter />
  </div>
</template>

<script setup>
import AppFooter from '@/components/footer/AppFooter.vue'
</script>
