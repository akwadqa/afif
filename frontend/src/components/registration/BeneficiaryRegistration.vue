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
        <PersonalInfoCard v-model="formData.personalInfo" :invalid-fields="invalidFields" />
        <AdditionalInfoCard v-model="formData.additionalInfo" :personal-info="formData.personalInfo" :invalid-fields="invalidFields" />
        <FamilyDetailsCard v-model="formData.familyDetails" :personal-info="formData.personalInfo" :invalid-fields="invalidFields" />
      </div>

      <div v-else-if="currentStep === 2">
        <IncomeDetailsCard v-model="formData.incomeDetails" :invalid-fields="invalidFields" />
      </div>

      <div v-else-if="currentStep === 3">
        <FinancialObligationsCard v-model="formData.financialObligations" :invalid-fields="invalidFields" />
      </div>

      <div v-else-if="currentStep === 4">
        <AdditionalDataCard v-if="subStep4 === 1" v-model="formData.additionalData" :invalid-fields="invalidFields" />
        <AttachmentsCard v-else-if="subStep4 === 2" v-model="formData.attachments" :context="formData" :invalid-fields="invalidFields" />
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
import FormStepsBar from './FormStepsBar.vue'
import FormActionsBar from './FormActionsBar.vue'
import PersonalInfoCard from './PersonalInfoCard.vue'
import AdditionalInfoCard from './AdditionalInfoCard.vue'
import FamilyDetailsCard from './FamilyDetailsCard.vue'
import IncomeDetailsCard from './IncomeDetailsCard.vue'
import FinancialObligationsCard from './FinancialObligationsCard.vue'
import AdditionalDataCard from './AdditionalDataCard.vue'
import AttachmentsCard from './AttachmentsCard.vue'
import ValidationErrorPopup from './ValidationErrorPopup.vue'

const props = defineProps({
  registrationName: { type: String, default: null },
})

const emit = defineEmits(['submitted'])
const { t, isRTL } = useLanguage()

const currentStep = ref(1)
const subStep4 = ref(1)
const submitting = ref(false)
const error = ref('')
const docName = ref(null)
const showValidationPopup = ref(false)
const validationErrors = ref([])
const invalidFields = ref([])

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
  error.value = err.messages?.[0] || err.message || t('registration.submitError')
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

  const step = doc.current_step || 1
  currentStep.value = step >= 4 ? 4 : step
  subStep4.value = step >= 5 ? 2 : 1

  formData.value.personalInfo = {
    ar_name: doc.ar_name,
    en_name: doc.en_name,
    ben_primary_idtype: doc.ben_primary_idtype,
    ben_primary_idnumber: doc.ben_primary_idnumber,
    ben_nationality: doc.ben_nationality,
    gender: doc.gender,
    date_of_birth: doc.date_of_birth,
    phone_number: doc.phone_number,
    marital_status: doc.marital_status,
    partner_name: doc.partner_name,
    expartner_name: doc.expartner_name,
    visa_type: doc.visa_type,
    residence_years: doc.residence_years,
  }

  formData.value.additionalInfo = {
    ben_requestor_relationtype: doc.ben_requestor_relationtype,
    requestor_name: doc.requestor_name,
    requestor_idtype: doc.requestor_idtype,
    requestor_idnumber: doc.requestor_idnumber,
    requestor_nationality: doc.requestor_nationality,
    requestor_number: doc.requestor_number,
    ben_sec_idtype: doc.ben_sec_idtype,
    ben_sec_nationality: doc.ben_sec_nationality,
    ben_sec_gulf_country: doc.ben_sec_gulf_country,
    ben_sec_idnumber: doc.ben_sec_idnumber,
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
  formData.value.attachments.files = existingFiles
}

onMounted(() => {
  if (props.registrationName) {
    getDoc.submit({ doctype: 'Beneficiaries Registration', name: props.registrationName })
  }
})

function buildStepPayload(logicalStep) {
  if (logicalStep === 1) {
    return {
      ...formData.value.personalInfo,
      ...formData.value.additionalInfo,
      ...formData.value.familyDetails,
    }
  }
  if (logicalStep === 2) {
    return { ...formData.value.incomeDetails }
  }
  if (logicalStep === 3) {
    return { ...formData.value.financialObligations }
  }
  if (logicalStep === 4) {
    const ad = formData.value.additionalData || {}
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
  const lc = formData.value.attachments.legalClaims
  return {
    documents_confirmation: lc.correctData      ? 1 : 0,
    verification_consent:   lc.verificationRight ? 1 : 0,
    cancellation_right:     lc.statusAwareness   ? 1 : 0,
  }
}

async function saveStep(logicalStep) {
  const doc = {
    doctype: 'Beneficiaries Registration',
    current_step: logicalStep,
    status: logicalStep >= 5 ? 'New Registration' : 'Draft',
    ...buildStepPayload(logicalStep),
  }

  if (docName.value) {
    doc.name = docName.value
    return saveDoc.submit({ doc })
  }
  return insertDoc.submit({ doc })
}

function validateCurrentStep() {
  const pi = formData.value.personalInfo
  const ai = formData.value.additionalInfo
  const fd = formData.value.familyDetails
  const id = formData.value.incomeDetails
  const fo = formData.value.financialObligations
  const ad = formData.value.additionalData
  const at = formData.value.attachments

  const errors = []
  const fields = []

  function req(value, field, label) {
    if (value === undefined || value === null || value === '') {
      errors.push(label)
      fields.push(field)
    }
  }

  if (currentStep.value === 1) {
    req(pi.ar_name, 'ar_name', t('registration.personalInfo.arName'))
    req(pi.en_name, 'en_name', t('registration.personalInfo.enName'))
    req(pi.ben_primary_idtype, 'ben_primary_idtype', t('registration.personalInfo.primaryIdType'))
    req(pi.ben_primary_idnumber, 'ben_primary_idnumber', t('registration.personalInfo.primaryIdNumber'))
    req(pi.ben_nationality, 'ben_nationality', t('registration.personalInfo.nationality'))
    req(pi.gender, 'gender', t('registration.personalInfo.gender'))
    req(pi.date_of_birth, 'date_of_birth', t('registration.personalInfo.dob'))
    req(pi.phone_number, 'phone_number', t('registration.personalInfo.phone'))
    req(pi.marital_status, 'marital_status', t('registration.personalInfo.maritalStatus'))
    if (pi.marital_status === 'Married') req(pi.partner_name, 'partner_name', t('registration.personalInfo.partnerName'))
    if (pi.marital_status === 'Divorced' || pi.marital_status === 'Widowed') req(pi.expartner_name, 'expartner_name', t('registration.personalInfo.exPartnerName'))
    if (pi.ben_nationality && pi.ben_nationality !== 'Qatar') {
      req(pi.visa_type, 'visa_type', t('registration.personalInfo.visaType'))
      req(pi.residence_years, 'residence_years', t('registration.personalInfo.residenceYears'))
    }

    req(ai.ben_requestor_relationtype, 'ben_requestor_relationtype', t('registration.additionalInfo.requestorRelation'))
    if (ai.ben_requestor_relationtype === 'Relative to the subvention requestor') {
      req(ai.requestor_name, 'requestor_name', t('registration.additionalInfo.requestorName'))
      req(ai.requestor_idtype, 'requestor_idtype', t('registration.additionalInfo.requestorIdType'))
      req(ai.requestor_idnumber, 'requestor_idnumber', t('registration.additionalInfo.requestorIdNumber'))
      req(ai.requestor_nationality, 'requestor_nationality', t('registration.additionalInfo.requestorNationality'))
      req(ai.requestor_number, 'requestor_number', t('registration.additionalInfo.requestorPhone'))
    }
    req(ai.ben_sec_idtype, 'ben_sec_idtype', t('registration.additionalInfo.secIdType'))
    if (ai.ben_sec_idtype === 'Passport') req(ai.ben_sec_nationality, 'ben_sec_nationality', t('registration.additionalInfo.secNationality'))
    if (ai.ben_sec_idtype === 'GCC Id') req(ai.ben_sec_gulf_country, 'ben_sec_gulf_country', t('registration.additionalInfo.gulfCountry'))
    req(ai.currently_working, 'currently_working', t('registration.additionalInfo.currentlyWorking'))
    if (ai.currently_working === 'Yes') {
      req(ai.employer_name, 'employer_name', t('registration.additionalInfo.employerName'))
      req(ai.employer_address, 'employer_address', t('registration.additionalInfo.employerAddress'))
      req(ai.occupation, 'occupation', t('registration.additionalInfo.occupation'))
    }
    if (pi.visa_type === 'Residence' && ai.currently_working === 'No') req(ai.worked_before, 'worked_before', t('registration.additionalInfo.workedBefore'))
    req(ai.education_level, 'education_level', t('registration.additionalInfo.educationLevel'))
    req(ai.sponsor_name, 'sponsor_name', t('registration.additionalInfo.sponsorName'))

    req(fd.family_size, 'family_size', t('registration.familyDetails.familySize'))
    if (fd.ben_dependent_count === undefined || fd.ben_dependent_count === null || fd.ben_dependent_count === '') {
      errors.push(t('registration.familyDetails.dependentCount'))
      fields.push('ben_dependent_count')
    }
    req(fd.family_visa_type, 'family_visa_type', t('registration.familyDetails.familyVisa'))
    if (pi.visa_type === 'Residence') {
      req(fd.visa_dependent, 'visa_dependent', t('registration.familyDetails.otherDependents'))
      if (fd.visa_dependent === 'Yes') req(fd.names_and_relation_to_sponsored, 'names_and_relation_to_sponsored', t('registration.familyDetails.namesRelation'))
    }
    req(fd.have_children, 'have_children', t('registration.familyDetails.haveChildren'))
    if (pi.marital_status === 'Married') req(fd.partner_working, 'partner_working', t('registration.familyDetails.partnerWorking'))
    if (fd.have_children === 'Yes') {
      req(fd.children_above_eighteen, 'children_above_eighteen', t('registration.familyDetails.childrenAbove18'))
      req(fd.children_in_school, 'children_in_school', t('registration.familyDetails.childrenInSchool'))
      if (fd.children_in_school === 'Yes') {
        req(fd.children_school, 'children_school', t('registration.familyDetails.childrenSchoolType'))
        req(fd.children_school_information, 'children_school_information', t('registration.familyDetails.childrenSchoolInfo'))
      }
      req(fd.children_special_needs, 'children_special_needs', t('registration.familyDetails.childrenSpecialNeeds'))
    }
    req(fd.afif_charity_assistance, 'afif_charity_assistance', t('registration.familyDetails.afifAssistance'))
    if (fd.afif_charity_assistance === 'Yes') req(fd.affif_assistance, 'affif_assistance', t('registration.familyDetails.afifAssistanceAmount'))
  }

  if (currentStep.value === 2) {
    const incomeSources = [
      { field: 'ben_income',      periodicField: 'ben_periodic_type',           periodicLabel: t('registration.incomeDetails.benPeriodicLabel'),      amountField: 'salary_amount',           amountLabel: t('registration.incomeDetails.salaryAmount'),    noteField: 'benficiary_note',     noteLabel: t('registration.incomeDetails.benNoteLabel') },
      { field: 'family_income',   periodicField: 'family_periodic_type',        periodicLabel: t('registration.incomeDetails.familyPeriodicLabel'),   amountField: 'family_income_amount',    amountLabel: t('registration.incomeDetails.familyAmount'),    noteField: 'family_note',         noteLabel: t('registration.incomeDetails.familyNoteLabel') },
      { field: 'family_extra',    periodicField: 'extra_periodic_type',         periodicLabel: t('registration.incomeDetails.extraPeriodicLabel'),    amountField: 'family_extra_salary',     amountLabel: t('registration.incomeDetails.extraAmount'),     noteField: 'family_extra_note',   noteLabel: t('registration.incomeDetails.extraNoteLabel') },
      { field: 'children_income', periodicField: 'children_periodic_type',      periodicLabel: t('registration.incomeDetails.childrenPeriodicLabel'), amountField: 'family_children_salary',  amountLabel: t('registration.incomeDetails.childrenAmount'),  noteField: 'children_note',       noteLabel: t('registration.incomeDetails.childrenNoteLabel') },
      { field: 'private_income',  periodicField: 'private_business_periodicity',periodicLabel: t('registration.incomeDetails.privatePeriodicLabel'),  amountField: 'private_business_amount', amountLabel: t('registration.incomeDetails.privateAmount'),   noteField: 'private_note',        noteLabel: t('registration.incomeDetails.privateNoteLabel') },
      { field: 'stock_income',    periodicField: 'stock_market_periodicity',    periodicLabel: t('registration.incomeDetails.stockPeriodicLabel'),    amountField: 'stock_market_income',     amountLabel: t('registration.incomeDetails.stockAmount'),     noteField: 'stock_market_note',   noteLabel: t('registration.incomeDetails.stockNoteLabel') },
      { field: 'rent_income',     periodicField: 'rent_periodic_type',          periodicLabel: t('registration.incomeDetails.rentPeriodicLabel'),     amountField: 'rent_income_amount',      amountLabel: t('registration.incomeDetails.rentAmount'),      noteField: 'rent_note',           noteLabel: t('registration.incomeDetails.rentNoteLabel') },
    ]
    for (const src of incomeSources) {
      if (id[src.field] == 1) {
        req(id[src.periodicField], src.periodicField, src.periodicLabel)
        req(id[src.amountField], src.amountField, src.amountLabel)
        req(id[src.noteField], src.noteField, src.noteLabel)
      }
    }
  }

  if (currentStep.value === 3) {
    const obligationSources = [
      { field: 'family_obligation',   subFields: [
        { name: 'family_obligations_installments_count', label: t('registration.financialObligations.familyInstallmentsLabel') },
        { name: 'family_obligation_periodicity',         label: t('registration.financialObligations.familyPeriodicLabel') },
        { name: 'family_expenses',                       label: t('registration.financialObligations.familyAmountLabel') },
        { name: 'family_obligations_note',               label: t('registration.financialObligations.familyNoteLabel') },
      ]},
      { field: 'rent_obligation',     subFields: [
        { name: 'rent_obligation_periodicity',           label: t('registration.financialObligations.rentPeriodicLabel') },
        { name: 'rent_obligations_installments_count',   label: t('registration.financialObligations.rentInstallmentsLabel') },
        { name: 'rent_amount',                           label: t('registration.financialObligations.rentAmountLabel') },
        { name: 'rent_obligations_note',                 label: t('registration.financialObligations.rentNoteLabel') },
      ]},
      { field: 'treatment_obligation',subFields: [
        { name: 'treatment_obligation_periodicity',          label: t('registration.financialObligations.treatmentPeriodicLabel') },
        { name: 'treatment_obligation_installments_count',   label: t('registration.financialObligations.treatmentInstallmentsLabel') },
        { name: 'treatment_amount',                          label: t('registration.financialObligations.treatmentAmountLabel') },
        { name: 'treatment_obligations_note',                label: t('registration.financialObligations.treatmentNoteLabel') },
      ]},
      { field: 'debt_obligation',     subFields: [
        { name: 'debt_obligation_periodicity',           label: t('registration.financialObligations.debtPeriodicLabel') },
        { name: 'debt_obligations_installments_count',   label: t('registration.financialObligations.debtInstallmentsLabel') },
        { name: 'bank_payments_amount',                  label: t('registration.financialObligations.debtAmountLabel') },
        { name: 'debt_obligations_note',                 label: t('registration.financialObligations.debtNoteLabel') },
      ]},
      { field: 'tuition_obligation',  subFields: [
        { name: 'tuition_obligation_periodicity',          label: t('registration.financialObligations.tuitionPeriodicLabel') },
        { name: 'tuition_obligation_installments_count',   label: t('registration.financialObligations.tuitionInstallmentsLabel') },
        { name: 'tuition_obligations_note',                label: t('registration.financialObligations.tuitionNoteLabel') },
        { name: 'tuition_amount',                          label: t('registration.financialObligations.tuitionAmountLabel') },
      ]},
    ]
    for (const src of obligationSources) {
      if (fo[src.field] == 1) {
        for (const f of src.subFields) req(fo[f.name], f.name, f.label)
      }
    }
  }

  if (currentStep.value === 4 && subStep4.value === 1) {
    req(ad.housing_type, 'housing_type', t('registration.additionalData.housingType'))
    req(ad.housing_city, 'housing_city', t('registration.additionalData.city'))
    req(ad.zone_number, 'zone_number', t('registration.additionalData.zoneNumber'))
    req(ad.street_number, 'street_number', t('registration.additionalData.streetNumber'))
    req(ad.unit_number, 'unit_number', t('registration.additionalData.unitNumber'))
    req(ad.building_number, 'building_number', t('registration.additionalData.buildingNumber'))
    req(ad.housing_description, 'housing_description', t('registration.additionalData.housingDescription'))
    req(ad.has_afif_employee_relation, 'has_afif_employee_relation', t('registration.additionalData.afifRelation'))
    req(ad.has_housemates, 'has_housemates', t('registration.additionalData.housemates'))
    req(ad.has_bank_loans, 'has_bank_loans', t('registration.additionalData.bankLoans'))
    if (ad.has_bank_loans === 'Yes') req(ad.court_tried, 'court_tried', t('registration.additionalData.courtTried'))
    req(ad.has_other_info, 'has_other_info', t('registration.additionalData.otherInfo'))
    if (ad.has_other_info === 'Yes') req(ad.additional_notes, 'additional_notes', t('registration.additionalData.additionalNotes'))
  }

  if (currentStep.value === 4 && subStep4.value === 2) {
    const files = at.files
    const lc = at.legalClaims
    const isMarried       = pi.marital_status === 'Married'
    const isDivorced      = pi.marital_status === 'Divorced'
    const isWidowed       = pi.marital_status === 'Widowed'
    const isResidence     = pi.visa_type === 'Residence'
    const isQatari        = pi.ben_nationality === 'Qatar'
    const hasChildren     = fd.have_children === 'Yes'
    const childrenAbove18 = fd.children_above_eighteen === 'Yes'
    const childrenSchool  = fd.children_in_school === 'Yes'
    const childSpecial    = fd.children_special_needs === 'Yes'
    const familyResidence = fd.family_visa_type === 'Residence'
    const partnerWorking  = fd.partner_working === 'Yes'
    const visaDependent   = fd.visa_dependent === 'Yes'
    const working         = ai.currently_working === 'Yes'
    const notWorking      = ai.currently_working === 'No'
    const workedBefore    = ai.worked_before === 'Yes'
    const hasHousemates   = ad.has_housemates === 'Yes'
    const hasBankLoans    = ad.has_bank_loans === 'Yes'
    const courtTried      = ad.court_tried === 'Yes'
    const isRental        = ad.housing_type === 'Rental'
    const isOwned         = ad.housing_type === 'Private Ownership'

    const requiredDocs = [
      { id: 'qid',                            labelKey: 'registration.attachments.docs.qid',                  show: true },
      { id: 'passport',                       labelKey: 'registration.attachments.docs.passport',             show: true },
      { id: 'wife_id',                        labelKey: 'registration.attachments.docs.wifeId',               show: isMarried },
      { id: 'wife_passport',                  labelKey: 'registration.attachments.docs.wifePassport',         show: isMarried },
      { id: 'children_identification',        labelKey: 'registration.attachments.docs.childrenId',          show: hasChildren },
      { id: 'rent_contract',                  labelKey: 'registration.attachments.docs.rentContract',        show: isRental },
      { id: 'property_deed',                  labelKey: 'registration.attachments.docs.property',            show: isOwned },
      { id: 'bank_statement',                 labelKey: 'registration.attachments.docs.bankStatement',       show: isResidence },
      { id: 'wife_bank_statement',            labelKey: 'registration.attachments.docs.wifeBankStatement',   show: isMarried && familyResidence },
      { id: 'wife_credit_certificate',        labelKey: 'registration.attachments.docs.wifeCredit',          show: isMarried && familyResidence },
      { id: 'beneficiary_credit_certificate', labelKey: 'registration.attachments.docs.creditBureau',        show: isResidence },
      { id: 'children_bank_statement',        labelKey: 'registration.attachments.docs.childrenBankStatement',show: familyResidence && childrenAbove18 },
      { id: 'children_credit_information',    labelKey: 'registration.attachments.docs.childrenCredit',      show: familyResidence && childrenAbove18 },
      { id: 'social_security_certificate',    labelKey: 'registration.attachments.docs.socialSecurityCert',  show: isQatari && notWorking },
      { id: 'partner_work_certificate',       labelKey: 'registration.attachments.docs.partnerWorkCert',     show: partnerWorking },
      { id: 'employment_certificate',         labelKey: 'registration.attachments.docs.employmentCert',      show: working },
      { id: 'vehicle_certificate',            labelKey: 'registration.attachments.docs.trafficCar',          show: isResidence },
      { id: 'iban_picture',                   labelKey: 'registration.attachments.docs.ibanPhoto',           show: isResidence },
      { id: 'children_schooling_proof',       labelKey: 'registration.attachments.docs.childrenSchoolProof', show: childrenSchool },
      { id: 'special_needs_certificate',      labelKey: 'registration.attachments.docs.specialNeedsCert',    show: childSpecial },
      { id: 'termination_letter',             labelKey: 'registration.attachments.docs.terminationLetter',   show: notWorking && workedBefore },
      { id: 'nonmarriage_proof',              labelKey: 'registration.attachments.docs.nonmarriageProof',    show: isDivorced || isWidowed },
      { id: 'divorce_paper',                  labelKey: 'registration.attachments.docs.divorcePaper',        show: isDivorced },
      { id: 'partner_death_certificate',      labelKey: 'registration.attachments.docs.partnerDeathCert',    show: isWidowed },
      { id: 'copy_of_court_judgment',         labelKey: 'registration.attachments.docs.courtJudgment',       show: hasBankLoans && courtTried },
      { id: 'id_coresidents',                 labelKey: 'registration.attachments.docs.coresidentsId',       show: hasHousemates },
      { id: 'id_sponsored',                   labelKey: 'registration.attachments.docs.sponsoredId',         show: visaDependent },
    ]
    for (const doc of requiredDocs.filter(d => d.show)) {
      if (!files[doc.id]) { errors.push(t(doc.labelKey)); fields.push(`attach_${doc.id}`) }
    }
    if (!lc.correctData)      { errors.push('الإقرار بصحة البيانات');           fields.push('claim_correctData') }
    if (!lc.verificationRight) { errors.push('الإقرار بحق التحقق من الأهلية'); fields.push('claim_verificationRight') }
    if (!lc.statusAwareness)   { errors.push('الإقرار بطبيعة التسجيل');         fields.push('claim_statusAwareness') }
  }

  return { errors, fields }
}

async function handleNext() {
  error.value = ''

  const { errors, fields } = validateCurrentStep()
  if (errors.length > 0) {
    validationErrors.value = errors
    invalidFields.value = fields
    showValidationPopup.value = true
    return
  }

  invalidFields.value = []
  submitting.value = true

  const isFinalStep = currentStep.value === 4 && subStep4.value === 2
  let data
  try {
    data = await saveStep(logicalCurrentStep.value)
  } catch (e) {
    return
  }
  docName.value = data.name

  if (isFinalStep) {
    try {
      await uploadAllFiles()
      emit('submitted', data.name)
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
}

function prevStep() {
  error.value = ''
  if (currentStep.value === 4 && subStep4.value === 2) {
    subStep4.value = 1
    return
  }
  if (currentStep.value > 1) currentStep.value--
}

async function uploadAllFiles() {
  for (const [fieldname, file] of Object.entries(formData.value.attachments.files)) {
    if (file instanceof File) await uploadFile(file, docName.value, fieldname)
  }
}

async function uploadFile(file, docName, fieldname) {
  const fd = new FormData()
  fd.append('file', file, file.name)
  fd.append('is_private', '0')
  fd.append('folder', 'Home/Attachments')
  fd.append('doctype', 'Beneficiaries Registration')
  fd.append('docname', docName)
  fd.append('fieldname', fieldname)

  const headers = { 'X-Frappe-Site-Name': window.location.hostname }
  if (window.csrf_token && window.csrf_token !== '{{ csrf_token }}') {
    headers['X-Frappe-CSRF-Token'] = window.csrf_token
  }

  const res = await fetch('/api/method/upload_file', { method: 'POST', headers, body: fd })
  if (!res.ok) throw new Error(`${t('registration.submitError')}: ${file.name}`)
  return res.json()
}
</script>
