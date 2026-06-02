<template>
  <div class="min-h-screen bg-[#EBF4FF] py-10 px-4 md:px-8" :dir="isRTL ? 'rtl' : 'ltr'">
    <div class="max-w-5xl mx-auto space-y-6">

      <div class="flex items-center justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-[#0570B6]">{{ t('registration.title') }}</h1>
          <p class="text-sm text-gray-500 mt-1">{{ t('registration.subtitle') }}</p>
        </div>
        <span class="border border-sky-200 text-sky-600 bg-white px-4 py-2 rounded-xl text-sm font-semibold whitespace-nowrap">
          {{ t('registration.statusNew') }}
        </span>
      </div>

      <FormStepsBar :current-step="currentStep" :steps="stepsList" />

      <div v-if="currentStep === 1" class="space-y-6">
        <PersonalInfoCard v-model="formData.personalInfo" />
        <AdditionalInfoCard v-model="formData.additionalInfo" />
        <FamilyDetailsCard v-model="formData.familyDetails" />
      </div>

      <div v-else-if="currentStep === 2">
        <IncomeDetailsCard v-model="formData.incomeDetails" />
      </div>

      <div v-else-if="currentStep === 3">
        <FinancialObligationsCard v-model="formData.financialObligations" />
      </div>

      <div v-else-if="currentStep === 4">
        <AdditionalDataCard v-model="formData.additionalData" />
      </div>

      <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 rounded-2xl px-6 py-4 text-sm">
        {{ error }}
      </div>

      <FormActionsBar
        :current-step="currentStep"
        :total-steps="stepsList.length"
        :loading="submitting"
        @next="handleNext"
        @prev="prevStep"
      />

    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { call } from 'frappe-ui'
import { useLanguage } from '@/composables/useLanguage'
import FormStepsBar from './FormStepsBar.vue'
import FormActionsBar from './FormActionsBar.vue'
import PersonalInfoCard from './PersonalInfoCard.vue'
import AdditionalInfoCard from './AdditionalInfoCard.vue'
import FamilyDetailsCard from './FamilyDetailsCard.vue'
import IncomeDetailsCard from './IncomeDetailsCard.vue'
import FinancialObligationsCard from './FinancialObligationsCard.vue'
import AdditionalDataCard from './AdditionalDataCard.vue'

const emit = defineEmits(['submitted'])
const { t, isRTL } = useLanguage()

const currentStep = ref(1)
const submitting = ref(false)
const error = ref('')

const stepsList = computed(() => [
  { number: 1, label: t('registration.steps.personalData') },
  { number: 2, label: t('registration.steps.incomeDetails') },
  { number: 3, label: t('registration.steps.financialObligations') },
  { number: 4, label: t('registration.steps.additionalData') },
])

const formData = ref({
  personalInfo: {},
  additionalInfo: {},
  familyDetails: {},
  incomeDetails: {
    ben_income: 0,
    family_income: 0,
    family_extra: 0,
    children_income: 0,
    private_income: 0,
    stock_income: 0,
    rent_income: 0,
  },
  financialObligations: {
    family_obligation: 0,
    rent_obligation: 0,
    treatment_obligation: 0,
    debt_obligation: 0,
    tuition_obligation: 0,
  },
  additionalData: {},
})

function nextStep() {
  if (currentStep.value < stepsList.value.length) currentStep.value++
}

function prevStep() {
  if (currentStep.value > 1) currentStep.value--
  error.value = ''
}

async function handleNext() {
  error.value = ''
  if (currentStep.value < stepsList.value.length) {
    nextStep()
    return
  }
  await submitRegistration()
}

async function submitRegistration() {
  submitting.value = true
  try {
    const doc = {
      ...formData.value.personalInfo,
      ...formData.value.additionalInfo,
      ...formData.value.familyDetails,
      ...formData.value.incomeDetails,
      ...formData.value.financialObligations,
      ...formData.value.additionalData,
    }
    await call('frappe.client.insert', {
      doc: { doctype: 'Beneficiaries Registration', ...doc },
    })
    emit('submitted')
  } catch (err) {
    error.value = err.message || t('registration.submitError')
  } finally {
    submitting.value = false
  }
}
</script>
