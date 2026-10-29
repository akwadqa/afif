<template>
  <div class="flex items-center gap-6">
    <!-- All navigation links removed per client request; only Beneficiary Profile / My Requests remain, for logged-in users.
    <NavDropdown v-for="item in navItems" :key="item.key" :item="item" />
    -->
    <!-- Beneficiary Profile / My Requests links removed per client request; kept commented for future reference.
    <template v-if="session.isLoggedIn">
      <router-link
        v-for="item in loggedInItems"
        :key="item.routeName"
        :to="{ name: item.routeName }"
        class="text-gray-700 hover:text-[#005979] hover:underline transition-colors duration-200 text-base font-medium py-2 px-1"
      >
        {{ t(item.labelKey) }}
      </router-link>
    </template>
    -->
  </div>
</template>

<script setup>
import { computed } from 'vue'
import NavDropdown from './NavDropdown.vue'
import { useLanguage } from '@/composables/useLanguage'
import { navConfig } from '@/config/navConfig'
import { session } from '@/data/session'

const { t } = useLanguage()

function withLabels(item) {
  return {
    ...item,
    label: t(`nav.${item.key}`),
    children: (item.children ?? []).map(withLabels),
  }
}

const navItems = computed(() => [...navConfig].reverse().map(withLabels))

const loggedInItems = [
  { labelKey: 'sidebar.beneficiaryProfile', routeName: 'Home' },
  { labelKey: 'sidebar.request', routeName: 'Request' },
]
</script>
