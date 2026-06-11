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
        <AdditionalDataCard v-if="subStep4 === 1" v-model="formData.additionalData" />
        <AttachmentsCard v-else-if="subStep4 === 2" v-model="formData.attachments" />
      </div>

      <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 rounded-2xl px-6 py-4 text-sm">
        {{ error }}
      </div>

      <FormActionsBar
        :current-step="logicalCurrentStep"
        :total-steps="5"
        :loading="submitting"
        @next="handleNext"
        @prev="prevStep"
      />

    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { call as _frappeCall } from 'frappe-ui'

// frappe-ui's call.js crashes with TypeError when the server returns a non-JSON
// error body (e.g. CSRFTokenError HTML page). Wrap it so we always get a clean Error.
async function call(method, args) {
  try {
    return await _frappeCall(method, args)
  } catch (err) {
    if (err instanceof TypeError) {
      const e = new Error('Internal Server Error')
      e.messages = ['Internal Server Error']
      throw e
    }
    throw err
  }
}
import { useLanguage } from '@/composables/useLanguage'
import FormStepsBar from './FormStepsBar.vue'
import FormActionsBar from './FormActionsBar.vue'
import PersonalInfoCard from './PersonalInfoCard.vue'
import AdditionalInfoCard from './AdditionalInfoCard.vue'
import FamilyDetailsCard from './FamilyDetailsCard.vue'
import IncomeDetailsCard from './IncomeDetailsCard.vue'
import FinancialObligationsCard from './FinancialObligationsCard.vue'
import AdditionalDataCard from './AdditionalDataCard.vue'
import AttachmentsCard from './AttachmentsCard.vue'

const emit = defineEmits(['submitted'])
const { t, isRTL } = useLanguage()

const currentStep = ref(1)
const subStep4 = ref(1)
const submitting = ref(false)
const error = ref('')

// Step 4 has two sub-steps; present 5 logical views to FormActionsBar
// so "Next" shows on sub-step 1 and "Submit" shows on sub-step 2.
const logicalCurrentStep = computed(() =>
  currentStep.value === 4 && subStep4.value === 2 ? 5 : currentStep.value
)

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
  attachments: {
    files: {},
    legalClaims: {
      correctData: false,
      verificationRight: false,
      statusAwareness: false,
    },
  },
})

function prevStep() {
  error.value = ''
  if (currentStep.value === 4 && subStep4.value === 2) {
    subStep4.value = 1
    return
  }
  if (currentStep.value > 1) currentStep.value--
}

async function handleNext() {
  error.value = ''
  if (currentStep.value === 4 && subStep4.value === 1) {
    subStep4.value = 2
    return
  }
  if (currentStep.value === 4 && subStep4.value === 2) {
    await submitRegistration()
    return
  }
  if (currentStep.value < stepsList.value.length) {
    currentStep.value++
  }
}

function readFileAsBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result.split(',')[1])
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

async function attachFile(file, docName) {
  const content = await readFileAsBase64(file)
  await call('frappe.client.insert', {
    doc: {
      doctype: 'File',
      file_name: file.name,
      content,
      decode: true,
      is_private: 0,
      attached_to_doctype: 'Beneficiaries Registration',
      attached_to_name: docName,
    },
  })
}

async function submitRegistration() {
  submitting.value = true
  try {
    const ad = formData.value.additionalData
    const lc = formData.value.attachments.legalClaims

    const doc = {
      doctype: 'Beneficiaries Registration',
      // Step 1 – personal info (fieldnames already match)
      ...formData.value.personalInfo,
      ...formData.value.additionalInfo,
      ...formData.value.familyDetails,
      // Step 2 – income checkboxes (fieldnames already match)
      ...formData.value.incomeDetails,
      // Step 3 – obligation checkboxes (fieldnames already match)
      ...formData.value.financialObligations,
      // Step 4a – address / other: frontend uses invented names; map to doctype fieldnames
      housing_type:             ad.housing_type,
      city:                     ad.housing_city,
      zone:                     ad.zone_number,
      street_name:              ad.street_number,
      unit:                     ad.unit_number,
      building_name:            ad.building_number,
      adress:                   ad.housing_description,
      afif_relationship:        ad.has_afif_employee_relation,
      additional_information:   ad.has_other_info,
      additional_information_text: ad.additional_notes,
      coresidence:              ad.has_housemates,
      bank_loans:               ad.has_bank_loans,
      // Step 4b – consent checkboxes (reqd:1 in doctype; boolean → Frappe Check 0/1)
      documents_confirmation:   lc.correctData      ? 1 : 0,
      verification_consent:     lc.verificationRight ? 1 : 0,
      cancellation_right:       lc.statusAwareness  ? 1 : 0,
    }

    const created = await call('frappe.client.insert', { doc })

    // Attach each selected file to the created document the same way
    // Frappe's desk does: insert a File doc with base64 content.
    for (const file of Object.values(formData.value.attachments.files)) {
      if (file instanceof File) {
        await attachFile(file, created.name)
      }
    }

    emit('submitted')
  } catch (err) {
    error.value = err.message || t('registration.submitError')
  } finally {
    submitting.value = false
  }
}
</script>
