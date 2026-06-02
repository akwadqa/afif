<template>
  <!-- Mobile backdrop -->
  <Transition name="fade">
    <div
      v-if="mobileOpen"
      class="fixed inset-0 bg-black/30 z-20 md:hidden"
      @click="$emit('close')"
    />
  </Transition>

  <aside
    dir="rtl"
    :class="[
      'flex flex-col bg-white border-l border-gray-100 transition-all duration-300 z-30',
      'fixed inset-y-0 right-0 md:static md:inset-auto md:h-full',
      mobileOpen ? 'translate-x-0 shadow-2xl' : 'translate-x-full md:translate-x-0',
      collapsed ? 'w-64 md:w-14' : 'w-64',
    ]"
  >
    <!-- Header -->
    <div
      class="flex items-center gap-2 border-b border-gray-50 transition-all duration-300"
      :class="collapsed ? 'p-3' : 'px-5 py-4'"
    >
      <!-- Avatar (first in DOM = right in RTL) -->
      <div class="w-10 h-10 bg-sky-50 rounded-full flex items-center justify-center text-sky-600 shrink-0">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M17.982 18.725A7.488 7.488 0 0 0 12 15.75a7.488 7.488 0 0 0-5.982 2.975m11.963 0a9 9 0 1 0-11.963 0m11.963 0A8.966 8.966 0 0 1 12 21a8.966 8.966 0 0 1-5.982-2.275M15 9.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
        </svg>
      </div>
      <!-- Name: visible on mobile always; hidden on desktop when collapsed -->
      <h2 :class="['flex-1 text-base font-bold text-gray-800 truncate', collapsed ? 'md:hidden' : '']">
        {{ displayName }}
      </h2>
      <!-- Desktop collapse/expand toggle -->
      <button
        class="hidden md:flex items-center justify-center w-7 h-7 rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors shrink-0"
        @click="collapsed = !collapsed"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <!-- collapsed → double-chevron left (expand outward) -->
          <path v-if="collapsed" stroke-linecap="round" stroke-linejoin="round" d="m18.75 4.5-7.5 7.5 7.5 7.5m-6-15L5.25 12l7.5 7.5" />
          <!-- expanded → double-chevron right (collapse inward) -->
          <path v-else stroke-linecap="round" stroke-linejoin="round" d="m5.25 4.5 7.5 7.5-7.5 7.5m6-15 7.5 7.5-7.5 7.5" />
        </svg>
      </button>
      <!-- Mobile close button -->
      <button
        class="md:hidden flex items-center justify-center w-8 h-8 rounded-lg text-gray-400 hover:bg-gray-100 transition-colors shrink-0"
        @click="$emit('close')"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-2 py-6 space-y-1">
      <router-link
        v-for="item in menuItems"
        :key="item.routeName"
        :to="{ name: item.routeName }"
        custom
        v-slot="{ navigate, isActive }"
      >
        <div class="relative group">
          <button
            @click="navigate"
            :class="[
              'w-full flex items-center rounded-lg transition-colors relative',
              collapsed ? 'justify-center px-2 py-3' : 'justify-between px-4 py-3',
              isActive
                ? 'bg-sky-50 text-sky-600 font-semibold'
                : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700',
            ]"
          >
            <!-- Active indicator on RIGHT -->
            <div v-if="isActive" class="absolute right-0 inset-y-0 w-1 bg-sky-500 rounded-l-full" />
            <!-- Icon (first in DOM = right in RTL) -->
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-5 h-5 shrink-0"
              :class="isActive ? 'text-sky-600' : 'text-gray-400'"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="1.5"
              v-html="item.svgPath"
            />
            <!-- Label (second in DOM = left in RTL); hidden on desktop when collapsed -->
            <span :class="['text-sm', collapsed ? 'md:hidden' : '']">{{ t(item.labelKey) }}</span>
          </button>
          <!-- Hover tooltip (desktop collapsed only) -->
          <div
            v-if="collapsed"
            class="absolute top-1/2 -translate-y-1/2 bg-gray-900 text-white text-xs px-2.5 py-1.5 rounded-md whitespace-nowrap pointer-events-none z-50 opacity-0 group-hover:opacity-100 transition-opacity hidden md:block"
            style="right: calc(100% + 8px);"
          >
            {{ t(item.labelKey) }}
          </div>
        </div>
      </router-link>
    </nav>

    <!-- Logout -->
    <div class="px-2 pt-3 pb-4 border-t border-gray-50">
      <div class="relative group">
        <button
          @click="handleLogout"
          :disabled="session.logout.loading"
          :class="[
            'w-full flex items-center text-red-500 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-60',
            collapsed ? 'justify-center px-2 py-3' : 'justify-between px-4 py-3',
          ]"
        >
          <!-- Icon (right in RTL, first in DOM) -->
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 9V5.25A2.25 2.25 0 0 1 10.5 3h6a2.25 2.25 0 0 1 2.25 2.25v13.5A2.25 2.25 0 0 1 16.5 21h-6a2.25 2.25 0 0 1-2.25-2.25V15m-3 0-3-3m0 0 3-3m-3 3H15" />
          </svg>
          <!-- Label (left in RTL, second in DOM) -->
          <span :class="['text-sm font-semibold', collapsed ? 'md:hidden' : '']">{{ t('sidebar.logout') }}</span>
        </button>
        <!-- Hover tooltip (desktop collapsed only) -->
        <div
          v-if="collapsed"
          class="absolute top-1/2 -translate-y-1/2 bg-gray-900 text-white text-xs px-2.5 py-1.5 rounded-md whitespace-nowrap pointer-events-none z-50 opacity-0 group-hover:opacity-100 transition-opacity hidden md:block"
          style="right: calc(100% + 8px);"
        >
          {{ t('sidebar.logout') }}
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref } from 'vue'
import { session } from '@/data/session'
import { useLanguage } from '@/composables/useLanguage'

defineProps({ mobileOpen: { type: Boolean, default: false } })
defineEmits(['close'])

const { t } = useLanguage()
const collapsed = ref(false)

const displayName = computed(() => {
  const user = session.user
  if (!user) return ''
  return user.includes('@') ? user.split('@')[0] : user
})

const menuItems = [
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
  {
    labelKey: 'sidebar.myAccount',
    routeName: 'Account',
    svgPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />',
  },
]

function handleLogout() {
  session.logout.submit()
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
