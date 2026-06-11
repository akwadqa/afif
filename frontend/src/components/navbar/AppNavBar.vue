<template>
  <header class="relative z-50 w-full">
    <nav class="bg-white border-b border-gray-100 shadow-sm h-[110px] pl-[50px] pr-[50px] md:pr-[100px] flex items-center justify-between">

      <!-- Left: Logo + Language toggle -->
      <div class="flex items-center gap-6">
        <NavLogo />
        <LanguageToggle class="hidden md:flex" />
      </div>

      <!-- Right: Nav links (desktop) + profile toggle + mobile hamburger -->
      <div class="flex items-center gap-2">
        <NavLinks class="hidden md:flex" />

        <!-- Profile / Sidebar toggle (only when logged in) -->
        <button
          v-if="session.isLoggedIn"
          :class="[
            'p-2 rounded-lg transition-colors',
            sidebarOpen
              ? 'text-sky-600 bg-sky-50'
              : 'text-gray-600 hover:text-sky-600 hover:bg-sky-50',
          ]"
          aria-label="الملف الشخصي"
          @click="toggleSidebar"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17.982 18.725A7.488 7.488 0 0 0 12 15.75a7.488 7.488 0 0 0-5.982 2.975m11.963 0a9 9 0 1 0-11.963 0m11.963 0A8.966 8.966 0 0 1 12 21a8.966 8.966 0 0 1-5.982-2.275M15 9.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
          </svg>
        </button>

        <!-- Mobile: hamburger for nav menu -->
        <button
          class="md:hidden p-2 rounded-lg text-gray-600 hover:text-sky-600 hover:bg-sky-50 transition-colors"
          :aria-expanded="menuOpen"
          aria-label="Toggle menu"
          @click="menuOpen = !menuOpen"
        >
          <svg v-if="!menuOpen" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
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
import { ref } from 'vue'
import NavLogo from './NavLogo.vue'
import NavLinks from './NavLinks.vue'
import LanguageToggle from './LanguageToggle.vue'
import MobileMenu from './MobileMenu.vue'
import { useSidebar } from '@/composables/useSidebar'
import { session } from '@/data/session'

const menuOpen = ref(false)
const { sidebarOpen, toggleSidebar } = useSidebar()
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
