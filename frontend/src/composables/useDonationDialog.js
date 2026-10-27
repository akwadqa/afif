import { ref } from 'vue'
import router from '@/router'
import { isProjectClosed } from '@/data/donation'

// Shared across the whole /donate section - a single <DonationDialog /> instance
// lives in DefaultLayout.vue and any project card/detail page just calls
// openDonationDialog(project) to trigger it.
const isOpen = ref(false)
const activeProject = ref(null)

// The open project is mirrored in ?donate= so shared links reopen the dialog and
// GA's page_view (fired on every fullPath change) records which project a donation started from.
// replace, not push, so the back button doesn't step through dialog states.
function setDonateQuery(projectName) {
  const { donate, ...query } = router.currentRoute.value.query
  if (donate === (projectName || undefined)) return
  return router.replace({ query: projectName ? { ...query, donate: projectName } : query })
}

export function useDonationDialog() {
  function openDonationDialog(project) {
    if (isProjectClosed(project)) return
    activeProject.value = project
    isOpen.value = true
    setDonateQuery(project.name)
  }

  function closeDonationDialog() {
    isOpen.value = false
    setDonateQuery(null)
  }

  function openFromQuery(projects) {
    const projectName = router.currentRoute.value.query.donate
    if (!projectName || isOpen.value) return

    const project = projects.find((candidate) => candidate.name === projectName)
    if (project && !isProjectClosed(project)) openDonationDialog(project)
    else setDonateQuery(null)
  }

  return { isOpen, activeProject, openDonationDialog, closeDonationDialog, openFromQuery }
}
