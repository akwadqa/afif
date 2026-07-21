import { onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const GA_MEASUREMENT_ID = 'G-6DRX93RTW9'
const SCRIPT_ID = 'ga-gtag-script'

let gtagLoaded = false

function loadGtagScript() {
  if (document.getElementById(SCRIPT_ID)) {
    gtagLoaded = true
    return
  }

  window.dataLayer = window.dataLayer || []
  window.gtag = (...args) => window.dataLayer.push(args)

  const script = document.createElement('script')
  script.id = SCRIPT_ID
  script.async = true
  script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`
  document.head.appendChild(script)

  window.gtag('js', new Date())
  window.gtag('config', GA_MEASUREMENT_ID)
  gtagLoaded = true
}

function unloadGtagScript() {
  document.getElementById(SCRIPT_ID)?.remove()
  gtagLoaded = false
}

// Loads Google Analytics only while a component using this composable is mounted,
// so gtag never runs on routes outside the donation flow.
export function useGoogleAnalytics() {
  const route = useRoute()

  onMounted(loadGtagScript)
  onUnmounted(unloadGtagScript)

  watch(
    () => route.fullPath,
    (path) => {
      if (gtagLoaded) {
        window.gtag('event', 'page_view', { page_path: path })
      }
    },
  )
}
