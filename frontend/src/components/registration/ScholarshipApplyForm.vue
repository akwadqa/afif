<template>
  <div class="min-h-screen bg-[#EBF4FF] py-10 px-4 md:px-8" :dir="isRTL ? 'rtl' : 'ltr'">
    <div class="max-w-5xl mx-auto space-y-6">

      <div class="min-w-0">
        <h1 class="text-xl sm:text-2xl font-bold text-[#0570B6]">{{ t('scholarship.title') }}</h1>
        <p class="text-xs sm:text-sm text-gray-500 mt-1">{{ t('scholarship.acceptedSubtitle') }}</p>
      </div>

      <ScholarshipRequestCard
        v-model="scholarshipRequest"
        :files="files"
        :invalid-fields="invalidFields"
        @select-file="(id, file) => (files = { ...files, [id]: file })"
        @remove-file="id => (files = { ...files, [id]: null })"
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
import { uploadFile } from '@/utils/fileUpload'
import FormActionsBar from './FormActionsBar.vue'
import ScholarshipRequestCard from './ScholarshipRequestCard.vue'
import ValidationErrorPopup from './ValidationErrorPopup.vue'
import { LEGACY_SCHOLARSHIP_ATTACHMENT_FIELDS, SCHOLARSHIP_DECLARATION_FIELDS } from './registrationVariant'
import { validateRegistrationStep } from './registrationValidation'

// Step 5 of the scholarship wizard for an accepted beneficiary, whose registration is already done.
const emit = defineEmits(['submitted'])
const { t, isRTL } = useLanguage()

const scholarshipRequest = ref({
  requested_amount: '',
  request_summary: '',
  declarations: Object.fromEntries(SCHOLARSHIP_DECLARATION_FIELDS.map(field => [field, false])),
})
const files = ref({})
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
    formData: { scholarshipRequest: scholarshipRequest.value, attachments: { files: files.value } },
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

// Only a Supervisor may save an Accepted registration, so the files are uploaded unattached and the
// endpoint puts them on the registration after checking they are the user's own.
async function submitRequest() {
  for (const id of LEGACY_SCHOLARSHIP_ATTACHMENT_FIELDS) {
    // Stored back as a URL so a retry after a failed submit reuses the upload.
    if (files.value[id] instanceof File) files.value[id] = await uploadFile(files.value[id], { is_private: '1' })
  }

  const sr = scholarshipRequest.value
  await createScholarshipRequest.submit({
    request: {
      requested_amount: sr.requested_amount,
      request_summary: sr.request_summary,
      ...files.value,
      ...Object.fromEntries(SCHOLARSHIP_DECLARATION_FIELDS.map(field => [field, sr.declarations[field] ? 1 : 0])),
    },
  })
}
</script>
