<template>
  <aside
    :dir="isRTL ? 'rtl' : 'ltr'"
    :class="[
      'hidden md:flex flex-col bg-white transition-transform duration-300 z-30',
      'absolute top-0 bottom-0 shadow-2xl',
      'w-80',
      isRTL ? 'right-0' : 'left-0',
      sidebarOpen ? 'translate-x-0' : (isRTL ? 'translate-x-full' : '-translate-x-full'),
      isRTL ? 'border-l border-gray-100' : 'border-r border-gray-100',
    ]"
  >
    <!-- Header -->
    <div
      :class="[
        'flex items-center gap-3 px-5 py-4 border-b border-gray-100',
        isRTL ? 'flex-row' : 'flex-row-reverse',
      ]"
    >
      <!-- Avatar -->
      <div class="w-10 h-10 bg-sky-50 rounded-full flex items-center justify-center text-sky-600 shrink-0">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M17.982 18.725A7.488 7.488 0 0 0 12 15.75a7.488 7.488 0 0 0-5.982 2.975m11.963 0a9 9 0 1 0-11.963 0m11.963 0A8.966 8.966 0 0 1 12 21a8.966 8.966 0 0 1-5.982-2.275M15 9.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
        </svg>
      </div>
      <!-- Name -->
      <h2 class="flex-1 text-base font-bold text-gray-800 truncate">{{ displayName }}</h2>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-2 py-6 space-y-1 overflow-y-auto">
      <router-link
        v-for="item in menuItems"
        :key="item.routeName"
        :to="{ name: item.routeName }"
        custom
        v-slot="{ navigate, isActive }"
      >
        <button
          @click="navigate"
          :class="[
            'w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors relative',
            isRTL ? 'flex-row' : 'flex-row-reverse',
            isActive
              ? 'bg-sky-50 text-sky-600 font-semibold'
              : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700',
          ]"
        >
          <!-- Active indicator — right edge in RTL, left edge in LTR -->
          <div
            v-if="isActive"
            :class="[
              'absolute inset-y-0 w-1 bg-sky-500',
              isRTL ? 'right-0 rounded-l-full' : 'left-0 rounded-r-full',
            ]"
          />
          <!-- Icon -->
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
          <!-- Label -->
          <span class="flex-1 text-sm text-start">{{ t(item.labelKey) }}</span>
        </button>
      </router-link>
    </nav>

    <!-- Logout — pinned to bottom -->
    <div class="px-2 pt-3 pb-4 border-t border-gray-100">
      <button
        @click="handleLogout"
        :disabled="session.logout.loading"
        :class="[
          'w-full flex items-center gap-3 px-4 py-3 text-red-500 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-60',
          isRTL ? 'flex-row' : 'flex-row-reverse',
        ]"
      >
        <!-- Icon -->
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 9V5.25A2.25 2.25 0 0 1 10.5 3h6a2.25 2.25 0 0 1 2.25 2.25v13.5A2.25 2.25 0 0 1 16.5 21h-6a2.25 2.25 0 0 1-2.25-2.25V15m-3 0-3-3m0 0 3-3m-3 3H15" />
        </svg>
        <!-- Label -->
        <span class="flex-1 text-sm font-semibold text-start">{{ t('sidebar.logout') }}</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { useLanguage } from '@/composables/useLanguage'
import { useSidebar } from '@/composables/useSidebar'
import { useBeneficiaryName } from '@/composables/useBeneficiaryName'
import { session } from '@/data/session'

const { t, isRTL } = useLanguage()
const { sidebarOpen, closeSidebar } = useSidebar()
const { displayName } = useBeneficiaryName()

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
]

function handleLogout() {
  session.logout.submit()
  closeSidebar()
}
</script>

