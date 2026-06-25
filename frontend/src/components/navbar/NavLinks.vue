<template>
  <div class="flex items-center gap-2">
    <NavDropdown v-for="item in navItems" :key="item.key" :item="item" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import NavDropdown from './NavDropdown.vue'
import { useLanguage } from '@/composables/useLanguage'
import { navConfig } from '@/config/navConfig'

const { t } = useLanguage()

const navItems = computed(() =>
  [...navConfig].reverse().map((item) => ({
    ...item,
    label: t(`nav.${item.key}`),
    children: item.children.map((child) => ({
      ...child,
      label: t(`nav.${child.key}`),
    })),
  }))
)
</script>
