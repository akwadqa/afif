import { describe, expect, it } from 'vitest'
import { useWholeNumberInput } from './useWholeNumberInput'

const type = (input, value) => input.filterInput({ target: { value } })

describe('useWholeNumberInput', () => {
  it('keeps digits only and converts Arabic-Indic digits without a warning', () => {
    const input = useWholeNumberInput()

    expect(type(input, '١٢٣4')).toBe('1234')
    expect(input.isWarningShown.value).toBe(false)
  })

  it('keeps the warning while digits follow a removed decimal point', () => {
    const input = useWholeNumberInput()

    expect(type(input, '12345.')).toBe('12345')
    expect(type(input, '123456')).toBe('123456')
    expect(input.isWarningShown.value).toBe(true)
  })

  it('hides the warning once the field is emptied', () => {
    const input = useWholeNumberInput()
    type(input, '1 ')

    type(input, '')
    expect(input.isWarningShown.value).toBe(false)
  })
})
