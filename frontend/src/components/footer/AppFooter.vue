<template>
  <footer
    class="w-full bg-white py-12 px-6 md:px-16 border-t border-[#D3D3D3] relative z-40"
    dir="rtl"
  >
    <div class="max-w-7xl mx-auto">

      <div class="grid grid-cols-1 md:grid-cols-3 gap-10 md:gap-8 pb-10 text-right">

        <div class="flex flex-col space-y-4 md:items-start">
          <div class="h-14 w-auto flex items-center justify-start">
            <img
              src="@/assets/images/Logo Footer.png"
              alt="Afif Charity Logo"
              class="h-full object-contain"
            />
          </div>
          <p class="text-sm text-[#3E4850] leading-relaxed max-w-sm">
            مؤسسة قطرية خيرية رائدة في مجال التنمية المستدامة والتمكين الاجتماعي.
          </p>
        </div>

        <div class="flex flex-col space-y-3 text-right">
          <h4 class="text-base font-bold text-[#3E4850] mb-1">من نحن</h4>
          <ul class="space-y-2.5 text-sm text-[#3E4850]">
            <li><a href="#" class="hover:text-sky-500 transition-colors">برامجنا</a></li>
            <li><a href="#" class="hover:text-sky-500 transition-colors">منحة الشيخ خالد بن ناصر</a></li>
            <li><a href="#" class="hover:text-sky-500 transition-colors">مبادراتنا</a></li>
            <li><a href="#" class="hover:text-sky-500 transition-colors">المركز الإعلامي</a></li>
          </ul>
        </div>

        <div class="flex flex-col space-y-4 text-right">
          <h4 class="text-base font-bold text-[#3E4850] mb-1">تواصل معنا</h4>

          <div class="space-y-3 text-sm text-[#3E4850]">
            <a href="tel:8001111" class="flex items-center gap-2 hover:text-sky-500 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 text-[#3E4850] shrink-0">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 0 0 2.25-2.25V16.19c0-.609-.372-1.155-.917-1.391L17.167 13.53a2.25 2.25 0 0 0-2.25.15c-.642.513-1.428.832-2.288.832-.86 0-1.646-.319-2.288-.832a2.25 2.25 0 0 0-2.25-.15L4.747 14.8c-.545.236-.917.782-.917 1.391v2.31c0 1.242 1.008 2.25 2.25 2.25h2.25Z" />
              </svg>
              <span>800 1111</span>
            </a>

            <a href="mailto:info@afif.org.qa" class="flex items-center gap-2 hover:text-sky-500 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 text-[#3E4850] shrink-0">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25H4.5A2.25 2.25 0 0 1 2.25 17.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5H4.5a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75" />
              </svg>
              <span>info@afif.org.qa</span>
            </a>
          </div>

          <div class="flex items-center gap-4 pt-2 text-[#3E4850]">
            <a href="#" class="hover:text-sky-500 transition-colors" aria-label="X / Twitter">
              <svg fill="currentColor" viewBox="0 0 24 24" class="w-5 h-5"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
            </a>
            <a href="#" class="hover:text-sky-500 transition-colors" aria-label="Facebook">
              <svg fill="currentColor" viewBox="0 0 24 24" class="w-5 h-5"><path d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z"/></svg>
            </a>
            <a href="#" class="hover:text-sky-500 transition-colors" aria-label="Instagram">
              <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" class="w-5 h-5"><rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37zM17.5 6.5h.01"/></svg>
            </a>
            <a href="#" class="hover:text-sky-500 transition-colors" aria-label="YouTube">
              <svg fill="currentColor" viewBox="0 0 24 24" class="w-5 h-5"><path d="M23.498 6.163a3.003 3.003 0 0 0-2.11-2.11C19.53 3.545 12 3.545 12 3.545s-7.53 0-9.388.508a3.003 3.003 0 0 0-2.11 2.11C0 8.022 0 12 0 12s0 3.978.502 5.837a3.003 3.003 0 0 0 2.11 2.11c1.858.507 9.388.507 9.388.507s7.53 0 9.388-.507a3.003 3.003 0 0 0 2.11-2.11C24 15.978 24 12 24 12s0-3.978-.502-5.837zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
            </a>
          </div>
        </div>

      </div>

      <div class="border-t border-[#D3D3D3] pt-6 text-center text-xs text-[#3E4850]">
        © {{ currentYear }} مؤسسة عفيف الخيرية. جميع الحقوق محفوظة.
      </div>
    </div>
  </footer>
</template>

<script setup>
const currentYear = new Date().getFullYear()
</script>
