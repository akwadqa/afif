import { ref } from 'vue'
import router from '@/router'
import { isProjectClosed } from '@/data/donation'

// Shared across the whole /donate section - a single <DonationDialog /> instance
// lives in DefaultLayout.vue and any project card/detail page just calls
// openDonationDialog(project) to trigger it.
const isOpen = ref(false)
const activeProject = ref(null)
// The landing filter, hidden while the dialog is open so a shared link carries only the project
let hiddenCategory = null

// The open project is mirrored in ?donate=<slug> so shared links reopen the dialog and
// GA's page_view (fired on every fullPath change) records which project a donation started from.
// replace, not push, so the back button doesn't step through dialog states.
function replaceQuery(query) {
  return router.replace({ query })
}

export function useDonationDialog() {
  function openDonationDialog(project) {
    if (isProjectClosed(project)) return
    activeProject.value = project
    isOpen.value = true

    const { category, donate, ...query } = router.currentRoute.value.query
    hiddenCategory = category || null
    if (category || donate !== project.slug) replaceQuery({ ...query, donate: project.slug })
  }

  function closeDonationDialog() {
    isOpen.value = false

    const { donate, ...query } = router.currentRoute.value.query
    replaceQuery(hiddenCategory ? { ...query, category: hiddenCategory } : query)
    hiddenCategory = null
  }

  function openFromQuery(projects) {
    const slug = router.currentRoute.value.query.donate
    if (!slug || isOpen.value) return

    const project = projects.find((candidate) => candidate.slug === slug)
    if (project && !isProjectClosed(project)) {
      openDonationDialog(project)
    } else {
      const { donate, ...query } = router.currentRoute.value.query
      replaceQuery(query)
    }
  }

  return { isOpen, activeProject, openDonationDialog, closeDonationDialog, openFromQuery }
}
