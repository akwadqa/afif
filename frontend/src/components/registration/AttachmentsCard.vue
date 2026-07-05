<template>
  <div class="space-y-6" :dir="isRTL ? 'rtl' : 'ltr'">

    <!-- Attachments list -->
    <div class="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-sm">
      <div class="flex items-center gap-2 border-b border-gray-50 pb-4 mb-6 text-[#0570B6]">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 shrink-0">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
        </svg>
        <h3 class="text-base font-bold">{{ t('registration.attachments.listTitle') }}</h3>
      </div>

      <div class="space-y-3">
        <div
          v-for="doc in visibleAttachments"
          :key="doc.id"
          class="flex flex-col md:flex-row md:items-center justify-between p-4 border rounded-xl transition-all gap-4"
          :class="isInvalid('attach_' + doc.id)
            ? 'bg-red-50/50 border-red-300'
            : 'bg-gray-50/50 hover:bg-gray-50/80 border-gray-100/70'"
        >
          <!-- Label -->
          <div class="flex-1 min-w-0">
            <div class="text-sm font-semibold text-gray-700">
              {{ t(doc.labelKey) }}
              <span v-if="doc.required" class="text-red-500">*</span>
            </div>
          </div>

          <!-- Action buttons + file name -->
          <div class="flex items-center gap-3 self-end md:self-auto shrink-0 flex-wrap rtl:flex-row-reverse">

            <!-- Upload (no file yet) -->
            <button
              v-if="!modelValue.files[doc.id]"
              type="button"
              @click="triggerFileInput(doc.id)"
              class="flex items-center gap-1.5 px-4 py-2 border border-sky-200 text-sky-600 rounded-xl bg-white hover:bg-sky-50 transition-colors text-xs font-bold shadow-sm"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4 shrink-0">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z" />
              </svg>
              <span>{{ t('registration.attachments.upload') }}</span>
            </button>

            <!-- Re-upload + Delete (file exists) -->
            <template v-else>
              <button
                type="button"
                @click="triggerFileInput(doc.id)"
                class="flex items-center gap-1.5 px-4 py-2 border border-sky-100 text-sky-600 rounded-xl bg-sky-50/40 hover:bg-sky-50 transition-colors text-xs font-semibold"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4 shrink-0">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
                </svg>
                <span>{{ t('registration.attachments.reupload') }}</span>
              </button>

              <button
                type="button"
                @click="deleteFile(doc.id)"
                class="flex items-center gap-1.5 px-3 py-2 border border-red-100 text-red-500 rounded-xl bg-red-50/30 hover:bg-red-50 transition-colors text-xs font-semibold"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4 shrink-0">
                  <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                </svg>
                <span>{{ t('registration.attachments.delete') }}</span>
              </button>
            </template>

            <span
              v-if="modelValue.files[doc.id]"
              class="text-xs text-gray-500 font-mono truncate max-w-[140px] md:max-w-[180px] inline-block align-middle"
              dir="ltr"
            >
              <a
                v-if="fileUrl(doc.id)"
                :href="fileUrl(doc.id)"
                target="_blank"
                rel="noopener"
                class="underline hover:text-sky-500"
              >{{ fileLabel(doc.id) }}</a>
              <span v-else>{{ fileLabel(doc.id) }}</span>
            </span>

            <input
              :id="`attach-input-${doc.id}`"
              type="file"
              accept=".jpg,.jpeg,.png,.ogg,.pdf, .webm"
              class="hidden"
              @change="handleFileSelected($event, doc.id)"
            />
          </div>
        </div>

        <!-- Additional attachments (multiple) -->
        <div
          v-for="(file, idx) in additionalAttachments"
          :key="idx"
          class="flex flex-col md:flex-row md:items-center justify-between p-4 border rounded-xl gap-4 bg-gray-50/50 hover:bg-gray-50/80 border-gray-100/70"
        >
          <div class="flex-1 min-w-0">
            <div class="text-sm font-semibold text-gray-700">
              {{ t('registration.attachments.docs.extraAttachments') }} #{{ idx + 1 }}
            </div>
          </div>

          <div class="flex items-center gap-3 self-end md:self-auto shrink-0 flex-wrap rtl:flex-row-reverse">
            <button
              type="button"
              @click="removeAdditionalAttachment(idx)"
              class="flex items-center gap-1.5 px-3 py-2 border border-red-100 text-red-500 rounded-xl bg-red-50/30 hover:bg-red-50 transition-colors text-xs font-semibold"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4 shrink-0">
                <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
              </svg>
              <span>{{ t('registration.attachments.delete') }}</span>
            </button>

            <span class="text-xs text-gray-500 font-mono truncate max-w-[140px] md:max-w-[180px] inline-block align-middle" dir="ltr">
              <a
                v-if="typeof file === 'string'"
                :href="file"
                target="_blank"
                rel="noopener"
                class="underline hover:text-sky-500"
              >{{ additionalAttachmentLabel(file) }}</a>
              <span v-else>{{ additionalAttachmentLabel(file) }}</span>
            </span>
          </div>
        </div>

        <!-- Add another attachment -->
        <button
          type="button"
          @click="triggerAdditionalFileInput"
          class="flex items-center gap-1.5 px-4 py-2 border border-dashed border-sky-200 text-sky-600 rounded-xl bg-white hover:bg-sky-50 transition-colors text-xs font-bold shadow-sm w-full justify-center"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4 shrink-0">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          <span>{{ t('registration.attachments.addAnother') }}</span>
        </button>
        <input
          id="additional-attachments-input"
          type="file"
          accept=".jpg,.jpeg,.png,.ogg,.pdf, .webm"
          class="hidden"
          @change="handleAdditionalFileSelected"
        />
      </div>
    </div>

    <!-- Legal claims -->
    <div class="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-sm space-y-4">
      <label
        class="flex items-start gap-3 cursor-pointer select-none rounded-xl p-2 -mx-2 transition-colors"
        :class="isInvalid('claim_correctData') ? 'bg-red-50 ring-1 ring-red-300' : ''"
      >
        <input
          type="checkbox"
          :checked="modelValue.legalClaims.correctData"
          @change="updateClaim('correctData', $event.target.checked)"
          class="custom-checkbox mt-0.5 shrink-0"
        />
        <span class="text-xs font-semibold text-gray-700 leading-relaxed">
          {{ t('registration.attachments.claimCorrectData') }}
        </span>
      </label>

      <label
        class="flex items-start gap-3 cursor-pointer select-none rounded-xl p-2 -mx-2 transition-colors"
        :class="isInvalid('claim_verificationRight') ? 'bg-red-50 ring-1 ring-red-300' : ''"
      >
        <input
          type="checkbox"
          :checked="modelValue.legalClaims.verificationRight"
          @change="updateClaim('verificationRight', $event.target.checked)"
          class="custom-checkbox mt-0.5 shrink-0"
        />
        <span class="text-xs font-semibold text-gray-700 leading-relaxed">
          {{ t('registration.attachments.claimVerificationRight') }}
        </span>
      </label>

      <label
        class="flex items-start gap-3 cursor-pointer select-none rounded-xl p-2 -mx-2 transition-colors"
        :class="isInvalid('claim_statusAwareness') ? 'bg-red-50 ring-1 ring-red-300' : ''"
      >
        <input
          type="checkbox"
          :checked="modelValue.legalClaims.statusAwareness"
          @change="updateClaim('statusAwareness', $event.target.checked)"
          class="custom-checkbox mt-0.5 shrink-0"
        />
        <span class="text-xs font-semibold text-gray-700 leading-relaxed">
          {{ t('registration.attachments.claimStatusAwareness') }}
        </span>
      </label>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useLanguage } from '@/composables/useLanguage'
import { isFileTooLarge } from '@/utils/fileValidation'

const { t, isRTL } = useLanguage()
const props = defineProps({
  modelValue: { type: Object, required: true },
  context: { type: Object, default: () => ({}) },
  invalidFields: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue'])

function isInvalid(field) {
  return props.invalidFields.includes(field)
}

const visibleAttachments = computed(() => {
  const pi = props.context.personalInfo || {}
  const ai = props.context.additionalInfo || {}
  const fd = props.context.familyDetails || {}
  const ad = props.context.additionalData || {}

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

  const all = [
    { id: 'qid',                            required: true,  labelKey: 'registration.attachments.docs.qid',                     show: true },
    { id: 'passport',                        required: true,  labelKey: 'registration.attachments.docs.passport',                 show: true },
    { id: 'wife_id',                         required: true,  labelKey: 'registration.attachments.docs.wifeId',                   show: isMarried },
    { id: 'wife_passport',                   required: true,  labelKey: 'registration.attachments.docs.wifePassport',             show: isMarried },
    { id: 'children_identification',         required: true,  labelKey: 'registration.attachments.docs.childrenId',              show: hasChildren },
    { id: 'rent_contract',                   required: true,  labelKey: 'registration.attachments.docs.rentContract',            show: isRental },
    { id: 'property_deed',                   required: true,  labelKey: 'registration.attachments.docs.property',                show: isOwned },
    { id: 'bank_statement',                  required: true,  labelKey: 'registration.attachments.docs.bankStatement',           show: isResidence },
    { id: 'wife_bank_statement',             required: true,  labelKey: 'registration.attachments.docs.wifeBankStatement',       show: isMarried && familyResidence },
    { id: 'wife_credit_certificate',         required: true,  labelKey: 'registration.attachments.docs.wifeCredit',              show: isMarried && familyResidence },
    { id: 'beneficiary_credit_certificate',  required: true,  labelKey: 'registration.attachments.docs.creditBureau',            show: isResidence },
    { id: 'children_bank_statement',         required: true,  labelKey: 'registration.attachments.docs.childrenBankStatement',   show: familyResidence && childrenAbove18 },
    { id: 'children_credit_information',     required: true,  labelKey: 'registration.attachments.docs.childrenCredit',          show: familyResidence && childrenAbove18 },
    { id: 'social_security_certificate',     required: true,  labelKey: 'registration.attachments.docs.socialSecurityCert',      show: isQatari && notWorking },
    { id: 'partner_work_certificate',        required: true,  labelKey: 'registration.attachments.docs.partnerWorkCert',         show: partnerWorking },
    { id: 'employment_certificate',          required: true,  labelKey: 'registration.attachments.docs.employmentCert',          show: working },
    { id: 'vehicle_certificate',             required: true,  labelKey: 'registration.attachments.docs.trafficCar',              show: isResidence },
    { id: 'iban_picture',                    required: true,  labelKey: 'registration.attachments.docs.ibanPhoto',               show: isResidence },
    { id: 'children_schooling_proof',        required: true,  labelKey: 'registration.attachments.docs.childrenSchoolProof',     show: childrenSchool },
    { id: 'special_needs_certificate',       required: true,  labelKey: 'registration.attachments.docs.specialNeedsCert',        show: childSpecial },
    { id: 'termination_letter',              required: true,  labelKey: 'registration.attachments.docs.terminationLetter',       show: notWorking && workedBefore },
    { id: 'nonmarriage_proof',               required: true,  labelKey: 'registration.attachments.docs.nonmarriageProof',        show: isDivorced || isWidowed },
    { id: 'divorce_paper',                   required: true,  labelKey: 'registration.attachments.docs.divorcePaper',            show: isDivorced },
    { id: 'partner_death_certificate',       required: true,  labelKey: 'registration.attachments.docs.partnerDeathCert',        show: isWidowed },
    { id: 'copy_of_court_judgment',          required: true,  labelKey: 'registration.attachments.docs.courtJudgment',           show: hasBankLoans && courtTried },
    { id: 'id_coresidents',                  required: true,  labelKey: 'registration.attachments.docs.coresidentsId',           show: hasHousemates },
    { id: 'id_sponsored',                    required: true,  labelKey: 'registration.attachments.docs.sponsoredId',             show: visaDependent },
    { id: 'metrash_adress',                  required: true,  labelKey: 'registration.attachments.docs.metrashAddress',          show: true },
  ]

  return all.filter(d => d.show)
})

function fileLabel(id) {
  const value = props.modelValue.files[id]
  if (value instanceof File) return value.name
  if (typeof value === 'string') return value.split('/').pop()
  return ''
}

function fileUrl(id) {
  const value = props.modelValue.files[id]
  return typeof value === 'string' ? value : null
}

function triggerFileInput(id) {
  document.getElementById(`attach-input-${id}`)?.click()
}

const ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'ogg', 'webm']

function handleFileSelected(event, id) {
  const file = event.target.files[0]
  if (!file) return

  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!ext || !ALLOWED_EXTENSIONS.includes(ext)) {
    alert(t('registration.attachments.invalidFileType'))
    event.target.value = ''
    return
  }

  if (isFileTooLarge(file)) {
    alert(t('registration.attachments.fileTooLarge'))
    event.target.value = ''
    return
  }

  emit('update:modelValue', {
    ...props.modelValue,
    files: { ...props.modelValue.files, [id]: file },
  })
  event.target.value = ''
}

function deleteFile(id) {
  const files = { ...props.modelValue.files }
  delete files[id]
  emit('update:modelValue', { ...props.modelValue, files })
}

const additionalAttachments = computed(() => props.modelValue.files.additional_attachments || [])

function additionalAttachmentLabel(value) {
  if (value instanceof File) return value.name
  if (typeof value === 'string') return value.split('/').pop()
  return ''
}

function triggerAdditionalFileInput() {
  document.getElementById('additional-attachments-input')?.click()
}

function handleAdditionalFileSelected(event) {
  const file = event.target.files[0]
  if (!file) return

  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!ext || !ALLOWED_EXTENSIONS.includes(ext)) {
    alert(t('registration.attachments.invalidFileType'))
    event.target.value = ''
    return
  }

  if (isFileTooLarge(file)) {
    alert(t('registration.attachments.fileTooLarge'))
    event.target.value = ''
    return
  }

  emit('update:modelValue', {
    ...props.modelValue,
    files: { ...props.modelValue.files, additional_attachments: [...additionalAttachments.value, file] },
  })
  event.target.value = ''
}

function removeAdditionalAttachment(idx) {
  const list = [...additionalAttachments.value]
  list.splice(idx, 1)
  emit('update:modelValue', {
    ...props.modelValue,
    files: { ...props.modelValue.files, additional_attachments: list },
  })
}

function updateClaim(key, value) {
  emit('update:modelValue', {
    ...props.modelValue,
    legalClaims: { ...props.modelValue.legalClaims, [key]: value },
  })
}
</script>

<style scoped>
.custom-checkbox {
  @apply w-4 h-4 rounded border-gray-300 text-[#34B0EE] focus:ring-[#34B0EE] transition-all;
}
</style>
