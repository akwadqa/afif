<template>
  <div class="min-h-screen w-full flex flex-col">
    <router-view class="flex-1" />
    <AppFooter />
  </div>
</template>

<script setup>
import AppFooter from '@/components/footer/AppFooter.vue'
</script>
