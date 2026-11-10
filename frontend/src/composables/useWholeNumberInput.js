import { ref } from 'vue'
import { arabicToWestern } from '@/utils/inputHelpers'

// Keeps an amount input to Western digits and owns the warning shown when anything else was typed.
export function useWholeNumberInput() {
  const isWarningShown = ref(false)

  function filterInput(event) {
    const digits = arabicToWestern(event.target.value)
    const value = digits.replace(/[^0-9]/g, '')
    event.target.value = value
    // Stays until the field is emptied, or the next digit would hide it before it is read.
    isWarningShown.value = digits !== value || (isWarningShown.value && value !== '')
    return value
  }

  function reset() {
    isWarningShown.value = false
  }

  return { isWarningShown, filterInput, reset }
}
