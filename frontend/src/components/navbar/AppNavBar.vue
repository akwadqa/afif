<template>
  <header class="sticky top-0 z-50 w-full">
    <nav
      :dir="isRTL ? 'ltr' : 'rtl'"
      :class="[
        'bg-white border-b border-gray-100 shadow-sm h-[110px] flex items-center justify-between',
        isRTL ? 'pr-[50px] pl-4 md:pl-6' : 'pl-[50px] pr-4 md:pr-6',
      ]"
    >

      <!-- Start: Logo + Language toggle -->
      <div class="flex items-center gap-2 md:gap-4">
        <NavLogo />
        <LanguageToggle :class="session.isLoggedIn ? 'hidden md:flex' : 'flex'" />
        <!-- Donate Now link removed per client request; kept commented for future reference.
        <a
          :href="donateNowRoute"
          target="_blank"
          rel="noopener"
          class="bg-[#005979] text-white px-3 py-1.5 text-xs md:px-5 md:py-2 md:text-sm rounded-lg font-semibold hover:bg-[#004a66] transition-colors whitespace-nowrap"
        >
          {{ t('nav.donateNow') }}
        </a>
        -->
      </div>

      <!-- End: Nav links (desktop) + hamburger -->
      <div class="flex items-center gap-2">
        <NavLinks class="hidden md:flex" />

        <!-- Hamburger: toggles sidebar on md+, toggles mobile menu on small -->
        <button
          v-if="session.isLoggedIn"
          :class="[
            'p-1 md:p-2 rounded-lg transition-colors',
            isActive
              ? 'text-sky-600 bg-sky-50'
              : 'text-gray-600 hover:text-sky-600 hover:bg-sky-50',
          ]"
          aria-label="Toggle menu"
          @click="handleMenuToggle"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6 md:w-7 md:h-7">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
          </svg>
        </button>
      </div>

    </nav>

    <!-- Mobile menu -->
    <Transition name="slide-down">
      <MobileMenu v-if="menuOpen" @close="menuOpen = false" />
    </Transition>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import NavLogo from './NavLogo.vue'
import NavLinks from './NavLinks.vue'
import LanguageToggle from './LanguageToggle.vue'
import MobileMenu from './MobileMenu.vue'
import { useSidebar } from '@/composables/useSidebar'
import { useLanguage } from '@/composables/useLanguage'
import { session } from '@/data/session'
import { donateNowRoute } from '@/config/navConfig'

const { isRTL, t } = useLanguage()

const menuOpen = ref(false)
const { sidebarOpen, toggleSidebar } = useSidebar()

const isActive = computed(() => menuOpen.value || sidebarOpen.value)

function handleMenuToggle() {
  const isDesktop = window.matchMedia('(min-width: 768px)').matches
  if (isDesktop) {
    toggleSidebar()
    menuOpen.value = false
  } else {
    menuOpen.value = !menuOpen.value
  }
}
</script>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.slide-down-enter-from,
.slide-down-leave-to {
  transform: translateY(-6px);
  opacity: 0;
}
</style>
