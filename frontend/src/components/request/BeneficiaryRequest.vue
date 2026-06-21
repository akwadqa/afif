<template>
  <div class="min-h-screen bg-[#EBF4FF] py-10 px-4 md:px-8" :dir="isRTL ? 'rtl' : 'ltr'">
    <div class="max-w-5xl mx-auto space-y-6">

      <!-- Header -->
      <div class="flex items-center justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-[#0570B6]">{{ t('request.title') }}</h1>
          <p class="text-sm text-gray-500 mt-1">{{ t('request.subtitle') }}</p>
        </div>
        <span class="border px-4 py-2 rounded-xl text-sm font-semibold whitespace-nowrap" :class="requestStatusClass">
          {{ requestStatusLabel }}
        </span>
      </div>

      <!-- Form -->
      <template v-if="!submitted">
        <div class="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-sm" :class="{ 'read-only-form': readOnly }">

          <!-- Card header -->
          <div class="flex items-center gap-2 border-b border-gray-50 pb-4 mb-6 text-[#0570B6]">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 shrink-0">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.568 3H5.25A2.25 2.25 0 0 0 3 5.25v4.318c0 .597.237 1.17.659 1.591l9.581 9.581c.699.699 1.78.872 2.607.33a18.095 18.095 0 0 0 5.223-5.223c.542-.827.369-1.908-.33-2.607L11.16 3.66A2.25 2.25 0 0 0 9.568 3Z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 6h.008v.008H6V6Z" />
            </svg>
            <h3 class="text-base font-bold">{{ t('request.category.title') }}</h3>
          </div>

          <div class="space-y-5">

            <!-- 1) Category select -->
            <div class="space-y-1.5">
              <label class="input-label">{{ t('request.category.type') }} <span v-if="!readOnly" class="text-red-500">*</span></label>
              <select
                v-model="form.request_category"
                @change="onCategoryChange"
                class="custom-select"
                :class="{ 'border-red-300 bg-red-50/30': isInvalid('request_category') }"
                :disabled="readOnly"
              >
                <option value="" disabled>{{ t('request.category.selectType') }}</option>
                <option v-for="cat in categories" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
              </select>
            </div>

            <!-- 2) Subcategory -->
            <Transition name="fade-slide">
              <div v-if="subcategoryField" class="space-y-1.5">
                <label class="input-label">{{ subcategoryLabel }} <span v-if="!readOnly" class="text-red-500">*</span></label>
                <select
                  v-model="form[subcategoryField]"
                  class="custom-select"
                  :class="{ 'border-red-300 bg-red-50/30': isInvalid(subcategoryField) }"
                  :disabled="readOnly"
                >
                  <option value="" disabled>{{ t('request.category.selectSubtype') }}</option>
                  <option v-for="opt in subcategoryOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                </select>
              </div>
            </Transition>

            <!-- 3) Requested amount -->
            <div class="space-y-1.5">
              <label class="input-label">{{ t('request.details.requestedAmount') }} <span v-if="!readOnly" class="text-red-500">*</span></label>
              <input
                type="text"
                v-model="form.requested_amount"
                :placeholder="t('request.details.amountPlaceholder')"
                class="custom-input font-sans"
                :class="{ 'border-red-300 bg-red-50/30': isInvalid('requested_amount') }"
                :disabled="readOnly"
              />
            </div>

            <!-- 4) Request summary -->
            <div class="space-y-1.5">
              <label class="input-label">{{ t('request.details.requestSummary') }} <span v-if="!readOnly" class="text-red-500">*</span></label>
              <textarea
                rows="4"
                v-model="form.request_summary"
                :placeholder="t('request.details.summaryPlaceholder')"
                class="custom-textarea"
                :class="{ 'border-red-300 bg-red-50/30': isInvalid('request_summary') }"
                :disabled="readOnly"
              ></textarea>
            </div>

            <!-- 5) Attachments -->
            <Transition name="fade-slide">
              <div v-if="requiredDocs.length" class="space-y-3">
                <div
                  v-for="doc in requiredDocs"
                  :key="doc.id"
                  class="flex flex-col md:flex-row md:items-center justify-between p-4 border rounded-xl transition-all gap-4"
                  :class="isInvalid('attach_' + doc.id)
                    ? 'bg-red-50/50 border-red-300'
                    : 'bg-gray-50/50 hover:bg-gray-50/80 border-gray-100/70'"
                >
                  <div class="flex-1 min-w-0">
                    <div class="text-sm font-semibold text-gray-700">
                      {{ t(doc.labelKey) }}
                      <span v-if="!readOnly" class="text-red-500">*</span>
                    </div>
                  </div>

                  <!-- Read-only: just show file name -->
                  <div v-if="readOnly" class="shrink-0">
                    <span v-if="files[doc.id]" class="text-xs text-green-600 font-semibold" dir="ltr">
                      {{ fileName(doc.id) }}
                    </span>
                    <span v-else class="text-xs text-gray-400">—</span>
                  </div>

                  <!-- Editable: upload/delete buttons -->
                  <div v-else class="flex items-center gap-3 self-end md:self-auto shrink-0 rtl:flex-row-reverse">
                    <button
                      v-if="!files[doc.id]"
                      type="button"
                      @click="triggerFileInput(doc.id)"
                      class="flex items-center gap-1.5 px-4 py-2 border border-sky-200 text-sky-600 rounded-xl bg-white hover:bg-sky-50 transition-colors text-xs font-bold shadow-sm"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4 shrink-0">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z" />
                      </svg>
                      <span>{{ t('request.attachments.upload') }}</span>
                    </button>

                    <template v-else>
                      <button
                        type="button"
                        @click="triggerFileInput(doc.id)"
                        class="flex items-center gap-1.5 px-4 py-2 border border-sky-100 text-sky-600 rounded-xl bg-sky-50/40 hover:bg-sky-50 transition-colors text-xs font-semibold"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4 shrink-0">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
                        </svg>
                        <span>{{ t('request.attachments.reupload') }}</span>
                      </button>

                      <button
                        type="button"
                        @click="deleteFile(doc.id)"
                        class="flex items-center gap-1.5 px-3 py-2 border border-red-100 text-red-500 rounded-xl bg-red-50/30 hover:bg-red-50 transition-colors text-xs font-semibold"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4 shrink-0">
                          <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                        </svg>
                        <span>{{ t('request.attachments.delete') }}</span>
                      </button>
                    </template>

                    <span
                      v-if="files[doc.id]"
                      class="text-xs text-green-600 font-semibold truncate max-w-[180px] inline-block align-middle"
                      dir="ltr"
                    >
                      {{ fileName(doc.id) }}
                    </span>
                  </div>
                </div>
              </div>
            </Transition>

          </div>
        </div>

        <!-- Error -->
        <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 rounded-2xl px-6 py-4 text-sm">
          {{ error }}
        </div>

        <!-- Read-only: back button only -->
        <div v-if="readOnly" class="bg-white rounded-[32px] border border-[#F8FAFC] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.05)] px-10 py-6 flex items-center justify-center">
          <button
            @click="$emit('back')"
            class="flex items-center gap-2 px-8 py-3 border border-sky-200 text-sky-600 rounded-xl font-semibold hover:bg-sky-50 active:scale-[0.98] transition-all"
          >
            {{ t('myRequests.backToList') }}
          </button>
        </div>

        <!-- Editable: Save + Discard -->
        <div v-else class="bg-white rounded-[32px] border border-[#F8FAFC] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.05)] px-10 py-12 flex items-center justify-end gap-3">
          <button
            @click="handleSubmit"
            :disabled="submitting"
            class="flex items-center gap-2 px-8 py-3 bg-[#34B0EE] text-white rounded-xl font-bold hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-60"
          >
            <svg v-if="submitting" class="animate-spin w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            <span>{{ submitting ? t('request.submitting') : t('request.save') }}</span>
          </button>
          <button
            @click="resetForm"
            :disabled="submitting"
            class="px-8 py-3 border border-gray-200 text-gray-600 rounded-xl font-semibold hover:bg-gray-50 active:scale-[0.98] transition-all disabled:opacity-60"
          >{{ t('request.discard') }}</button>
        </div>

        <!-- Validation popup -->
        <ValidationErrorPopup
          v-if="showValidationPopup"
          :missing-fields="validationErrors"
          @close="showValidationPopup = false"
        />
      </template>

    </div>
  </div>

  <!-- Hidden file input -->
  <input
    v-if="!readOnly"
    ref="fileInputRef"
    type="file"
    class="hidden"
    accept=".pdf,.jpg,.jpeg,.png,.ogg,.webm"
    @change="onFileSelected"
  />
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import { useLanguage } from '@/composables/useLanguage'
import ValidationErrorPopup from '@/components/registration/ValidationErrorPopup.vue'

const props = defineProps({
  beneficiaryName: { type: String, required: true },
  requestName: { type: String, default: '' },
  readOnly: { type: Boolean, default: false },
})
const emit = defineEmits(['submitted', 'back'])

const router = useRouter()
const { t, isRTL } = useLanguage()

const submitting = ref(false)
const submitted = ref(false)
const error = ref('')
const showValidationPopup = ref(false)
const validationErrors = ref([])
const invalidFields = ref([])
const fileInputRef = ref(null)
const activeFieldId = ref('')
const loadedStatus = ref('')

const form = ref({
  request_category: '',
  medical_assistance: '',
  educational_assistance: '',
  social_assistance: '',
  family_assistance: '',
  housing_assistance: '',
  training_assistance: '',
  awareness_assistance: '',
  requested_amount: '',
  request_summary: '',
})

const files = ref({})

const REQUEST_ATTACHMENT_FIELDS = [
  'medical_bill', 'education_invoice', 'garmeen_proof', 'garmeen_disclosure',
  'travel_ticket_doc', 'rent_contract', 'onwer_qid', 'late_letter', 'estate_pruchase',
]

const requestStatusLabel = computed(() => {
  if (loadedStatus.value) {
    const translated = t(`statuses.request.${loadedStatus.value}`)
    if (translated && translated !== `statuses.request.${loadedStatus.value}`) return translated
    return loadedStatus.value
  }
  return t('request.statusNew')
})

const requestStatusClass = computed(() => {
  const status = loadedStatus.value
  if (['Approved', 'Approved For Aid'].includes(status)) return 'border-green-200 text-green-600 bg-green-50'
  if (['Rejected', 'Rejected by Supervisor'].includes(status)) return 'border-red-200 text-red-600 bg-red-50'
  if (['Pending Supervisor Approval', 'Pending Specialist Approval', 'Saved'].includes(status)) return 'border-amber-200 text-amber-600 bg-amber-50'
  return 'border-sky-200 text-sky-600 bg-white'
})

// ── Load existing request for read-only view ──

const getDoc = createResource({
  url: 'frappe.client.get',
  onSuccess(data) {
    populateFromDoc(data)
  },
  onError(err) {
    error.value = err.message || t('request.submitError')
  },
})

function populateFromDoc(doc) {
  loadedStatus.value = doc.status || ''

  form.value.request_category = doc.request_category || ''
  form.value.medical_assistance = doc.medical_assistance || ''
  form.value.educational_assistance = doc.educational_assistance || ''
  form.value.social_assistance = doc.social_assistance || ''
  form.value.family_assistance = doc.family_assistance || ''
  form.value.housing_assistance = doc.housing_assistance || ''
  form.value.training_assistance = doc.training_assistance || ''
  form.value.awareness_assistance = doc.awareness_assistance || ''
  form.value.requested_amount = doc.requested_amount || ''
  form.value.request_summary = doc.request_summary || ''

  const existingFiles = {}
  for (const field of REQUEST_ATTACHMENT_FIELDS) {
    if (doc[field]) existingFiles[field] = doc[field]
  }
  files.value = existingFiles
}

onMounted(() => {
  if (props.requestName) {
    getDoc.submit({ doctype: 'Beneficiary Request', name: props.requestName })
  }
})

// ── Category / subcategory ──

const categories = computed(() => [
  { value: 'Medical Assistance', label: t('request.categories.medical') },
  { value: 'Education Assistance', label: t('request.categories.education') },
  { value: 'Social Assistance', label: t('request.categories.social') },
  { value: 'Family Assistance', label: t('request.categories.family') },
  { value: 'Housing Assistance', label: t('request.categories.housing') },
  { value: 'Training Assistance', label: t('request.categories.training') },
  { value: 'Awareness Assistance', label: t('request.categories.awareness') },
])

const SUBCATEGORY_MAP = {
  'Medical Assistance': {
    field: 'medical_assistance',
    key: 'medical',
    options: ['Medical Procedures', 'Medical Equipment', 'Medication', 'Medical Supplies', 'Natural Treatment', 'Other Medical Assistance'],
  },
  'Education Assistance': {
    field: 'educational_assistance',
    key: 'education',
    options: ['Tuition Fees', 'Transportation Fees', 'Books And Resources', 'Educational Equipment', 'Other Educational Assistance'],
  },
  'Social Assistance': {
    field: 'social_assistance',
    key: 'social',
    options: ['Garmeen', 'Orphan sponsorship', 'Marriage assistance', 'Economic empowerment assistance', 'Travel ticket assistance', 'Widow assistance', 'Divorced women assistance', 'Elderly assistance', 'Unemployed assistance', 'Visitor assistance', 'Emergency assistance', 'Psychological support assistance', 'Other social assistance'],
  },
  'Family Assistance': {
    field: 'family_assistance',
    key: 'family',
    options: ['Emergency lump-sum financial assistance', 'Monthly financial assistance', 'In-kind assistance', 'Family nursery sponsorship', 'Seasonal financial assistance', 'Food basket (food aid)', 'In-kind assistance with a monthly shopping card', 'In-kind assistance with a Ramadan shopping card', 'Utility bills', 'Fines support', 'Other family assistance'],
  },
  'Housing Assistance': {
    field: 'housing_assistance',
    key: 'housing',
    options: ['Rent support', 'Land purchase', 'Real estate purchase', 'Land purchase and construction', 'Demolition and construction', 'Maintenance and restoration', 'Furnishing support', 'Other social housing assistance'],
  },
  'Training Assistance': {
    field: 'training_assistance',
    key: 'training',
    options: ['Secretarial training', 'Entrepreneurship training', 'Student training', 'Prisoner training', 'Other training and rehabilitation'],
  },
  'Awareness Assistance': {
    field: 'awareness_assistance',
    key: 'awareness',
    options: ['National Awareness', 'Cultural Awareness', 'Social Awareness', 'Health Awareness', 'Environmental Awareness', 'Charitable Awareness', 'Consumer Awareness', 'Other Awareness Assistance'],
  },
}

const subcategoryConfig = computed(() => SUBCATEGORY_MAP[form.value.request_category] || null)
const subcategoryField = computed(() => subcategoryConfig.value?.field || '')

const subcategoryLabel = computed(() => {
  if (!form.value.request_category) return ''
  const cat = categories.value.find(c => c.value === form.value.request_category)
  return cat ? cat.label : ''
})

const subcategoryOptions = computed(() => {
  if (!subcategoryConfig.value) return []
  const k = subcategoryConfig.value.key
  return subcategoryConfig.value.options.map(val => ({
    value: val,
    label: t(`request.subtypes.${k}.${val}`),
  }))
})

const currentSubcategory = computed(() => {
  return subcategoryField.value ? form.value[subcategoryField.value] : ''
})

function onCategoryChange() {
  if (props.readOnly) return
  form.value.medical_assistance = ''
  form.value.educational_assistance = ''
  form.value.social_assistance = ''
  form.value.family_assistance = ''
  form.value.housing_assistance = ''
  form.value.training_assistance = ''
  form.value.awareness_assistance = ''
  files.value = {}
}

// ── Conditional attachments ──

const requiredDocs = computed(() => {
  const docs = []
  const cat = form.value.request_category
  const sub = currentSubcategory.value

  if (cat === 'Medical Assistance') {
    docs.push({ id: 'medical_bill', labelKey: 'request.attachments.docs.medicalBill' })
  }
  if (cat === 'Education Assistance') {
    docs.push({ id: 'education_invoice', labelKey: 'request.attachments.docs.educationInvoice' })
  }
  if (cat === 'Social Assistance' && sub === 'Garmeen') {
    docs.push({ id: 'garmeen_proof', labelKey: 'request.attachments.docs.garmeenProof' })
    docs.push({ id: 'garmeen_disclosure', labelKey: 'request.attachments.docs.garmeenDisclosure' })
  }
  if (cat === 'Social Assistance' && sub === 'Travel ticket assistance') {
    docs.push({ id: 'travel_ticket_doc', labelKey: 'request.attachments.docs.travelTicketDoc' })
  }
  if (cat === 'Housing Assistance') {
    docs.push({ id: 'rent_contract', labelKey: 'request.attachments.docs.rentContract' })
    docs.push({ id: 'onwer_qid', labelKey: 'request.attachments.docs.ownerQid' })
    docs.push({ id: 'late_letter', labelKey: 'request.attachments.docs.lateLetter' })
    if (sub === 'Real estate purchase') {
      docs.push({ id: 'estate_pruchase', labelKey: 'request.attachments.docs.estatePurchase' })
    }
  }

  return docs
})

function isInvalid(field) {
  return invalidFields.value.includes(field)
}

// ── File handling ──

function triggerFileInput(fieldId) {
  activeFieldId.value = fieldId
  fileInputRef.value.value = ''
  fileInputRef.value.click()
}

function onFileSelected(e) {
  const file = e.target.files[0]
  if (!file) return
  const allowed = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'audio/ogg', 'video/webm']
  if (!allowed.includes(file.type)) {
    alert(t('request.attachments.invalidFileType'))
    return
  }
  files.value[activeFieldId.value] = file
}

function deleteFile(fieldId) {
  delete files.value[fieldId]
}

function fileName(fieldId) {
  const val = files.value[fieldId]
  if (val instanceof File) return val.name
  if (typeof val === 'string') return val.split('/').pop()
  return ''
}

// ── Validation ──

function validate() {
  const errors = []
  const fields = []
  const f = form.value

  function req(value, field, label) {
    if (!value) { errors.push(label); fields.push(field) }
  }

  req(f.request_category, 'request_category', t('request.category.type'))

  if (subcategoryField.value) {
    req(f[subcategoryField.value], subcategoryField.value, subcategoryLabel.value)
  }

  req(f.requested_amount, 'requested_amount', t('request.details.requestedAmount'))
  req(f.request_summary, 'request_summary', t('request.details.requestSummary'))

  for (const doc of requiredDocs.value) {
    if (!files.value[doc.id]) {
      errors.push(t(doc.labelKey))
      fields.push('attach_' + doc.id)
    }
  }

  return { errors, fields }
}

// ── Submit ──

function extractError(err) {
  if (err._server_messages) {
    try {
      const parsed = JSON.parse(err._server_messages)
      const first = typeof parsed[0] === 'string' ? JSON.parse(parsed[0]) : parsed[0]
      if (first.message) return first.message
    } catch { /* fall through */ }
  }
  if (err.messages?.length) {
    const msg = err.messages[0]
    return typeof msg === 'string' ? msg : msg.message || JSON.stringify(msg)
  }
  return err.message || err.exc_type || t('request.submitError')
}

const insertDoc = createResource({
  url: 'frappe.client.insert',
  onError(err) {
    error.value = extractError(err)
    submitting.value = false
  },
})

async function handleSubmit() {
  error.value = ''

  const { errors, fields } = validate()
  if (errors.length) {
    validationErrors.value = errors
    invalidFields.value = fields
    showValidationPopup.value = true
    return
  }

  invalidFields.value = []
  submitting.value = true

  const f = form.value
  const doc = {
    doctype: 'Beneficiary Request',
    request_category: f.request_category,
    requested_amount: f.requested_amount,
    request_summary: f.request_summary,
  }

  if (subcategoryField.value && f[subcategoryField.value]) {
    doc[subcategoryField.value] = f[subcategoryField.value]
  }

  try {
    const result = await insertDoc.submit({ doc })
    if (!result?.name) return

    const docName = result.name

    for (const [fieldname, file] of Object.entries(files.value)) {
      if (file instanceof File) {
        await uploadFile(file, docName, fieldname)
      }
    }

    submitted.value = true
    emit('submitted')
  } catch (e) {
    if (!error.value) {
      error.value = extractError(e)
    }
  }

  submitting.value = false
}

async function uploadFile(file, docName, fieldname) {
  const fd = new FormData()
  fd.append('file', file, file.name)
  fd.append('is_private', '0')
  fd.append('folder', 'Home/Attachments')
  fd.append('doctype', 'Beneficiary Request')
  fd.append('docname', docName)
  fd.append('fieldname', fieldname)

  const headers = { 'X-Frappe-Site-Name': window.location.hostname }
  if (window.csrf_token && window.csrf_token !== '{{ csrf_token }}') {
    headers['X-Frappe-CSRF-Token'] = window.csrf_token
  }

  const res = await fetch('/api/method/upload_file', { method: 'POST', headers, body: fd })
  if (!res.ok) throw new Error(`${t('request.submitError')}: ${file.name}`)
  const data = await res.json()
  return data.message.file_url
}

// ── Navigation ──

function resetForm() {
  form.value = {
    request_category: '',
    medical_assistance: '',
    educational_assistance: '',
    social_assistance: '',
    family_assistance: '',
    housing_assistance: '',
    training_assistance: '',
    awareness_assistance: '',
    requested_amount: '',
    request_summary: '',
  }
  files.value = {}
  submitted.value = false
  error.value = ''
  invalidFields.value = []
}
</script>

<style scoped>
.input-label {
  @apply text-xs font-semibold text-gray-700 block leading-relaxed;
}

.custom-input {
  @apply w-full px-4 py-3 bg-gray-50/60 border border-gray-100/70 rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all placeholder:text-gray-300;
}

.custom-input:disabled {
  @apply opacity-75 cursor-default;
  background-color: #f9fafb;
}

.custom-textarea {
  @apply w-full px-4 py-3 bg-gray-50/60 border border-gray-100/70 rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all resize-none min-h-[120px] placeholder:text-gray-300;
}

.custom-textarea:disabled {
  @apply opacity-75 cursor-default;
  background-color: #f9fafb;
}

.custom-select {
  @apply w-full px-4 py-3 bg-gray-50/60 border border-gray-100/70 rounded-xl focus:ring-2 focus:ring-[#34B0EE] outline-none text-sm appearance-none bg-no-repeat text-gray-700;
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23a0aec0%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
  background-size: 12px 12px;
}

.custom-select:disabled {
  @apply opacity-75 cursor-default;
  background-color: #f9fafb;
}

.read-only-form select,
.read-only-form input,
.read-only-form textarea {
  pointer-events: none;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.25s ease-in-out;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
