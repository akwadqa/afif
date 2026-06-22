<template>
  <div class="bg-white border-b border-gray-100 shadow-md md:hidden">
    <div class="px-4 py-2 flex flex-col">

      <!-- Nav links -->
      <div v-for="item in navItems" :key="item.key">
        <button
          v-if="item.children?.length"
          @click="toggle(item.key)"
          class="w-full flex items-center justify-between py-3.5 text-gray-700 hover:text-sky-600 transition-colors font-medium text-sm"
        >
          <span>{{ item.label }}</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="2"
            stroke="currentColor"
            class="w-4 h-4 transition-transform duration-200 text-gray-400"
            :class="{ 'rotate-180': open.includes(item.key) }"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
          </svg>
        </button>

        <a
          v-else
          href="#"
          @click.prevent="$emit('close')"
          class="flex py-3.5 text-gray-700 hover:text-sky-600 transition-colors font-medium text-sm"
        >
          {{ item.label }}
        </a>

        <Transition name="expand">
          <div v-if="item.children?.length && open.includes(item.key)" class="pb-2 ps-3 flex flex-col gap-0.5">
            <a
              v-for="child in item.children"
              :key="child.key"
              href="#"
              @click.prevent="$emit('close')"
              class="block py-2 px-3 text-sm text-gray-600 hover:text-sky-600 hover:bg-sky-50 rounded-lg transition-colors"
            >
              {{ child.label }}
            </a>
          </div>
        </Transition>
      </div>

      <!-- Language toggle -->
      <div class="py-3">
        <button
          @click="toggleLanguage"
          class="flex items-center gap-2 text-gray-600 hover:text-sky-600 transition-colors text-sm font-medium"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 text-sky-500 shrink-0">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 0 1 7.843 4.582M12 3a8.997 8.997 0 0 0-7.843 4.582m15.686 0A11.953 11.953 0 0 1 12 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0 1 21 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0 1 12 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 0 1 3 12c0-.778.099 1.533-.284 2.253" />
          </svg>
          <span>{{ t('nav.switchLang') }}</span>
        </button>
      </div>

      <!-- Divider + Sidebar items (when logged in) -->
      <template v-if="session.isLoggedIn">
        <div class="border-t border-gray-200 my-1"></div>
        <div class="pt-2 pb-1">
          <span class="px-1 text-xs font-semibold text-gray-400 uppercase tracking-wide">{{ displayName }}</span>
        </div>
        <router-link
          v-for="item in sidebarItems"
          :key="item.routeName"
          :to="{ name: item.routeName }"
          custom
          v-slot="{ navigate, isActive }"
        >
          <button
            @click="() => { navigate(); $emit('close') }"
            :class="[
              'w-full flex items-center gap-3 py-3 text-sm font-medium transition-colors',
              isActive ? 'text-sky-600' : 'text-gray-700 hover:text-sky-600',
            ]"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" v-html="item.svgPath" />
            <span>{{ t(item.labelKey) }}</span>
          </button>
        </router-link>
        <button
          @click="handleLogout"
          :disabled="session.logout.loading"
          class="w-full flex items-center gap-3 py-3 text-sm font-medium text-red-500 hover:text-red-600 transition-colors disabled:opacity-60"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 9V5.25A2.25 2.25 0 0 1 10.5 3h6a2.25 2.25 0 0 1 2.25 2.25v13.5A2.25 2.25 0 0 1 16.5 21h-6a2.25 2.25 0 0 1-2.25-2.25V15m-3 0-3-3m0 0 3-3m-3 3H15" />
          </svg>
          <span>{{ t('sidebar.logout') }}</span>
        </button>
      </template>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useLanguage } from '@/composables/useLanguage'
import { navConfig } from '@/config/navConfig'
import { session } from '@/data/session'

defineEmits(['close'])

const { t, toggleLanguage } = useLanguage()

const navItems = computed(() =>
  navConfig.map((item) => ({
    ...item,
    label: t(`nav.${item.key}`),
    children: item.children.map((child) => ({
      ...child,
      label: t(`nav.${child.key}`),
    })),
  }))
)

const displayName = computed(() => {
  const user = session.user
  if (!user) return ''
  return user.includes('@') ? user.split('@')[0] : user
})

const sidebarItems = [
  {
    labelKey: 'sidebar.beneficiaryProfile',
    routeName: 'Home',
    svgPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M17.982 18.725A7.488 7.488 0 0 0 12 15.75a7.488 7.488 0 0 0-5.982 2.975m11.963 0a9 9 0 1 0-11.963 0m11.963 0A8.966 8.966 0 0 1 12 21a8.966 8.966 0 0 1-5.982-2.275M15 9.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />',
  },
  {
    labelKey: 'sidebar.request',
    routeName: 'Request',
    svgPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />',
  },
]

const open = ref([])

function toggle(key) {
  const idx = open.value.indexOf(key)
  idx === -1 ? open.value.push(key) : open.value.splice(idx, 1)
}

function handleLogout() {
  session.logout.submit()
}
</script>

<style scoped>
.expand-enter-active,
.expand-leave-active {
  transition: max-height 0.2s ease, opacity 0.15s ease;
  max-height: 300px;
  overflow: hidden;
}
.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>
