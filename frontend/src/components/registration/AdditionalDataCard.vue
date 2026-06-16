<template>
  <div class="space-y-4" :dir="isRTL ? 'rtl' : 'ltr'">

    <!-- Housing Details card -->
    <div class="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-sm">
      <div class="flex items-center gap-2 border-b border-gray-50 pb-4 mb-6 text-[#0570B6]">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 shrink-0">
          <path stroke-linecap="round" stroke-linejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
        </svg>
        <h3 class="text-base font-bold">{{ t('registration.additionalData.housingTitle') }}</h3>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

        <div class="space-y-1.5">
          <label class="text-xs font-semibold text-gray-700 block">
            {{ t('registration.additionalData.housingType') }} <span class="text-red-500">*</span>
          </label>
          <select
            :value="modelValue.housing_type"
            @change="update('housing_type', $event.target.value)"
            class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
            :class="isInvalid('housing_type') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          >
            <option value="">{{ t('registration.additionalData.housingTypePlaceholder') }}</option>
            <option value="Private Ownership">{{ t('registration.additionalData.owned') }}</option>
            <option value="Rental">{{ t('registration.additionalData.rented') }}</option>
            <option value="Government">{{ t('registration.additionalData.government') }}</option>
            <option value="Endowment">{{ t('registration.additionalData.endowment') }}</option>
          </select>
        </div>

        <div class="space-y-1.5">
          <label class="text-xs font-semibold text-gray-700 block">
            {{ t('registration.additionalData.city') }} <span class="text-red-500">*</span>
          </label>
          <select
            :value="modelValue.housing_city"
            @change="update('housing_city', $event.target.value)"
            class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
            :class="isInvalid('housing_city') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          >
            <option value="">{{ t('registration.additionalData.cityPlaceholder') }}</option>
            <option value="Doha">الدوحة</option>
            <option value="Al Rayan">الريان</option>
            <option value="Al Wakra">الوكرة</option>
            <option value="AL Khoar">الخور</option>
            <option value="Ash Shamal">الشمال</option>
            <option value="Al Daayen">الضعاين</option>
            <option value="Umm Salal">أم صلال</option>
            <option value="AL Shehanyia">الشحانية</option>
          </select>
        </div>

        <div class="space-y-1.5">
          <label class="text-xs font-semibold text-gray-700 block">
            {{ t('registration.additionalData.zoneNumber') }} <span class="text-red-500">*</span>
          </label>
          <input
            type="text"
            :value="modelValue.zone_number"
            @input="update('zone_number', $event.target.value)"
            :placeholder="t('registration.additionalData.numberPlaceholder')"
            dir="ltr"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm transition-all"
            :class="isInvalid('zone_number') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
        </div>

        <div class="space-y-1.5">
          <label class="text-xs font-semibold text-gray-700 block">
            {{ t('registration.additionalData.streetNumber') }} <span class="text-red-500">*</span>
          </label>
          <input
            type="text"
            :value="modelValue.street_number"
            @input="update('street_number', $event.target.value)"
            :placeholder="t('registration.additionalData.numberPlaceholder')"
            dir="ltr"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm transition-all"
            :class="isInvalid('street_number') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
        </div>

        <div class="space-y-1.5">
          <label class="text-xs font-semibold text-gray-700 block">
            {{ t('registration.additionalData.unitNumber') }} <span class="text-red-500">*</span>
          </label>
          <input
            type="text"
            :value="modelValue.unit_number"
            @input="update('unit_number', $event.target.value)"
            :placeholder="t('registration.additionalData.numberPlaceholder')"
            dir="ltr"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm transition-all"
            :class="isInvalid('unit_number') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
        </div>

        <div class="space-y-1.5">
          <label class="text-xs font-semibold text-gray-700 block">
            {{ t('registration.additionalData.buildingNumber') }} <span class="text-red-500">*</span>
          </label>
          <input
            type="text"
            :value="modelValue.building_number"
            @input="update('building_number', $event.target.value)"
            :placeholder="t('registration.additionalData.numberPlaceholder')"
            dir="ltr"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm transition-all"
            :class="isInvalid('building_number') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
        </div>

        <div class="space-y-1.5 md:col-span-2">
          <label class="text-xs font-semibold text-gray-700 block">
            {{ t('registration.additionalData.housingDescription') }} <span class="text-red-500">*</span>
          </label>
          <textarea
            :value="modelValue.housing_description"
            @input="update('housing_description', $event.target.value)"
            rows="3"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-2xl outline-none text-sm resize-none min-h-[90px] focus:ring-2 focus:ring-[#34B0EE] focus:bg-white transition-all"
            :class="isInvalid('housing_description') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
        </div>

      </div>
    </div>

    <!-- Other card -->
    <div class="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-sm">
      <div class="flex items-center gap-2 border-b border-gray-50 pb-4 mb-6 text-[#0570B6]">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 shrink-0">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
        </svg>
        <h3 class="text-base font-bold">{{ t('registration.additionalData.otherTitle') }}</h3>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

        <div class="space-y-1.5">
          <label class="text-xs font-semibold text-gray-700 block leading-relaxed">
            {{ t('registration.additionalData.afifRelation') }} <span class="text-red-500">*</span>
          </label>
          <select
            :value="modelValue.has_afif_employee_relation"
            @change="update('has_afif_employee_relation', $event.target.value)"
            class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
            :class="isInvalid('has_afif_employee_relation') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          >
            <option value="">{{ t('registration.additionalData.yesNo') }}</option>
            <option value="Yes">{{ t('registration.additionalData.yes') }}</option>
            <option value="No">{{ t('registration.additionalData.no') }}</option>
          </select>
        </div>

        <div class="space-y-1.5">
          <label class="text-xs font-semibold text-gray-700 block leading-relaxed">
            {{ t('registration.additionalData.housemates') }} <span class="text-red-500">*</span>
          </label>
          <select
            :value="modelValue.has_housemates"
            @change="update('has_housemates', $event.target.value)"
            class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
            :class="isInvalid('has_housemates') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          >
            <option value="">{{ t('registration.additionalData.yesNo') }}</option>
            <option value="Yes">{{ t('registration.additionalData.yes') }}</option>
            <option value="No">{{ t('registration.additionalData.no') }}</option>
          </select>
        </div>

        <div class="space-y-1.5">
          <label class="text-xs font-semibold text-gray-700 block leading-relaxed">
            {{ t('registration.additionalData.bankLoans') }} <span class="text-red-500">*</span>
          </label>
          <select
            :value="modelValue.has_bank_loans"
            @change="update('has_bank_loans', $event.target.value)"
            class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
            :class="isInvalid('has_bank_loans') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          >
            <option value="">{{ t('registration.additionalData.yesNo') }}</option>
            <option value="Yes">{{ t('registration.additionalData.yes') }}</option>
            <option value="No">{{ t('registration.additionalData.no') }}</option>
          </select>
        </div>

        <!-- Court Tried — shown when bank_loans = Yes -->
        <div v-if="modelValue.has_bank_loans === 'Yes'" class="space-y-1.5">
          <label class="text-xs font-semibold text-gray-700 block leading-relaxed">
            {{ t('registration.additionalData.courtTried') }} <span class="text-red-500">*</span>
          </label>
          <select
            :value="modelValue.court_tried"
            @change="update('court_tried', $event.target.value)"
            class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
            :class="isInvalid('court_tried') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          >
            <option value="">{{ t('registration.additionalData.yesNo') }}</option>
            <option value="Yes">{{ t('registration.additionalData.yes') }}</option>
            <option value="No">{{ t('registration.additionalData.no') }}</option>
          </select>
        </div>

        <div class="space-y-1.5">
          <label class="text-xs font-semibold text-gray-700 block leading-relaxed">
            {{ t('registration.additionalData.otherInfo') }} <span class="text-red-500">*</span>
          </label>
          <select
            :value="modelValue.has_other_info"
            @change="update('has_other_info', $event.target.value)"
            class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
            :class="isInvalid('has_other_info') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          >
            <option value="">{{ t('registration.additionalData.yesNo') }}</option>
            <option value="Yes">{{ t('registration.additionalData.yes') }}</option>
            <option value="No">{{ t('registration.additionalData.no') }}</option>
          </select>
        </div>

        <!-- Additional notes — shown when has_other_info = Yes -->
        <div v-if="modelValue.has_other_info === 'Yes'" class="space-y-1.5 md:col-span-2">
          <label class="text-xs font-semibold text-gray-700 block">
            {{ t('registration.additionalData.additionalNotes') }} <span class="text-red-500">*</span>
          </label>
          <textarea
            :value="modelValue.additional_notes"
            @input="update('additional_notes', $event.target.value)"
            rows="3"
            :placeholder="t('registration.additionalData.additionalNotesPlaceholder')"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-2xl outline-none text-sm resize-none min-h-[90px] focus:ring-2 focus:ring-[#34B0EE] focus:bg-white transition-all"
            :class="isInvalid('additional_notes') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
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
</script>

<style scoped>
.select-field {
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23a0aec0%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
  background-repeat: no-repeat;
  background-size: 12px 12px;
  background-position: left 16px center;
}
</style>
