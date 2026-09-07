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
      <div class="rounded-[32px] md:rounded-l-none flex max-w-[1155px] w-full overflow-hidden min-h-[420px] lg:min-h-[580px]">
        <LoginLeftPanel />
        <ResetPasswordFormPanel />
      </div>
    </div>
  </div>
</template>

<script setup>
import bgImg from '@/assets/images/background.png'
import AppNavBar from '@/components/navbar/AppNavBar.vue'
import LoginLeftPanel from '@/components/auth/LoginLeftPanel.vue'
import ResetPasswordFormPanel from '@/components/auth/ResetPasswordFormPanel.vue'
</script>
