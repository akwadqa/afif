<template>
  <a href="https://afif.qa/" target="_blank" rel="noopener noreferrer" class="block shrink-0">
    <img
      v-if="!logoError"
      src="@/assets/images/afif.png"
      alt="Afif Charity"
      class="w-[120px] h-auto md:w-[195px] object-contain"
      @error="logoError = true"
    />
    <!-- Fallback shown until logo.png is placed in src/assets/images/ -->
    <div v-else class="w-[120px] h-[38px] md:w-[195px] md:h-[62px] flex items-center gap-2 md:gap-3">
      <svg viewBox="0 0 100 100" class="fill-current text-sky-500 w-[38px] h-[38px] md:w-[62px] md:h-[62px] shrink-0">
        <circle cx="50" cy="20" r="10" />
        <path d="M50,40 C25,40 15,65 20,90 C35,90 45,75 50,55 C55,75 65,90 80,90 C85,65 75,40 50,40 Z" />
      </svg>
      <div class="flex flex-col leading-tight">
        <span class="text-base md:text-xl font-bold text-sky-600">عفيف الخيرية</span>
        <span class="text-[8px] md:text-[10px] tracking-widest text-sky-400 font-semibold">AFIF CHARITY</span>
      </div>
    </div>
  </a>
</template>

<script setup>
import { ref } from 'vue'

const logoError = ref(false)
</script>
