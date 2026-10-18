<template>
  <div class="space-y-6" :dir="isRTL ? 'rtl' : 'ltr'">

    <!-- Amount and summary -->
    <div class="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-sm">
      <div class="flex items-center gap-2 border-b border-gray-50 pb-4 mb-6 text-[#0570B6]">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 shrink-0">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.636 50.636 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.903 59.903 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342" />
        </svg>
        <h3 class="text-base font-bold">{{ t('scholarship.request.title') }}</h3>
      </div>

      <div class="space-y-5">
        <div class="space-y-1.5">
          <label class="input-label">{{ t('scholarship.request.requestedAmount') }} <span class="text-red-500">*</span></label>
          <input
            type="text"
            inputmode="numeric"
            :value="modelValue.requested_amount"
            @input="onAmountInput"
            :placeholder="t('scholarship.request.amountPlaceholder')"
            class="custom-input font-sans"
            :class="{ 'border-red-300 bg-red-50/30': isInvalid('requested_amount') }"
          />
          <p v-if="amountLetterWarning" class="text-xs text-red-500">
            {{ t('registration.validation.noLetters') }}
          </p>
        </div>

        <div class="space-y-1.5">
          <label class="input-label">{{ t('scholarship.request.summary') }}</label>
          <textarea
            rows="4"
            maxlength="1000"
            :value="modelValue.request_summary"
            @input="update({ request_summary: $event.target.value })"
            :placeholder="t('scholarship.request.summaryPlaceholder')"
            class="custom-textarea"
          ></textarea>
        </div>
      </div>
    </div>

    <!-- Attachments -->
    <div class="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-sm">
      <div class="flex items-center gap-2 border-b border-gray-50 pb-4 mb-6 text-[#0570B6]">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 shrink-0">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
        </svg>
        <h3 class="text-base font-bold">{{ t('scholarship.request.attachmentsTitle') }}</h3>
      </div>

      <div class="space-y-3">
        <div
          v-for="id in SCHOLARSHIP_ATTACHMENT_FIELDS"
          :key="id"
          class="flex flex-col md:flex-row md:items-center justify-between p-4 border rounded-xl transition-all gap-4"
          :class="isInvalid('attach_' + id)
            ? 'bg-red-50/50 border-red-300'
            : 'bg-gray-50/50 hover:bg-gray-50/80 border-gray-100/70'"
        >
          <div class="flex-1 min-w-0 text-sm font-semibold text-gray-700">
            {{ t(`scholarship.attachments.${id}`) }}
            <span class="text-red-500">*</span>
          </div>

          <div class="flex items-center gap-3 self-end md:self-auto shrink-0 flex-wrap rtl:flex-row-reverse">
            <button
              v-if="!modelValue.files[id]"
              type="button"
              @click="triggerFileInput(id)"
              class="flex items-center gap-1.5 px-4 py-2 border border-sky-200 text-sky-600 rounded-xl bg-white hover:bg-sky-50 transition-colors text-xs font-bold shadow-sm"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4 shrink-0">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z" />
              </svg>
              <span>{{ t('registration.attachments.upload') }}</span>
            </button>

            <template v-else>
              <button
                type="button"
                @click="triggerFileInput(id)"
                class="flex items-center gap-1.5 px-4 py-2 border border-sky-100 text-sky-600 rounded-xl bg-sky-50/40 hover:bg-sky-50 transition-colors text-xs font-semibold"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4 shrink-0">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
                </svg>
                <span>{{ t('registration.attachments.reupload') }}</span>
              </button>

              <button
                type="button"
                @click="setFile(id, null)"
                class="flex items-center gap-1.5 px-3 py-2 border border-red-100 text-red-500 rounded-xl bg-red-50/30 hover:bg-red-50 transition-colors text-xs font-semibold"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4 shrink-0">
                  <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                </svg>
                <span>{{ t('registration.attachments.delete') }}</span>
              </button>

              <span class="text-xs text-gray-500 font-mono truncate max-w-[140px] md:max-w-[180px] inline-block align-middle" dir="ltr">
                {{ fileLabel(id) }}
              </span>
            </template>

            <input
              :id="`scholarship-input-${id}`"
              type="file"
              accept=".jpg,.jpeg,.png,.pdf"
              class="hidden"
              @change="handleFileSelected($event, id)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Declarations -->
    <div class="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-sm space-y-4">
      <label
        v-for="field in SCHOLARSHIP_DECLARATION_FIELDS"
        :key="field"
        class="flex items-start gap-3 cursor-pointer select-none rounded-xl p-2 -mx-2 transition-colors"
        :class="isInvalid('claim_' + field) ? 'bg-red-50 ring-1 ring-red-300' : ''"
      >
        <input
          type="checkbox"
          :checked="modelValue.declarations[field]"
          @change="update({ declarations: { ...modelValue.declarations, [field]: $event.target.checked } })"
          class="custom-checkbox mt-0.5 shrink-0"
        />
        <span class="text-xs font-semibold text-gray-700 leading-relaxed">
          {{ t(`scholarship.declarations.${field}`) }}
        </span>
      </label>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useLanguage } from '@/composables/useLanguage'
import { isFileTooLarge } from '@/utils/fileValidation'
import { SCHOLARSHIP_ATTACHMENT_FIELDS, SCHOLARSHIP_DECLARATION_FIELDS } from './registrationVariant'

const { t, isRTL } = useLanguage()
const props = defineProps({
  modelValue: { type: Object, required: true },
  invalidFields: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue'])

const ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png']
const amountLetterWarning = ref(false)

function isInvalid(field) {
  return props.invalidFields.includes(field)
}

function update(changes) {
  emit('update:modelValue', { ...props.modelValue, ...changes })
}

function setFile(id, file) {
  update({ files: { ...props.modelValue.files, [id]: file } })
}

function onAmountInput(event) {
  const raw = event.target.value
  const value = raw.replace(/[^\d.]/g, '')
  event.target.value = value
  amountLetterWarning.value = raw !== value
  update({ requested_amount: value })
}

function fileLabel(id) {
  const value = props.modelValue.files[id]
  if (value instanceof File) return value.name
  if (typeof value === 'string') return value.split('/').pop()
  return ''
}

function triggerFileInput(id) {
  document.getElementById(`scholarship-input-${id}`)?.click()
}

function handleFileSelected(event, id) {
  const file = event.target.files[0]
  event.target.value = ''
  if (!file) return

  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!ext || !ALLOWED_EXTENSIONS.includes(ext)) {
    alert(t('registration.attachments.invalidFileType'))
    return
  }
  if (isFileTooLarge(file)) {
    alert(t('registration.attachments.fileTooLarge'))
    return
  }
  setFile(id, file)
}
</script>

<style scoped>
.input-label {
  @apply text-xs font-semibold text-gray-700 block leading-relaxed;
}

.custom-input {
  @apply w-full px-4 py-3 bg-gray-50/60 border border-gray-100/70 rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all placeholder:text-gray-300;
}

.custom-textarea {
  @apply w-full px-4 py-3 bg-gray-50/60 border border-gray-100/70 rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all resize-none min-h-[120px] placeholder:text-gray-300;
}

.custom-checkbox {
  @apply w-4 h-4 rounded border-gray-300 text-[#34B0EE] focus:ring-[#34B0EE] transition-all;
}
</style>
