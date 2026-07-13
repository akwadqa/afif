<template>
  <div
    class="min-h-screen flex items-center justify-center p-4 py-12"
    style="background: #EBF4FF;"
  >
    <DonationWelcome v-if="view === 'welcome'" @action="view = 'form'" />
    <DonationForm v-else-if="view === 'form'" @back="view = 'welcome'" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import DonationWelcome from '@/components/donation/DonationWelcome.vue'
import DonationForm from '@/components/donation/DonationForm.vue'

const view = ref('welcome')
</script>
