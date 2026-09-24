<template>
  <div class="flex flex-col min-h-screen">
    <AppNavBar />
    <div class="flex flex-1 overflow-hidden relative">
      <main
        :class="[
          'flex-1 overflow-y-auto transition-[margin] duration-300',
          session.isLoggedIn && sidebarOpen ? (isRTL ? 'sm:mr-80' : 'sm:ml-80') : '',
        ]"
      >
        <router-view v-slot="{ Component, route }">
          <Transition name="page-fade" mode="out-in">
            <component :is="Component" :key="route.path" />
          </Transition>
        </router-view>
      </main>
      <AppSidebar v-if="session.isLoggedIn" />
    </div>
    <AppFooter />
    <DonationDialog />
  </div>
</template>

<script setup>
import AppNavBar from '@/components/navbar/AppNavBar.vue'
import AppFooter from '@/components/footer/AppFooter.vue'
import AppSidebar from '@/components/sidebar/AppSidebar.vue'
import DonationDialog from '@/components/donation/DonationDialog.vue'
import { useLanguage } from '@/composables/useLanguage'
import { useGoogleAnalytics } from '@/composables/useGoogleAnalytics'
import { useSidebar } from '@/composables/useSidebar'
import { session } from '@/data/session'

// Ensures language/dir is initialised when any page using this layout loads
const { isRTL } = useLanguage()
const { sidebarOpen } = useSidebar()

// This layout is only used by the /donate route, so GA is scoped to donations
useGoogleAnalytics()
</script>

<style scoped>
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
