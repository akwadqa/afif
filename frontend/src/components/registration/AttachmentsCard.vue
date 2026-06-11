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
          v-for="doc in attachmentDefs"
          :key="doc.id"
          class="flex flex-col md:flex-row md:items-center justify-between p-4 bg-gray-50/50 hover:bg-gray-50/80 border border-gray-100/70 rounded-xl transition-all gap-4"
        >
          <!-- Label + file info -->
          <div class="space-y-1 flex-1 min-w-0">
            <div class="text-sm font-semibold text-gray-700">
              {{ t(doc.labelKey) }} <span class="text-red-500">*</span>
            </div>
            <div
              v-if="modelValue.files[doc.id]"
              class="text-xs text-gray-400 font-mono truncate max-w-xs"
              dir="ltr"
            >
              {{ modelValue.files[doc.id].name }}
            </div>
          </div>

          <!-- Action buttons -->
          <div class="flex items-center gap-2 self-end md:self-auto shrink-0">

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

            <input
              :id="`attach-input-${doc.id}`"
              type="file"
              class="hidden"
              @change="handleFileSelected($event, doc.id)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Legal claims -->
    <div class="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-sm space-y-4">
      <label class="flex items-start gap-3 cursor-pointer select-none">
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

      <label class="flex items-start gap-3 cursor-pointer select-none">
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

      <label class="flex items-start gap-3 cursor-pointer select-none">
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
import { useLanguage } from '@/composables/useLanguage'

const { t, isRTL } = useLanguage()
const props = defineProps({ modelValue: { type: Object, required: true } })
const emit = defineEmits(['update:modelValue'])

const attachmentDefs = [
  { id: 'qid',              labelKey: 'registration.attachments.docs.qid' },
  { id: 'passport',         labelKey: 'registration.attachments.docs.passport' },
  { id: 'property',         labelKey: 'registration.attachments.docs.property' },
  { id: 'bank_statement',   labelKey: 'registration.attachments.docs.bankStatement' },
  { id: 'credit_bureau',    labelKey: 'registration.attachments.docs.creditBureau' },
  { id: 'metrash_address',  labelKey: 'registration.attachments.docs.metrashAddress' },
  { id: 'extra_attachments',labelKey: 'registration.attachments.docs.extraAttachments' },
  { id: 'traffic_car',      labelKey: 'registration.attachments.docs.trafficCar' },
  { id: 'iban_photo',       labelKey: 'registration.attachments.docs.ibanPhoto' },
  { id: 'coresidents_id',   labelKey: 'registration.attachments.docs.coresidentsId' },
]

function triggerFileInput(id) {
  document.getElementById(`attach-input-${id}`)?.click()
}

function handleFileSelected(event, id) {
  const file = event.target.files[0]
  if (!file) return
  emit('update:modelValue', {
    ...props.modelValue,
    files: { ...props.modelValue.files, [id]: file },
  })
  // Reset so the same file can be reselected
  event.target.value = ''
}

function deleteFile(id) {
  const files = { ...props.modelValue.files }
  delete files[id]
  emit('update:modelValue', { ...props.modelValue, files })
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
