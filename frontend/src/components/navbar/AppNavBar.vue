<template>
  <header class="relative z-50 w-full">
    <nav class="bg-white border-b border-gray-100 shadow-sm h-[110px] pl-[50px] pr-[50px] md:pr-[100px] flex items-center justify-between">

      <!-- Left: Logo + Language toggle -->
      <div class="flex items-center gap-6">
        <NavLogo />
        <LanguageToggle class="hidden md:flex" />
      </div>

      <!-- Right: Nav links (desktop) -->
      <NavLinks class="hidden md:flex" />

      <!-- Mobile: hamburger -->
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

const menuOpen = ref(false)
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
