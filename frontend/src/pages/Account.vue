<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold text-gray-800">{{ t('sidebar.myAccount') }}</h1>
  </div>
</template>

<script setup>
import { useLanguage } from '@/composables/useLanguage'
const { t } = useLanguage()
</script>
