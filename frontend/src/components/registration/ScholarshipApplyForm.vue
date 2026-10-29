<template>
  <div class="min-h-screen bg-[#EBF4FF] py-10 px-4 md:px-8" :dir="isRTL ? 'rtl' : 'ltr'">
    <div class="max-w-5xl mx-auto space-y-6">

      <div class="min-w-0">
        <h1 class="text-xl sm:text-2xl font-bold text-[#0570B6]">{{ t('scholarship.title') }}</h1>
        <p class="text-xs sm:text-sm text-gray-500 mt-1">{{ t('scholarship.acceptedSubtitle') }}</p>
      </div>

      <ScholarshipRequestCard
        v-model="scholarshipRequest"
        :invalid-fields="invalidFields"
      />

      <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 rounded-2xl px-6 py-4 text-sm">
        {{ error }}
      </div>

      <FormActionsBar :current-step="1" :total-steps="1" :loading="submitting" @next="submit" />

      <ValidationErrorPopup
        v-if="validationErrors.length"
        :missing-fields="validationErrors"
        @close="validationErrors = []"
      />

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { createResource } from 'frappe-ui'
import { useLanguage } from '@/composables/useLanguage'
import FormActionsBar from './FormActionsBar.vue'
import ScholarshipRequestCard from './ScholarshipRequestCard.vue'
import ValidationErrorPopup from './ValidationErrorPopup.vue'
import { SCHOLARSHIP_DECLARATION_FIELDS } from './registrationVariant'
import { validateRegistrationStep } from './registrationValidation'
import { createScholarshipRequestFiles, uploadScholarshipRequestFiles } from './scholarshipRequestFiles'

// Step 5 of the scholarship wizard for an accepted beneficiary, whose registration is already done.
const emit = defineEmits(['submitted'])
const { t, isRTL } = useLanguage()

const scholarshipRequest = ref({
  requested_amount: '',
  request_summary: '',
  declarations: Object.fromEntries(SCHOLARSHIP_DECLARATION_FIELDS.map(field => [field, false])),
  files: createScholarshipRequestFiles(),
})
const invalidFields = ref([])
const validationErrors = ref([])
const error = ref('')
const submitting = ref(false)

const createScholarshipRequest = createResource({
  url: 'afif.api.scholarship.create_scholarship_request',
  onError(err) {
    error.value = err.messages?.[0] || err.message || t('registration.submitError')
  },
})

async function submit() {
  error.value = ''
  const { errors, fields } = validateRegistrationStep({
    formData: { scholarshipRequest: scholarshipRequest.value },
    step: 5,
    flow: 'scholarship',
    t,
  })
  invalidFields.value = fields
  if (errors.length) {
    validationErrors.value = errors
    return
  }

  submitting.value = true
  try {
    await submitRequest()
    emit('submitted')
  } catch (e) {
    error.value ||= e.message || t('registration.submitError')
  } finally {
    submitting.value = false
  }
}

async function submitRequest() {
  const sr = scholarshipRequest.value
  const uploadedFiles = await uploadScholarshipRequestFiles(sr.files)
  await createScholarshipRequest.submit({
    request: {
      requested_amount: sr.requested_amount,
      request_summary: sr.request_summary,
      ...Object.fromEntries(SCHOLARSHIP_DECLARATION_FIELDS.map(field => [field, sr.declarations[field] ? 1 : 0])),
      ...uploadedFiles,
    },
  })
}
</script>
