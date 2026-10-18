<template>
  <div class="min-h-screen bg-[#EBF4FF] py-10 px-4 md:px-8" :dir="isRTL ? 'rtl' : 'ltr'">
    <div class="max-w-5xl mx-auto space-y-6">

      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-4">
        <div class="min-w-0">
          <h1 class="text-xl sm:text-2xl font-bold text-[#0570B6]">{{ t(isScholarshipFlow ? 'scholarship.title' : 'registration.title') }}</h1>
          <p class="text-xs sm:text-sm text-gray-500 mt-1">{{ t(isScholarshipFlow ? 'scholarship.subtitle' : 'registration.subtitle') }}</p>
        </div>
        <div class="flex items-center gap-2 sm:gap-3 flex-wrap">
          <button
            v-if="canEdit && !editing"
            @click="editing = true"
            class="border-2 border-sky-500 bg-white text-sky-600 hover:bg-sky-50 px-2.5 py-1 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 whitespace-nowrap active:scale-[0.99]"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-3.5 h-3.5 shrink-0">
              <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
            </svg>
            {{ t('registration.editButton') }}
          </button>
          <span class="border px-3 sm:px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold whitespace-nowrap" :class="statusClass">
            {{ statusLabel }}
          </span>
        </div>
      </div>

      <FormStepsBar :current-step="currentStep" :steps="stepsList" />

      <div :class="{ 'read-only-form': isReadOnly }">
        <div v-if="currentStep === 1" class="space-y-6">
          <PersonalInfoCard v-model="formData.personalInfo" v-model:additional-info="formData.additionalInfo" :flow="flow" :invalid-fields="invalidFields" />
          <FamilyDetailsCard v-model="formData.familyDetails" :personal-info="formData.personalInfo" :flow="flow" :invalid-fields="invalidFields" />
        </div>

        <div v-else-if="currentStep === 2">
          <IncomeDetailsCard v-model="formData.incomeDetails" :flow="flow" :invalid-fields="invalidFields" />
        </div>

        <div v-else-if="currentStep === 3">
          <FinancialObligationsCard v-model="formData.financialObligations" :flow="flow" :invalid-fields="invalidFields" />
        </div>

        <div v-else-if="currentStep === 4">
          <AdditionalDataCard v-if="subStep4 === 1" v-model="formData.additionalData" :invalid-fields="invalidFields" />
          <AttachmentsCard
            v-else-if="subStep4 === 2"
            v-model="formData.attachments"
            :context="formData"
            :invalid-fields="invalidFields"
            :uploading="attachmentUploading"
            :upload-errors="attachmentUploadErrors"
            @select-file="handleAttachmentFileSelected"
          />
        </div>

        <div v-else-if="currentStep === 5 && isScholarshipFlow">
          <ScholarshipRequestCard v-model="formData.scholarshipRequest" :invalid-fields="invalidFields" />
        </div>
      </div>

      <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 rounded-2xl px-6 py-4 text-sm">
        {{ error }}
      </div>

      <!-- Read-only: navigation only (no submit), with back-to-list button -->
      <div v-if="isReadOnly"
        class="bg-white rounded-[32px] px-4 md:px-6 py-4 border border-gray-100 shadow-sm flex items-center justify-between gap-2"
        :dir="isRTL ? 'rtl' : 'ltr'"
      >
        <button
          @click="readOnlyPrev"
          :disabled="logicalCurrentStep === 1"
          class="border border-gray-100 text-gray-400 hover:text-gray-600 hover:bg-gray-50 disabled:opacity-40 px-3 md:px-5 py-2.5 rounded-xl text-xs md:text-sm font-medium flex items-center gap-1 transition-all shrink-0"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="w-3.5 h-3.5 shrink-0">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
          </svg>
          <span class="hidden sm:inline">{{ t('registration.back') }}</span>
        </button>

        <button
          @click="$emit('back')"
          class="border border-sky-200 text-sky-600 hover:bg-sky-50 px-5 py-2.5 rounded-xl text-xs md:text-sm font-semibold transition-all shrink-0"
        >
          {{ t('beneficiaryList.backToList') }}
        </button>

        <button
          @click="readOnlyNext"
          :disabled="logicalCurrentStep === 5"
          class="text-white font-medium text-xs md:text-sm py-2.5 px-4 md:px-8 rounded-xl shadow-md transition-all hover:opacity-95 active:scale-[0.98] disabled:opacity-40 flex items-center gap-2 shrink-0"
          style="background-color: #34B0EE;"
        >
          {{ t('registration.next') }}
        </button>
      </div>

      <!-- Editable: normal form actions -->
      <FormActionsBar
        v-else
        :current-step="logicalCurrentStep"
        :total-steps="totalLogicalSteps"
        :loading="submitting"
        @next="handleNext"
        @prev="prevStep"
      />

      <ValidationErrorPopup
        v-if="showValidationPopup"
        :missing-fields="validationErrors"
        @close="showValidationPopup = false"
      />

    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { createResource } from 'frappe-ui'
import { useLanguage } from '@/composables/useLanguage'
import { session } from '@/data/session'
import FormStepsBar from './FormStepsBar.vue'
import FormActionsBar from './FormActionsBar.vue'
import PersonalInfoCard from './PersonalInfoCard.vue'
import FamilyDetailsCard from './FamilyDetailsCard.vue'
import IncomeDetailsCard from './IncomeDetailsCard.vue'
import FinancialObligationsCard from './FinancialObligationsCard.vue'
import AdditionalDataCard from './AdditionalDataCard.vue'
import AttachmentsCard from './AttachmentsCard.vue'
import ScholarshipRequestCard from './ScholarshipRequestCard.vue'
import ValidationErrorPopup from './ValidationErrorPopup.vue'
import {
  SCHOLARSHIP_ATTACHMENT_FIELDS,
  SCHOLARSHIP_DECLARATION_FIELDS,
  getRegistrationVariant,
} from './registrationVariant'
import { validateRegistrationStep } from './registrationValidation'

const props = defineProps({
  registrationName: { type: String, default: null },
  readOnly: { type: Boolean, default: false },
  flow: { type: String, default: 'registration', validator: value => ['registration', 'scholarship'].includes(value) },
})

const emit = defineEmits(['submitted', 'back'])
const { t, isRTL } = useLanguage()

const EDITABLE_STATUSES = ['Draft', 'New Registration', 'Not Accepted', 'Update Required', 'Updated', 'Updated beneficiary']

const currentStep = ref(1)
const subStep4 = ref(1)
const maxStepReached = ref(1)
const snapshot = ref(null)
const submitting = ref(false)
const error = ref('')
const attachmentUploading = ref({})
const attachmentUploadErrors = ref({})
const docName = ref(null)
const docMeta = ref({})
const showValidationPopup = ref(false)
const validationErrors = ref([])
const invalidFields = ref([])
const editing = ref(false)

const canEdit = computed(() => EDITABLE_STATUSES.includes(docMeta.value.status))
const isReadOnly = computed(() => props.readOnly && !editing.value)
const isScholarshipFlow = computed(() => props.flow === 'scholarship')
const variant = computed(() => getRegistrationVariant(props.flow))

// Logical steps: 1-3 as numbered, 4 = additional data, 5 = registration attachments,
// 6 = scholarship request data (scholarship flow only).
const totalLogicalSteps = computed(() => (isScholarshipFlow.value ? 6 : 5))
const logicalCurrentStep = computed(() => {
  if (currentStep.value === 4 && subStep4.value === 2) return 5
  if (currentStep.value === 5) return 6
  return currentStep.value
})

const STATUS_MAP = {
  'Draft':                { key: 'statusDraft',       cls: 'border-gray-200 text-gray-600 bg-gray-50' },
  'New Registration':     { key: 'statusNew',         cls: 'border-sky-200 text-sky-600 bg-white' },
  'Not Accepted':         { key: 'statusNotAccepted', cls: 'border-red-200 text-red-600 bg-red-50' },
  'Accepted':             { key: 'statusNew',         cls: 'border-green-200 text-green-600 bg-green-50' },
  'Updated':              { key: 'statusNew',         cls: 'border-blue-200 text-blue-600 bg-blue-50' },
  'Update Required':      { key: 'statusNotAccepted', cls: 'border-amber-200 text-amber-600 bg-amber-50' },
  'Updated beneficiary':  { key: 'statusNew',         cls: 'border-green-200 text-green-600 bg-green-50' },
}

const statusLabel = computed(() => {
  const status = docMeta.value.status
  const translated = t(`statuses.registration.${status}`)
  if (translated && translated !== `statuses.registration.${status}`) return translated
  const entry = STATUS_MAP[status]
  if (entry) return t(`registration.${entry.key}`)
  if (status) return status
  return t('registration.statusDraft')
})

const statusClass = computed(() => {
  const entry = STATUS_MAP[docMeta.value.status]
  return entry?.cls || STATUS_MAP['Draft'].cls
})

const stepsList = computed(() => [
  { number: 1, label: t('registration.steps.personalData') },
  { number: 2, label: t('registration.steps.incomeDetails') },
  { number: 3, label: t('registration.steps.financialObligations') },
  { number: 4, label: t('registration.steps.additionalData') },
  ...(isScholarshipFlow.value ? [{ number: 5, label: t('scholarship.steps.request') }] : []),
])

const formData = ref({
  personalInfo: { ben_primary_idtype: 'Qatari Id', id_expiry_date: '' },
  additionalInfo: { ben_requestor_relationtype: 'The same subvention requestor', ben_sec_idtype: 'Passport' },
  familyDetails: {},
  incomeDetails: {
    ben_income: 0,
    family_income: 0,
    family_extra: 0,
    children_income: 0,
    private_income: 0,
    stock_income: 0,
    rent_income: 0,
    father_income: 0,
    mother_income: 0,
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
    files: { additional_attachments: [] },
    legalClaims: {
      correctData: false,
      verificationRight: false,
      statusAwareness: false,
    },
  },
  // Kept in memory only: it becomes the Beneficiary Request when the application is submitted.
  scholarshipRequest: {
    requested_amount: '',
    request_summary: '',
    files: {},
    declarations: Object.fromEntries(SCHOLARSHIP_DECLARATION_FIELDS.map(field => [field, false])),
  },
})

const ATTACHMENT_FIELDS = [
  'qid', 'passport', 'wife_id', 'wife_passport', 'children_identification',
  'rent_contract', 'property_deed', 'bank_statement', 'wife_bank_statement',
  'wife_credit_certificate', 'beneficiary_credit_certificate', 'children_bank_statement',
  'children_credit_information', 'social_security_certificate', 'partner_work_certificate',
  'employment_certificate', 'vehicle_certificate', 'iban_picture', 'children_schooling_proof',
  'special_needs_certificate', 'termination_letter', 'nonmarriage_proof', 'divorce_paper',
  'partner_death_certificate', 'copy_of_court_judgment', 'id_coresidents', 'id_sponsored',
  'metrash_adress', 'additional_documents',
]

function onStepError(err) {
  if (err.exc_type === 'DuplicatePersonalIDError') {
    error.value = t('registration.duplicatePersonalId')
  } else {
    error.value = err.messages?.[0] || err.message || t('registration.submitError')
  }
  submitting.value = false
}

const insertDoc = createResource({
  url: 'frappe.client.insert',
  onError: onStepError,
})

const saveDoc = createResource({
  url: 'frappe.client.save',
  onError: onStepError,
})

const workflowAction = createResource({
  url: 'frappe.model.workflow.apply_workflow',
  onError: onStepError,
})

const submitScholarship = createResource({
  url: 'afif.api.scholarship.submit_scholarship_application',
  onError: onStepError,
})

function toDocMeta(doc) {
  return {
    owner: doc.owner,
    modified: doc.modified,
    creation: doc.creation,
    docstatus: doc.docstatus,
    workflow_state: doc.workflow_state,
    status: doc.status,
    custom_notes: doc.custom_notes,
    is_scholarship: doc.is_scholarship,
  }
}

const getDoc = createResource({
  url: 'frappe.client.get',
  onSuccess(data) {
    populateFromDoc(data)
  },
  onError(err) {
    error.value = err.message || t('registration.submitError')
  },
})

function populateFromDoc(doc) {
  docName.value = doc.name
  docMeta.value = toDocMeta(doc)

  const step = doc.current_step || 0
  const nextStep = step + 1
  const resumeStep = step >= 5 ? 1 : (nextStep >= 4 ? 4 : nextStep)
  const resumeSubStep4 = step >= 5 || nextStep >= 5 ? 2 : 1

  currentStep.value = 1
  subStep4.value = 1
  maxStepReached.value = resumeStep === 4 && resumeSubStep4 === 2 ? 5 : resumeStep

  formData.value.personalInfo = {
    ar_name: doc.ar_name,
    en_name: doc.en_name,
    ben_primary_idtype: doc.ben_primary_idtype || 'Qatari Id',
    ben_primary_idnumber: doc.ben_primary_idnumber,
    id_expiry_date: doc.id_expiry_date,
    passport_number: doc.passport_number,
    ben_nationality: doc.ben_nationality,
    gender: doc.gender,
    date_of_birth: doc.date_of_birth,
    phone_number: doc.phone_number,
    guardian_mobile_number: doc.guardian_mobile_number,
    partners_phone_number: doc.partners_phone_number,
    marital_status: doc.marital_status,
    partner_name: doc.partner_name,
    expartner_name: doc.expartner_name,
    visa_type: doc.visa_type,
    residence_years: doc.residence_years,
  }

  formData.value.additionalInfo = {
    ben_requestor_relationtype: doc.ben_requestor_relationtype || 'The same subvention requestor',
    requestor_name: doc.requestor_name,
    requestor_idtype: doc.requestor_idtype,
    requestor_idnumber: doc.requestor_idnumber,
    requestor_nationality: doc.requestor_nationality,
    requestor_number: doc.requestor_number,
    ben_sec_idtype: doc.ben_sec_idtype || 'Passport',
    ben_sec_nationality: doc.ben_sec_nationality,
    ben_sec_gulf_country: doc.ben_sec_gulf_country,
    ben_sec_idnumber: doc.passport_number,
    currently_working: doc.currently_working,
    employer_name: doc.employer_name,
    employer_address: doc.employer_address,
    occupation: doc.occupation,
    worked_before: doc.worked_before,
    education_level: doc.education_level,
    sponsor_name: doc.sponsor_name,
  }

  formData.value.familyDetails = {
    family_size: doc.family_size,
    ben_dependent_count: doc.ben_dependent_count,
    family_visa_type: doc.family_visa_type,
    visa_dependent: doc.visa_dependent,
    names_and_relation_to_sponsored: doc.names_and_relation_to_sponsored,
    have_children: doc.have_children,
    partner_working: doc.partner_working,
    children_above_eighteen: doc.children_above_eighteen,
    children_in_school: doc.children_in_school,
    children_school: doc.children_school,
    children_school_information: doc.children_school_information,
    children_special_needs: doc.children_special_needs,
    afif_charity_assistance: doc.afif_charity_assistance,
    affif_assistance: doc.affif_assistance,
  }

  formData.value.incomeDetails = {
    ben_income: doc.ben_income ?? 0,
    family_income: doc.family_income ?? 0,
    family_extra: doc.family_extra ?? 0,
    children_income: doc.children_income ?? 0,
    private_income: doc.private_income ?? 0,
    stock_income: doc.stock_income ?? 0,
    rent_income: doc.rent_income ?? 0,
    father_income: doc.father_income ?? 0,
    mother_income: doc.mother_income ?? 0,
    ben_periodic_type: doc.ben_periodic_type,
    salary_amount: doc.salary_amount,
    benficiary_note: doc.benficiary_note,
    family_periodic_type: doc.family_periodic_type,
    family_income_amount: doc.family_income_amount,
    family_note: doc.family_note,
    extra_periodic_type: doc.extra_periodic_type,
    family_extra_salary: doc.family_extra_salary,
    family_extra_note: doc.family_extra_note,
    children_periodic_type: doc.children_periodic_type,
    family_children_salary: doc.family_children_salary,
    children_note: doc.children_note,
    private_business_periodicity: doc.private_business_periodicity,
    private_business_amount: doc.private_business_amount,
    private_note: doc.private_note,
    stock_market_periodicity: doc.stock_market_periodicity,
    stock_market_income: doc.stock_market_income,
    stock_market_note: doc.stock_market_note,
    rent_periodic_type: doc.rent_periodic_type,
    rent_income_amount: doc.rent_income_amount,
    rent_note: doc.rent_note,
    father_income_periodicity: doc.father_income_periodicity,
    father_income_amount: doc.father_income_amount,
    father_income_note: doc.father_income_note,
    mother_income_periodicity: doc.mother_income_periodicity,
    mother_income_amount: doc.mother_income_amount,
    mother_income_note: doc.mother_income_note,
  }

  formData.value.financialObligations = {
    family_obligation: doc.family_obligation ?? 0,
    rent_obligation: doc.rent_obligation ?? 0,
    treatment_obligation: doc.treatment_obligation ?? 0,
    debt_obligation: doc.debt_obligation ?? 0,
    tuition_obligation: doc.tuition_obligation ?? 0,
    family_obligations_installments_count: doc.family_obligations_installments_count,
    family_obligation_periodicity: doc.family_obligation_periodicity,
    family_expenses: doc.family_expenses,
    family_obligations_note: doc.family_obligations_note,
    rent_obligation_periodicity: doc.rent_obligation_periodicity,
    rent_obligations_installments_count: doc.rent_obligations_installments_count,
    rent_amount: doc.rent_amount,
    rent_obligations_note: doc.rent_obligations_note,
    treatment_obligation_periodicity: doc.treatment_obligation_periodicity,
    treatment_obligation_installments_count: doc.treatment_obligation_installments_count,
    treatment_amount: doc.treatment_amount,
    treatment_obligations_note: doc.treatment_obligations_note,
    debt_obligation_periodicity: doc.debt_obligation_periodicity,
    debt_obligations_installments_count: doc.debt_obligations_installments_count,
    bank_payments_amount: doc.bank_payments_amount,
    debt_obligations_note: doc.debt_obligations_note,
    tuition_obligation_periodicity: doc.tuition_obligation_periodicity,
    tuition_obligation_installments_count: doc.tuition_obligation_installments_count,
    tuition_obligations_note: doc.tuition_obligations_note,
    tuition_amount: doc.tuition_amount,
  }

  formData.value.additionalData = {
    housing_type: doc.housing_type,
    housing_city: doc.city,
    zone_number: doc.zone,
    street_number: doc.street_name,
    unit_number: doc.unit,
    building_number: doc.building_name,
    housing_description: doc.adress,
    has_afif_employee_relation: doc.afif_relationship,
    has_other_info: doc.additional_information,
    additional_notes: doc.additional_information_text,
    has_housemates: doc.coresidence,
    has_bank_loans: doc.bank_loans,
    court_tried: doc.court_tried,
  }

  formData.value.attachments.legalClaims = {
    correctData: !!doc.documents_confirmation,
    verificationRight: !!doc.verification_consent,
    statusAwareness: !!doc.cancellation_right,
  }

  const existingFiles = {}
  for (const field of ATTACHMENT_FIELDS) {
    if (doc[field]) existingFiles[field] = doc[field]
  }
  existingFiles.additional_attachments = (doc.additional_attachments || [])
    .map(row => row.attachment)
    .filter(Boolean)
  formData.value.attachments.files = existingFiles

  snapshot.value = cloneFormData(formData.value)
}

onMounted(() => {
  if (props.registrationName) {
    getDoc.submit({ doctype: 'Beneficiaries Registration', name: props.registrationName })
  }
  if (props.readOnly && !editing.value) {
    currentStep.value = 1
    subStep4.value = 1
  }
})

function buildAttachmentsPayload(source) {
  const lc = source.attachments.legalClaims
  const payload = {
    documents_confirmation: lc.correctData      ? 1 : 0,
    verification_consent:   lc.verificationRight ? 1 : 0,
    cancellation_right:     lc.statusAwareness   ? 1 : 0,
  }

  const lastKnownFiles = snapshot.value?.attachments?.files || {}
  for (const field of ATTACHMENT_FIELDS) {
    const val = source.attachments.files[field]
    if (typeof val === 'string') {
      payload[field] = val
    } else if (val === null) {
      // Explicit user deletion (see AttachmentsCard's deleteFile) — clear it for real.
      payload[field] = ''
    } else if (typeof lastKnownFiles[field] === 'string') {
      payload[field] = lastKnownFiles[field]
    }
  }
  payload.additional_attachments = (source.attachments.files.additional_attachments || [])
    .filter(val => typeof val === 'string')
    .map(url => ({ attachment: url }))
  return payload
}

function buildStepPayload(logicalStep, source = formData.value) {
  if (logicalStep === 1) {
    const payload = {
      ...source.personalInfo,
      ...source.additionalInfo,
      ...source.familyDetails,
      ben_sec_idnumber: source.personalInfo.passport_number,
    }
    // Defaults the cards set on hidden fields (e.g. ben_sec_idtype = Passport) must not be saved.
    return Object.fromEntries(Object.entries(payload).filter(([field]) => variant.value.isShown(field)))
  }
  if (logicalStep === 2) {
    return { ...source.incomeDetails }
  }
  if (logicalStep === 3) {
    return { ...source.financialObligations }
  }
  if (logicalStep === 4) {
    const ad = source.additionalData || {}
    return {
      housing_type:                ad.housing_type,
      city:                        ad.housing_city,
      zone:                        ad.zone_number,
      street_name:                 ad.street_number,
      unit:                        ad.unit_number,
      building_name:               ad.building_number,
      adress:                      ad.housing_description,
      afif_relationship:           ad.has_afif_employee_relation,
      additional_information:      ad.has_other_info,
      additional_information_text: ad.additional_notes,
      coresidence:                 ad.has_housemates,
      bank_loans:                  ad.has_bank_loans,
      court_tried:                 ad.court_tried,
    }
  }
  // logicalStep === 5
  return buildAttachmentsPayload(source)
}

function buildFullPayload(source = formData.value) {
  return {
    ...buildStepPayload(1, source),
    ...buildStepPayload(2, source),
    ...buildStepPayload(3, source),
    ...buildStepPayload(4, source),
    ...buildStepPayload(5, source),
  }
}

function cloneSection(section) {

  if (section instanceof File) return section
  if (Array.isArray(section)) return section.map(cloneSection)
  if (section && typeof section === 'object') {
    const out = {}
    for (const key of Object.keys(section)) out[key] = cloneSection(section[key])
    return out
  }
  return section
}

function cloneFormData(source) {
  return {
    personalInfo:          cloneSection(source.personalInfo),
    additionalInfo:        cloneSection(source.additionalInfo),
    familyDetails:         cloneSection(source.familyDetails),
    incomeDetails:         cloneSection(source.incomeDetails),
    financialObligations:  cloneSection(source.financialObligations),
    additionalData:        cloneSection(source.additionalData),
    attachments:           cloneSection(source.attachments),
  }
}

const SNAPSHOT_SECTIONS = {
  1: ['personalInfo', 'additionalInfo', 'familyDetails'],
  2: ['incomeDetails'],
  3: ['financialObligations'],
  4: ['additionalData'],
  5: ['attachments'],
}

function updateSnapshotForStep(logicalStep) {
  if (!snapshot.value) return
  for (const section of SNAPSHOT_SECTIONS[logicalStep]) {
    snapshot.value[section] = cloneSection(formData.value[section])
  }
}

function buildMergedPayload(logicalStep) {
  return {
    ...buildFullPayload(snapshot.value),
    ...buildStepPayload(logicalStep, formData.value),
  }
}

async function applyAction(action) {
  const result = await workflowAction.submit({
    doc: JSON.stringify({ doctype: 'Beneficiaries Registration', name: docName.value }),
    action,
  })
  docMeta.value = toDocMeta(result)
  return result
}

async function saveStep(logicalStep, { applyWorkflow = true } = {}) {
  // Once a doc has left Draft it's a live record reviewers can already see, so a save must only
  // ever persist the step being confirmed here — every other step's fields come from the
  // last-confirmed snapshot instead of live formData, so an edit abandoned on another step
  // (navigated away from without hitting its own Next) never reaches the backend.
  const isLiveRecord = Boolean(docName.value) && docMeta.value.status !== 'Draft' && snapshot.value
  const doc = {
    doctype: 'Beneficiaries Registration',
    current_step: logicalStep,
    email: session.user,
    // frappe.client.save rebuilds the doc from this payload, so the flag must be resent every time.
    is_scholarship: docName.value ? docMeta.value.is_scholarship : Number(isScholarshipFlow.value),
    ...(isLiveRecord ? buildMergedPayload(logicalStep) : buildFullPayload()),
  }

  const currentState = docName.value ? docMeta.value.workflow_state : null

  if (docName.value) {
    doc.name = docName.value
    doc.user = session.user
    doc.owner = docMeta.value.owner
    doc.modified = docMeta.value.modified
    doc.creation = docMeta.value.creation
    doc.docstatus = docMeta.value.docstatus
    doc.workflow_state = currentState
    doc.status = docMeta.value.status
    doc.custom_notes = docMeta.value.custom_notes
  }

  if (applyWorkflow && logicalStep >= 5 && currentState === 'Not Accepted') {
    await applyAction('Review')
    doc.modified = docMeta.value.modified
    doc.workflow_state = docMeta.value.workflow_state
    doc.status = docMeta.value.status
    doc.custom_notes = docMeta.value.custom_notes
    return saveDoc.submit({ doc })
  }

  if (!docName.value) {
    return insertDoc.submit({ doc })
  }

  const result = await saveDoc.submit({ doc })

  // A scholarship registration is submitted together with its request by submitScholarshipApplication.
  if (applyWorkflow && !doc.is_scholarship && logicalStep >= 5 && (!currentState || currentState === 'Draft')) {
    return applyAction('Submit')
  }

  return result
}

function validateStep(targetStep, targetSubStep4) {
  return validateRegistrationStep({
    formData: formData.value,
    step: targetStep,
    subStep4: targetSubStep4,
    flow: props.flow,
    t,
  })
}

function logicalStepArgs(logicalStep) {
  if (logicalStep === 4) return [4, 1]
  if (logicalStep === 5) return [4, 2]
  if (logicalStep === 6) return [5, undefined]
  return [logicalStep, undefined]
}

function validateUpToCurrentStep() {
  for (let logicalStep = 1; logicalStep <= logicalCurrentStep.value; logicalStep++) {
    const [step, subStep4Arg] = logicalStepArgs(logicalStep)
    const result = validateStep(step, subStep4Arg)
    if (result.errors.length > 0) {
      return { ...result, step, subStep4: subStep4Arg ?? 1 }
    }
  }
  return { errors: [], fields: [] }
}

function validateCurrentStepOnly() {
  const result = validateStep(currentStep.value, subStep4.value)
  return { ...result, step: currentStep.value, subStep4: subStep4.value }
}

async function handleNext() {
  error.value = ''

  const isAttachmentsStep = currentStep.value === 4 && subStep4.value === 2
  const isScholarshipRequestStep = currentStep.value === 5
  if (isAttachmentsStep && pendingAttachmentOps.size) {
    
    submitting.value = true
    await waitForPendingAttachmentOps()
    submitting.value = false
  }
  
  const validation = isAttachmentsStep || isScholarshipRequestStep ? validateUpToCurrentStep() : validateCurrentStepOnly()

  const { errors, fields, step: invalidStep, subStep4: invalidSubStep4 } = validation
  if (errors.length > 0) {
    if (invalidStep !== undefined && (invalidStep !== currentStep.value || invalidSubStep4 !== subStep4.value)) {
      currentStep.value = invalidStep
      subStep4.value = invalidSubStep4
    }
    validationErrors.value = errors
    invalidFields.value = fields
    showValidationPopup.value = true
    return
  }

  invalidFields.value = []
  submitting.value = true

  if (isScholarshipRequestStep) {
    await submitScholarshipApplication()
    submitting.value = false
    return
  }

  const wasLiveRecord = Boolean(docName.value) && docMeta.value.status !== 'Draft' && snapshot.value
  function syncSnapshot() {
    if (wasLiveRecord) {
      updateSnapshotForStep(logicalCurrentStep.value)
    } else {
      snapshot.value = cloneFormData(formData.value)
    }
  }

  let data
  try {
    data = await saveStep(logicalCurrentStep.value, { applyWorkflow: !isAttachmentsStep })
  } catch (e) {
    return
  }
  docName.value = data.name
  docMeta.value = toDocMeta(data)
  syncSnapshot()

  if (isAttachmentsStep) {
    try {
      const failedUploads = await uploadAllFiles()
      const finalData = await saveStep(logicalCurrentStep.value, { applyWorkflow: failedUploads.length === 0 })
      docMeta.value = toDocMeta(finalData)
      syncSnapshot()
      if (failedUploads.length > 0) {
        error.value = `${t('registration.submitError')}: ${failedUploads.join(', ')}`
      } else if (isScholarshipFlow.value) {
        currentStep.value = 5
        maxStepReached.value = Math.max(maxStepReached.value, logicalCurrentStep.value)
      } else {
        emit('submitted', finalData.name)
      }
    } catch (e) {
      error.value = e.message || t('registration.submitError')
    }
    submitting.value = false
    return
  }

  submitting.value = false
  if (currentStep.value === 4 && subStep4.value === 1) {
    subStep4.value = 2
  } else {
    currentStep.value++
  }
  maxStepReached.value = Math.max(maxStepReached.value, logicalCurrentStep.value)
}

async function submitScholarshipApplication() {
  const sr = formData.value.scholarshipRequest
  try {
    for (const id of SCHOLARSHIP_ATTACHMENT_FIELDS) {
      // Stored back as a URL so a retry after a failed submit reuses the upload.
      if (sr.files[id] instanceof File) sr.files[id] = await uploadUnattachedPrivateFile(sr.files[id])
    }
  } catch (e) {
    error.value = e.message || t('registration.submitError')
    return
  }

  const request = {
    requested_amount: sr.requested_amount,
    request_summary: sr.request_summary,
    ...sr.files,
    ...Object.fromEntries(SCHOLARSHIP_DECLARATION_FIELDS.map(field => [field, sr.declarations[field] ? 1 : 0])),
  }
  try {
    await submitScholarship.submit({ registration: docName.value, request })
  } catch (e) {
    return
  }
  emit('submitted', docName.value)
}

function prevStep() {
  error.value = ''
  if (currentStep.value === 5) {
    currentStep.value = 4
    subStep4.value = 2
    return
  }
  if (currentStep.value === 4 && subStep4.value === 2) {
    subStep4.value = 1
    return
  }
  if (currentStep.value > 1) currentStep.value--
}

function readOnlyNext() {
  if (currentStep.value === 4 && subStep4.value === 1) {
    subStep4.value = 2
  } else if (currentStep.value < 4) {
    currentStep.value++
  }
}

function readOnlyPrev() {
  if (currentStep.value === 4 && subStep4.value === 2) {
    subStep4.value = 1
  } else if (currentStep.value > 1) {
    currentStep.value--
  }
}

async function uploadAllFiles() {
  const failures = []

  for (const [fieldname, file] of Object.entries(formData.value.attachments.files)) {
    if (fieldname === 'additional_attachments') continue
    if (file instanceof File) {
      try {
        const fileUrl = await uploadFile(file, docName.value, fieldname)
        formData.value.attachments.files[fieldname] = fileUrl
      } catch (e) {
        failures.push(e.message || file.name)
      }
    }
  }

  const extras = formData.value.attachments.files.additional_attachments || []
  for (let i = 0; i < extras.length; i++) {
    if (extras[i] instanceof File) {
      try {
        extras[i] = await uploadFile(extras[i], docName.value, 'additional_attachments')
      } catch (e) {
        failures.push(e.message || extras[i].name)
      }
    }
  }

  return failures
}

function uploadFile(file, docName, fieldname) {
  return postFile(file, {
    is_private: '0',
    doctype: 'Beneficiaries Registration',
    docname: docName,
    fieldname,
  })
}

// The scholarship endpoint attaches these to the request it creates, after checking they are the user's own.
function uploadUnattachedPrivateFile(file) {
  return postFile(file, { is_private: '1' })
}

async function postFile(file, fields) {
  const fd = new FormData()
  fd.append('file', file, file.name)
  fd.append('folder', 'Home/Attachments')
  for (const [key, value] of Object.entries(fields)) fd.append(key, value)

  const headers = { 'X-Frappe-Site-Name': window.location.hostname }
  if (window.csrf_token && window.csrf_token !== '{{ csrf_token }}') {
    headers['X-Frappe-CSRF-Token'] = window.csrf_token
  }

  const res = await fetch('/api/method/upload_file', { method: 'POST', headers, body: fd })
  if (!res.ok) {
    if (res.status === 413) throw new Error(`${t('registration.attachments.fileTooLarge')}: ${file.name}`)
    throw new Error(`${t('registration.submitError')}: ${file.name}`)
  }
  const data = await res.json()
  return data.message.file_url
}


let attachmentSaveChain = Promise.resolve()
const pendingAttachmentOps = new Set()

function queueAttachmentSave() {
  
  const run = attachmentSaveChain.then(async () => {
    const data = await saveStep(5, { applyWorkflow: false })
    docMeta.value = toDocMeta(data)
    if (docMeta.value.status !== 'Draft' && snapshot.value) {
      updateSnapshotForStep(5)
    } else {
      snapshot.value = cloneFormData(formData.value)
    }
  })
  attachmentSaveChain = run.catch(() => {})
  return run
}

async function waitForPendingAttachmentOps() {
  while (pendingAttachmentOps.size) {
    await Promise.allSettled([...pendingAttachmentOps])
  }
}

function handleAttachmentFileSelected(id, file) {
  const op = uploadAndSaveAttachment(id, file)
  pendingAttachmentOps.add(op)
  op.finally(() => pendingAttachmentOps.delete(op))
  return op
}

async function uploadAndSaveAttachment(id, file) {
  attachmentUploadErrors.value = { ...attachmentUploadErrors.value, [id]: undefined }

  if (!docName.value) {

    formData.value.attachments.files = { ...formData.value.attachments.files, [id]: file }
    return
  }

  attachmentUploading.value = { ...attachmentUploading.value, [id]: true }
  try {
    const fileUrl = await uploadFile(file, docName.value, id)
    formData.value.attachments.files = { ...formData.value.attachments.files, [id]: fileUrl }

    await queueAttachmentSave()
  } catch (e) {
    attachmentUploadErrors.value = { ...attachmentUploadErrors.value, [id]: e.message || t('registration.submitError') }
  } finally {
    attachmentUploading.value = { ...attachmentUploading.value, [id]: false }
  }
}
</script>

<style scoped>
.read-only-form {
  pointer-events: none;
}

.read-only-form :deep(input:not([type="checkbox"])),
.read-only-form :deep(select),
.read-only-form :deep(textarea),
.read-only-form :deep(input[type="file"]) {
  opacity: 0.75;
  background-color: #f9fafb;
}

.read-only-form :deep(button) {
  opacity: 0.5;
}
</style>
