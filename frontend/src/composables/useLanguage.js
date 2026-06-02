import { ref, computed, watch } from 'vue'
import translations from '@/locales/translations.js'

const currentLang = ref(localStorage.getItem('afif_lang') || 'ar')

watch(currentLang, (lang) => {
  document.documentElement.lang = lang
})
document.documentElement.lang = currentLang.value

export function useLanguage() {
  const isRTL = computed(() => currentLang.value === 'ar')

  function toggleLanguage() {
    currentLang.value = currentLang.value === 'ar' ? 'en' : 'ar'
    localStorage.setItem('afif_lang', currentLang.value)
  }

  function t(path) {
    const keys = path.split('.')
    let val = translations[currentLang.value]
    for (const key of keys) {
      val = val?.[key]
    }
    return val ?? path
  }

  return { currentLang, isRTL, toggleLanguage, t }
}
