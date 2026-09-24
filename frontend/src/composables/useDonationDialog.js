import { ref } from 'vue'

// Shared across the whole /donate section - a single <DonationDialog /> instance
// lives in DefaultLayout.vue and any project card/detail page just calls
// openDonationDialog(project) to trigger it.
const isOpen = ref(false)
const activeProject = ref(null)

export function useDonationDialog() {
  function openDonationDialog(project) {
    activeProject.value = project
    isOpen.value = true
  }

  function closeDonationDialog() {
    isOpen.value = false
  }

  return { isOpen, activeProject, openDonationDialog, closeDonationDialog }
}
