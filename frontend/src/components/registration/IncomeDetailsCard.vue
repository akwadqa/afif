<template>
  <div class="space-y-4" :dir="isRTL ? 'rtl' : 'ltr'">

    <!-- Checkbox selection card -->
    <div class="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-sm">
      <div class="space-y-3">
        <label
          v-for="src in incomeSources"
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

    <!-- Detail fields — single card for all active sources -->
    <Transition name="slide-fade">
      <div
        v-if="activeIncomeSources.length"
        class="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-sm space-y-8"
      >
        <div
          v-for="(src, index) in activeIncomeSources"
          :key="src.field"
          :class="index > 0 ? 'pt-8 border-t border-gray-100' : ''"
        >
          <h4 class="text-sm font-bold text-[#0570B6] mb-5">{{ src.sectionTitle }}</h4>

          <div class="space-y-4">
            <div class="space-y-1.5">
              <label class="text-xs font-semibold text-gray-700 block">
                {{ src.periodicLabel }} <span class="text-red-500">*</span>
              </label>
              <select
                :value="modelValue[src.periodicField]"
                @change="update(src.periodicField, $event.target.value)"
                class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
                :class="isInvalid(src.periodicField) ? 'border-red-400 bg-red-50' : 'border-gray-100'"
              >
                <option value="">{{ t('registration.incomeDetails.selectPeriod') }}</option>
                <option value="Yearly">{{ t('registration.incomeDetails.yearly') }}</option>
                <option value="Monthly">{{ t('registration.incomeDetails.monthly') }}</option>
                <option value="Others">{{ t('registration.incomeDetails.others') }}</option>
              </select>
            </div>

            <div class="space-y-1.5">
              <label class="text-xs font-semibold text-gray-700 block">
                {{ src.amountLabel }} <span class="text-red-500">*</span>
              </label>
              <input
                type="text"
                inputmode="numeric"
                :value="modelValue[src.amountField]"
                @input="onNumberOnly(src.amountField, $event)"
                :placeholder="t('registration.incomeDetails.amountPlaceholder')"
                class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm transition-all"
                :class="isInvalid(src.amountField) ? 'border-red-400 bg-red-50' : 'border-gray-100'"
              />
              <p v-if="letterWarnings.has(src.amountField)" class="text-xs text-red-500">
                {{ t('registration.validation.noLetters') }}
              </p>
            </div>

            <div class="space-y-1.5">
              <label class="text-xs font-semibold text-gray-700 block">
                {{ src.noteLabel }} <span class="text-red-500">*</span>
              </label>
              <input
                type="text"
                maxlength="2000"
                :value="modelValue[src.noteField]"
                @input="update(src.noteField, $event.target.value)"
                :placeholder="t('registration.incomeDetails.notesPlaceholder')"
                class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm transition-all"
                :class="isInvalid(src.noteField) ? 'border-red-400 bg-red-50' : 'border-gray-100'"
              />
              <p
                class="text-xs"
                :class="(modelValue[src.noteField] || '').length >= 2000 ? 'text-red-500' : 'text-gray-400'"
              >
                {{ (modelValue[src.noteField] || '').length }} / 2000 {{ t('registration.validation.maxCharsSuffix') }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useLanguage } from '@/composables/useLanguage'
import { arabicToWestern } from '@/utils/inputHelpers'

const { t, isRTL } = useLanguage()
const props = defineProps({
  modelValue: { type: Object, required: true },
  invalidFields: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue'])

const letterWarnings = ref(new Set())

function update(field, value) {
  emit('update:modelValue', { ...props.modelValue, [field]: value })
}

function onNumberOnly(field, event) {
  const raw = event.target.value
  const val = arabicToWestern(raw).replace(/[^0-9]/g, '')
  event.target.value = val
  update(field, val)
  if (raw !== val) letterWarnings.value.add(field)
  else letterWarnings.value.delete(field)
}

function isInvalid(field) {
  return props.invalidFields.includes(field)
}

const incomeSources = computed(() => [
  {
    field: 'ben_income',
    label: t('registration.incomeDetails.benIncomeLabel'),
    sectionTitle: t('registration.incomeDetails.benIncomeTitle'),
    periodicField: 'ben_periodic_type',            periodicLabel: t('registration.incomeDetails.benPeriodicLabel'),
    amountField:   'salary_amount',                amountLabel:   t('registration.incomeDetails.salaryAmount'),
    noteField:     'benficiary_note',              noteLabel:     t('registration.incomeDetails.benNoteLabel'),
  },
  {
    field: 'family_income',
    label: t('registration.incomeDetails.familyIncomeLabel'),
    sectionTitle: t('registration.incomeDetails.familyIncomeTitle'),
    periodicField: 'family_periodic_type',         periodicLabel: t('registration.incomeDetails.familyPeriodicLabel'),
    amountField:   'family_income_amount',         amountLabel:   t('registration.incomeDetails.familyAmount'),
    noteField:     'family_note',                  noteLabel:     t('registration.incomeDetails.familyNoteLabel'),
  },
  {
    field: 'family_extra',
    label: t('registration.incomeDetails.familyExtraLabel'),
    sectionTitle: t('registration.incomeDetails.familyExtraTitle'),
    periodicField: 'extra_periodic_type',          periodicLabel: t('registration.incomeDetails.extraPeriodicLabel'),
    amountField:   'family_extra_salary',          amountLabel:   t('registration.incomeDetails.extraAmount'),
    noteField:     'family_extra_note',            noteLabel:     t('registration.incomeDetails.extraNoteLabel'),
  },
  {
    field: 'children_income',
    label: t('registration.incomeDetails.childrenIncomeLabel'),
    sectionTitle: t('registration.incomeDetails.childrenIncomeTitle'),
    periodicField: 'children_periodic_type',       periodicLabel: t('registration.incomeDetails.childrenPeriodicLabel'),
    amountField:   'family_children_salary',       amountLabel:   t('registration.incomeDetails.childrenAmount'),
    noteField:     'children_note',                noteLabel:     t('registration.incomeDetails.childrenNoteLabel'),
  },
  {
    field: 'private_income',
    label: t('registration.incomeDetails.privateIncomeLabel'),
    sectionTitle: t('registration.incomeDetails.privateIncomeTitle'),
    periodicField: 'private_business_periodicity', periodicLabel: t('registration.incomeDetails.privatePeriodicLabel'),
    amountField:   'private_business_amount',      amountLabel:   t('registration.incomeDetails.privateAmount'),
    noteField:     'private_note',                 noteLabel:     t('registration.incomeDetails.privateNoteLabel'),
  },
  {
    field: 'stock_income',
    label: t('registration.incomeDetails.stockIncomeLabel'),
    sectionTitle: t('registration.incomeDetails.stockIncomeTitle'),
    periodicField: 'stock_market_periodicity',     periodicLabel: t('registration.incomeDetails.stockPeriodicLabel'),
    amountField:   'stock_market_income',          amountLabel:   t('registration.incomeDetails.stockAmount'),
    noteField:     'stock_market_note',            noteLabel:     t('registration.incomeDetails.stockNoteLabel'),
  },
  {
    field: 'rent_income',
    label: t('registration.incomeDetails.rentIncomeLabel'),
    sectionTitle: t('registration.incomeDetails.rentIncomeTitle'),
    periodicField: 'rent_periodic_type',           periodicLabel: t('registration.incomeDetails.rentPeriodicLabel'),
    amountField:   'rent_income_amount',           amountLabel:   t('registration.incomeDetails.rentAmount'),
    noteField:     'rent_note',                    noteLabel:     t('registration.incomeDetails.rentNoteLabel'),
  },
])

const activeIncomeSources = computed(() =>
  incomeSources.value.filter(src => props.modelValue[src.field] == 1)
)
</script>

<style scoped>
.select-field {
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23a0aec0%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
  background-repeat: no-repeat;
  background-size: 12px 12px;
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
