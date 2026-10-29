import { ref } from 'vue'
import router from '@/router'
import { isProjectClosed } from '@/data/donation'

// Shared across the whole /donate section - a single <DonationDialog /> instance
// lives in DefaultLayout.vue and any project card/detail page just calls
// openDonationDialog(project) to trigger it.
const isOpen = ref(false)
const activeProject = ref(null)
// Opened from the landing page: keeps the landing behind the dialog and remembers its query to restore on close
const isOverLanding = ref(false)
let landingQuery = {}

// The open dialog shows as ?project=<slug>&donate=1 so a shared link reopens it on the project page,
// and GA's page_view (fired on every fullPath change) records who started donating.
// replace, not push, so the back button doesn't step through dialog states.
export function useDonationDialog() {
  function openDonationDialog(project) {
    if (isProjectClosed(project)) return
    activeProject.value = project
    isOpen.value = true

    const { query } = router.currentRoute.value
    if (query.project === project.slug && query.donate === '1') return
    isOverLanding.value = !query.project
    if (isOverLanding.value) landingQuery = query
    // A project link carries no category; other params (e.g. utm_*) are kept
    const { category, ...rest } = query
    return router.replace({ query: { ...rest, project: project.slug, donate: '1' } })
  }

  async function closeDonationDialog() {
    isOpen.value = false

    const { donate, ...query } = router.currentRoute.value.query
    await router.replace({ query: isOverLanding.value ? landingQuery : query })
    // Only after ?project= is gone, otherwise the project page flashes in behind the closing dialog
    isOverLanding.value = false
    landingQuery = {}
  }

  function openFromQuery(projects) {
    const { project: slug, donate } = router.currentRoute.value.query
    if (donate !== '1' || isOpen.value) return

    const project = projects.find((candidate) => candidate.slug === slug)
    if (project && !isProjectClosed(project)) {
      openDonationDialog(project)
    } else {
      const { donate: _donate, ...query } = router.currentRoute.value.query
      router.replace({ query })
    }
  }

  return { isOpen, isOverLanding, activeProject, openDonationDialog, closeDonationDialog, openFromQuery }
}
