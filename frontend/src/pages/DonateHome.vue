<template>
  <DonationProjectDetail v-if="isProjectView" />
  <Donate v-else />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Donate from '@/pages/Donate.vue'
import DonationProjectDetail from '@/pages/DonationProjectDetail.vue'
import { useDonationDialog } from '@/composables/useDonationDialog'

const route = useRoute()
const { isOverLanding } = useDonationDialog()

// ?project= shows the project page, like ?category= filters the landing page.
// A dialog opened from the landing page also sets ?project=, but the landing stays behind it.
const isProjectView = computed(() => !!route.query.project && !isOverLanding.value)
</script>
