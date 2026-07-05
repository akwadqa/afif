<template>
  <footer
    class="w-full bg-[#00AEEF] text-white pt-16 pb-0 ps-6 pe-6 md:ps-16 md:pe-6 select-none"
    :dir="isRTL ? 'rtl' : 'ltr'"
  >
    <!-- Main 3-column layout: Links (start) | Sub-menu (middle) | Image (end) -->
    <div
      class="max-w-7xl mx-auto flex flex-col md:flex-row md:items-end gap-6 md:gap-4"
      @mouseleave="activeMenu = null"
    >

      <!-- Column 1: Navigation Links + Social Icons -->
      <div class="flex flex-col items-center md:items-start md:self-center space-y-6 min-w-[180px] shrink-0">
        <nav class="flex flex-col items-center md:items-start space-y-3 text-lg font-medium w-full">
          <template v-for="item in navItems" :key="item.key">
            <div v-if="item.children.length" class="w-full flex flex-col items-center md:items-start">
              <button
                @click="toggleMenu(item.key)"
                @mouseenter="activeMenu = item.key"
                class="flex items-center gap-2 px-3 py-1.5 rounded transition-colors focus:outline-none"
                :class="{ 'bg-[#005979]': activeMenu === item.key }"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                  class="w-3 h-3 transition-transform duration-200"
                  :class="{ 'rotate-180': activeMenu === item.key }"
                >
                  <path d="M12 15l-6-6h12z" />
                </svg>
                <span>{{ item.label }}</span>
              </button>

              <!-- Mobile inline sub-menu -->
              <Transition name="expand">
                <div
                  v-if="activeMenu === item.key"
                  class="md:hidden flex flex-col items-center space-y-1 mt-2"
                >
                  <template v-for="child in item.children" :key="child.key">
                    <div v-if="child.children.length" class="flex flex-col items-center">
                      <button
                        @click="toggleSubMenu(child.key)"
                        class="flex items-center gap-2 hover:bg-[#005979] active:bg-[#005979] px-3 py-2 text-sm font-medium rounded transition-colors"
                        :class="{ 'bg-[#005979]': activeSubMenu === child.key }"
                      >
                        <span>{{ child.label }}</span>
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          fill="currentColor"
                          viewBox="0 0 24 24"
                          class="w-2.5 h-2.5 transition-transform duration-200"
                          :class="{ 'rotate-180': activeSubMenu === child.key }"
                        >
                          <path d="M12 15l-6-6h12z" />
                        </svg>
                      </button>
                      <Transition name="expand">
                        <div v-if="activeSubMenu === child.key" class="flex flex-col items-center space-y-1 mt-1">
                          <a
                            v-for="grandchild in child.children"
                            :key="grandchild.key"
                            :href="grandchild.route || '#'"
                            class="hover:bg-[#005979] active:bg-[#005979] px-5 py-2 text-sm font-medium rounded transition-colors"
                          >
                            {{ grandchild.label }}
                          </a>
                        </div>
                      </Transition>
                    </div>
                    <a
                      v-else
                      :href="child.route || '#'"
                      class="hover:bg-[#005979] active:bg-[#005979] px-3 py-2 text-sm font-medium rounded transition-colors"
                    >
                      {{ child.label }}
                    </a>
                  </template>
                </div>
              </Transition>
            </div>

            <a
              v-else
              :href="item.route || '#'"
              class="hover:text-opacity-80 transition-opacity md:ps-5"
            >
              {{ item.label }}
            </a>
          </template>
        </nav>

        <!-- Social Media Icons -->
        <div class="flex items-center gap-2.5 pt-2">
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

      <!-- Column 2: Desktop sub-menu panel (middle) -->
      <div class="hidden md:flex self-center items-start justify-center min-w-[200px]">
        <template v-for="item in navItems" :key="item.key">
          <div
            v-if="activeMenu === item.key && item.children.length"
            class="flex flex-col space-y-1"
          >
            <template v-for="child in item.children" :key="child.key">
              <div v-if="child.children.length" class="relative group/nested">
                <span
                  class="flex items-center justify-between gap-3 hover:bg-[#005979] px-4 py-2.5 text-sm font-medium rounded transition-colors cursor-default whitespace-nowrap"
                >
                  <span>{{ child.label }}</span>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke-width="2.5"
                    stroke="currentColor"
                    class="w-3 h-3 shrink-0 -rotate-90 rtl:rotate-90"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                  </svg>
                </span>
                <div
                  class="absolute hidden group-hover/nested:flex flex-col start-full top-0 ps-1 min-w-[180px] z-50"
                >
                  <a
                    v-for="grandchild in child.children"
                    :key="grandchild.key"
                    :href="grandchild.route || '#'"
                    class="hover:bg-[#005979] px-4 py-2 text-sm font-medium rounded transition-colors whitespace-nowrap"
                  >
                    {{ grandchild.label }}
                  </a>
                </div>
              </div>
              <a
                v-else
                :href="child.route || '#'"
                class="hover:bg-[#005979] px-4 py-2.5 font-medium text-sm rounded transition-colors"
              >
                {{ child.label }}
              </a>
            </template>
          </div>
        </template>
      </div>

      <!-- Column 3: Illustration image (end side, flush to bottom) -->
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
import { ref, computed } from 'vue'
import { useLanguage } from '@/composables/useLanguage'
import { navConfig } from '@/config/navConfig'

const { t, isRTL } = useLanguage()

function withLabels(item) {
  return {
    ...item,
    label: t(`nav.${item.key}`),
    children: (item.children ?? []).map(withLabels),
  }
}

const navItems = computed(() => navConfig.map(withLabels))

const activeMenu = ref(null)
const activeSubMenu = ref(null)

const toggleMenu = (menuName) => {
  activeMenu.value = activeMenu.value === menuName ? null : menuName
  activeSubMenu.value = null
}

const toggleSubMenu = (menuName) => {
  activeSubMenu.value = activeSubMenu.value === menuName ? null : menuName
}
</script>

<style scoped>
.expand-enter-active,
.expand-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
