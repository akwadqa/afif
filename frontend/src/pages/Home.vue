<template>

  <!-- Welcome / onboarding state -->
  <div
    v-if="view === 'welcome'"
    class="relative flex-1 flex items-center justify-center p-4 py-8 min-h-screen"
  >
    <img
      :src="bgImg"
      alt=""
      aria-hidden="true"
      fetchpriority="high"
      class="absolute inset-0 w-full h-full object-cover -z-10 select-none pointer-events-none"
    />
    <WelcomeCard @create-profile="view = 'registration'" />
  </div>

  <!-- Multi-step beneficiary registration -->
  <BeneficiaryRegistration
    v-else-if="view === 'registration'"
    @submitted="view = 'dashboard'"
  />

  <!-- Dashboard (placeholder until implemented) -->
  <div v-else class="max-w-3xl py-12 mx-auto">
    <!-- dashboard content goes here -->
  </div>

</template>

<script setup>
import { ref } from 'vue'
import bgImg from '@/assets/images/background.png'
import WelcomeCard from '@/components/onboarding/WelcomeCard.vue'
import BeneficiaryRegistration from '@/components/registration/BeneficiaryRegistration.vue'

const view = ref('welcome')
</script>
