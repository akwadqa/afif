<template>
  <div class="relative min-h-screen w-full flex flex-col">

    <img
      :src="bgImg"
      alt=""
      aria-hidden="true"
      fetchpriority="high"
      loading="eager"
      class="absolute inset-0 w-full h-full object-cover -z-10 select-none pointer-events-none"
    />

    <AppNavBar />

    <div class="flex-1 flex items-center justify-center p-4 py-8">
      <div class="bg-white rounded-3xl shadow-xl flex max-w-4xl w-full overflow-hidden min-h-[580px]" style="border-radius:10px">
        <LoginLeftPanel />
        <RegisterFormPanel />
      </div>
    </div>
  </div>
</template>

<script setup>
import bgImg from '@/assets/images/background.png'
import AppNavBar from '@/components/navbar/AppNavBar.vue'
import LoginLeftPanel from '@/components/auth/LoginLeftPanel.vue'
import RegisterFormPanel from '@/components/auth/RegisterFormPanel.vue'
</script>
