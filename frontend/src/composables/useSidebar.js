import { ref } from 'vue'

const sidebarOpen = ref(true)

export function useSidebar() {
  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }
  function closeSidebar() {
    sidebarOpen.value = false
  }
  return { sidebarOpen, toggleSidebar, closeSidebar }
}
