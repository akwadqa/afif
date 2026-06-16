<template>
  <div class="space-y-4" :dir="isRTL ? 'rtl' : 'ltr'">

    <!-- Checkbox selection card -->
    <div class="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-sm">
      <div class="flex items-center gap-2 border-b border-gray-50 pb-4 mb-6 text-[#0570B6]">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 shrink-0">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25ZM6.75 12h.008v.008H6.75V12Zm0 3h.008v.008H6.75V15Zm0 3h.008v.008H6.75V18Z" />
        </svg>
        <h3 class="text-base font-bold">{{ t('registration.financialObligations.title') }}</h3>
      </div>

      <div class="space-y-3">
        <label
          v-for="src in obligationSources"
          :key="src.field"
          :class="[
            'flex items-center gap-3 px-5 py-4 rounded-xl border transition-all cursor-pointer select-none',
            modelValue[src.field] == 1
              ? 'bg-sky-50/50 border-sky-100 shadow-sm'
              : 'bg-gray-50/50 border-gray-100/70 hover:bg-gray-50'
          ]"
        >
          <input
            type="checkbox"
            :checked="modelValue[src.field] == 1"
            @change="update(src.field, $event.target.checked ? 1 : 0)"
            class="w-5 h-5 rounded border-gray-300 text-[#34B0EE] focus:ring-[#34B0EE] cursor-pointer shrink-0"
          />
          <span class="text-sm font-medium text-gray-700">{{ src.label }}</span>
        </label>
      </div>
    </div>

    <!-- Detail fields — single card for all active obligations -->
    <Transition name="slide-fade">
      <div
        v-if="activeObligationSources.length"
        class="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-sm space-y-8"
      >
        <div
          v-for="(src, index) in activeObligationSources"
          :key="src.field"
          :class="index > 0 ? 'pt-8 border-t border-gray-100' : ''"
        >
          <h4 class="text-sm font-bold text-[#0570B6] mb-5">{{ src.sectionTitle }}</h4>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="fieldDef in src.fields"
              :key="fieldDef.name"
              class="space-y-1.5"
            >
              <label class="text-xs font-semibold text-gray-700 block">
                {{ fieldDef.label }} <span class="text-red-500">*</span>
              </label>

              <select
                v-if="fieldDef.type === 'select'"
                :value="modelValue[fieldDef.name]"
                @change="update(fieldDef.name, $event.target.value)"
                class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
                :class="isInvalid(fieldDef.name) ? 'border-red-400 bg-red-50' : 'border-gray-100'"
              >
                <option value="">{{ t('registration.financialObligations.selectPeriod') }}</option>
                <option value="Monthly">{{ t('registration.financialObligations.monthly') }}</option>
                <option value="One Time">{{ t('registration.financialObligations.oneTime') }}</option>
              </select>

              <input
                v-else
                type="text"
                :value="modelValue[fieldDef.name]"
                @input="update(fieldDef.name, $event.target.value)"
                :placeholder="fieldDef.placeholder"
                :dir="fieldDef.dir || (isRTL ? 'rtl' : 'ltr')"
                class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm transition-all"
                :class="isInvalid(fieldDef.name) ? 'border-red-400 bg-red-50' : 'border-gray-100'"
              />
            </div>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useLanguage } from '@/composables/useLanguage'

const { t, isRTL } = useLanguage()
const props = defineProps({
  modelValue: { type: Object, required: true },
  invalidFields: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue'])

function update(field, value) {
  emit('update:modelValue', { ...props.modelValue, [field]: value })
}

function isInvalid(field) {
  return props.invalidFields.includes(field)
}

const obligationSources = computed(() => [
  {
    field: 'family_obligation',
    label: t('registration.financialObligations.familyLabel'),
    sectionTitle: t('registration.financialObligations.familyTitle'),
    fields: [
      { name: 'family_obligations_installments_count', type: 'text',   label: t('registration.financialObligations.familyInstallmentsLabel'), placeholder: t('registration.financialObligations.installmentsPlaceholder'), dir: 'ltr' },
      { name: 'family_obligation_periodicity',         type: 'select', label: t('registration.financialObligations.familyPeriodicLabel') },
      { name: 'family_expenses',                       type: 'text',   label: t('registration.financialObligations.familyAmountLabel'), placeholder: t('registration.financialObligations.amountPlaceholder'), dir: 'ltr' },
      { name: 'family_obligations_note',               type: 'text',   label: t('registration.financialObligations.familyNoteLabel'), placeholder: t('registration.financialObligations.notesPlaceholder') },
    ],
  },
  {
    field: 'rent_obligation',
    label: t('registration.financialObligations.rentLabel'),
    sectionTitle: t('registration.financialObligations.rentTitle'),
    fields: [
      { name: 'rent_obligation_periodicity',          type: 'select', label: t('registration.financialObligations.rentPeriodicLabel') },
      { name: 'rent_obligations_installments_count',  type: 'text',   label: t('registration.financialObligations.rentInstallmentsLabel'), placeholder: t('registration.financialObligations.installmentsPlaceholder'), dir: 'ltr' },
      { name: 'rent_amount',                          type: 'text',   label: t('registration.financialObligations.rentAmountLabel'), placeholder: t('registration.financialObligations.amountPlaceholder'), dir: 'ltr' },
      { name: 'rent_obligations_note',                type: 'text',   label: t('registration.financialObligations.rentNoteLabel'), placeholder: t('registration.financialObligations.notesPlaceholder') },
    ],
  },
  {
    field: 'treatment_obligation',
    label: t('registration.financialObligations.treatmentLabel'),
    sectionTitle: t('registration.financialObligations.treatmentTitle'),
    fields: [
      { name: 'treatment_obligation_periodicity',          type: 'select', label: t('registration.financialObligations.treatmentPeriodicLabel') },
      { name: 'treatment_obligation_installments_count',   type: 'text',   label: t('registration.financialObligations.treatmentInstallmentsLabel'), placeholder: t('registration.financialObligations.installmentsPlaceholder'), dir: 'ltr' },
      { name: 'treatment_amount',                          type: 'text',   label: t('registration.financialObligations.treatmentAmountLabel'), placeholder: t('registration.financialObligations.amountPlaceholder'), dir: 'ltr' },
      { name: 'treatment_obligations_note',                type: 'text',   label: t('registration.financialObligations.treatmentNoteLabel'), placeholder: t('registration.financialObligations.notesPlaceholder') },
    ],
  },
  {
    field: 'debt_obligation',
    label: t('registration.financialObligations.debtLabel'),
    sectionTitle: t('registration.financialObligations.debtTitle'),
    fields: [
      { name: 'debt_obligation_periodicity',          type: 'select', label: t('registration.financialObligations.debtPeriodicLabel') },
      { name: 'debt_obligations_installments_count',  type: 'text',   label: t('registration.financialObligations.debtInstallmentsLabel'), placeholder: t('registration.financialObligations.installmentsPlaceholder'), dir: 'ltr' },
      { name: 'bank_payments_amount',                 type: 'text',   label: t('registration.financialObligations.debtAmountLabel'), placeholder: t('registration.financialObligations.amountPlaceholder'), dir: 'ltr' },
      { name: 'debt_obligations_note',                type: 'text',   label: t('registration.financialObligations.debtNoteLabel'), placeholder: t('registration.financialObligations.notesPlaceholder') },
    ],
  },
  {
    field: 'tuition_obligation',
    label: t('registration.financialObligations.tuitionLabel'),
    sectionTitle: t('registration.financialObligations.tuitionTitle'),
    fields: [
      { name: 'tuition_obligation_periodicity',          type: 'select', label: t('registration.financialObligations.tuitionPeriodicLabel') },
      { name: 'tuition_obligation_installments_count',   type: 'text',   label: t('registration.financialObligations.tuitionInstallmentsLabel'), placeholder: t('registration.financialObligations.installmentsPlaceholder'), dir: 'ltr' },
      { name: 'tuition_obligations_note',                type: 'text',   label: t('registration.financialObligations.tuitionNoteLabel'), placeholder: t('registration.financialObligations.notesPlaceholder') },
      { name: 'tuition_amount',                          type: 'text',   label: t('registration.financialObligations.tuitionAmountLabel'), placeholder: t('registration.financialObligations.amountPlaceholder'), dir: 'ltr' },
    ],
  },
])

const activeObligationSources = computed(() =>
  obligationSources.value.filter(src => props.modelValue[src.field] == 1)
)
</script>

<style scoped>
.select-field {
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23a0aec0%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
  background-repeat: no-repeat;
  background-size: 12px 12px;
  background-position: left 16px center;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-8px);
  opacity: 0;
}
</style>
