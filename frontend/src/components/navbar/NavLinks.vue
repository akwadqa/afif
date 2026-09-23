<template>
  <div class="flex items-center gap-6">
    <!-- All navigation links removed per client request; kept commented for future reference.
    <NavDropdown v-for="item in navItems" :key="item.key" :item="item" />
    -->
  </div>
</template>

<script setup>
import { computed } from 'vue'
import NavDropdown from './NavDropdown.vue'
import { useLanguage } from '@/composables/useLanguage'
import { navConfig } from '@/config/navConfig'

const { t } = useLanguage()

function withLabels(item) {
  return {
    ...item,
    label: t(`nav.${item.key}`),
    children: (item.children ?? []).map(withLabels),
  }
}

const navItems = computed(() => [...navConfig].reverse().map(withLabels))
</script>
