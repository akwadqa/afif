<template>
  <footer
    class="w-full bg-[#00AEEF] text-white pt-16 pb-0 ps-6 pe-6 md:ps-16 md:pe-6 select-none"
    :dir="isRTL ? 'rtl' : 'ltr'"
  >
    <!-- 2-column layout: Social media (start) | Image (end) -->
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row md:items-end gap-6 md:gap-4">

      <!-- Column 1: Social media -->
      <div class="flex flex-col items-center md:items-start md:self-center space-y-4 min-w-[180px] shrink-0">
        <p class="text-lg font-medium text-center md:text-start">{{ t('footer.followUs') }}</p>

        <div class="flex items-center gap-2.5">
          <a href="https://www.threads.net/@afifqatar?igshid=MzRlODBiNWFlZA==" target="_blank" class="w-7 h-7 rounded-full bg-black/30 flex items-center justify-center hover:bg-black/50 transition-colors" aria-label="Threads">
            <span class="text-xs font-bold font-sans">@</span>
          </a>
          <a href="https://www.instagram.com/afifqatar/" target="_blank" class="w-7 h-7 rounded-full bg-black/30 flex items-center justify-center hover:bg-black/50 transition-colors" aria-label="Instagram">
            <svg fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" class="w-4 h-4"><rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37zM17.5 6.5h.01"/></svg>
          </a>
          <a href="https://www.youtube.com/afifprog" target="_blank" class="w-7 h-7 rounded-full bg-black/30 flex items-center justify-center hover:bg-black/50 transition-colors" aria-label="YouTube">
            <svg fill="currentColor" viewBox="0 0 24 24" class="w-4 h-4"><path d="M23.498 6.163a3.003 3.003 0 0 0-2.11-2.11C19.53 3.545 12 3.545 12 3.545s-7.53 0-9.388.508a3.003 3.003 0 0 0-2.11 2.11C0 8.022 0 12 0 12s0 3.978.502 5.837a3.003 3.003 0 0 0 2.11 2.11c1.858.507 9.388.507 9.388.507s7.53 0 9.388-.507a3.003 3.003 0 0 0 2.11-2.11C24 15.978 24 12 24 12s0-3.978-.502-5.837zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
          </a>
          <a href="https://twitter.com/AfifQatar" target="_blank" class="w-7 h-7 rounded-full bg-black/30 flex items-center justify-center hover:bg-black/50 transition-colors" aria-label="X / Twitter">
            <svg fill="currentColor" viewBox="0 0 24 24" class="w-3.5 h-3.5"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
          </a>
          <a href="https://www.facebook.com/afifqatar/" target="_blank" class="w-7 h-7 rounded-full bg-black/30 flex items-center justify-center hover:bg-black/50 transition-colors" aria-label="Facebook">
            <svg fill="currentColor" viewBox="0 0 24 24" class="w-4 h-4"><path d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z"/></svg>
          </a>
        </div>
      </div>

      <!-- Column 2: Illustration image (end side, flush to bottom) -->
      <div class="hidden md:flex items-end justify-end shrink-0 self-end md:ms-auto">
        <img
          src="@/assets/images/image.png"
          alt=""
          class="block w-[620px] h-auto object-contain"
        />
      </div>

    </div>

    <!-- Mobile image: flush to bottom -->
    <div class="md:hidden flex justify-center">
      <img
        src="@/assets/images/image.png"
        alt=""
        class="block w-full max-w-[480px] h-auto object-contain opacity-40"
      />
    </div>
  </footer>
</template>

<script setup>
import { useLanguage } from '@/composables/useLanguage'

const { t, isRTL } = useLanguage()
</script>
