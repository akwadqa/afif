<template>
  <div class="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-sm" :dir="isRTL ? 'rtl' : 'ltr'">
    <div class="flex items-center space-x-2 space-x-reverse border-b border-gray-50 pb-4 mb-6 text-[#0570B6]">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 shrink-0">
        <path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" />
      </svg>
      <h3 class="text-base font-bold">{{ t('registration.familyDetails.title') }}</h3>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.familySize') }} <span class="text-red-500">*</span></label>
        <input
          type="number"
          min="1"
          :value="modelValue.family_size"
          @input="update('family_size', $event.target.value)"
          :placeholder="t('registration.familyDetails.familySizePlaceholder')"
          dir="ltr"
          class="w-full px-4 py-3 bg-gray-50/60 border border-gray-100 rounded-xl outline-none text-sm"
        />
      </div>

      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.familyVisa') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.family_visa_type"
          @change="update('family_visa_type', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border border-gray-100 rounded-xl outline-none text-sm text-gray-600 appearance-none"
        >
          <option value="">{{ t('registration.familyDetails.visaTypePlaceholder') }}</option>
          <option value="Residence">{{ t('registration.familyDetails.residence') }}</option>
          <option value="Visit">{{ t('registration.familyDetails.visit') }}</option>
        </select>
      </div>

      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.dependentCount') }} <span class="text-red-500">*</span></label>
        <input
          type="number"
          min="0"
          :value="modelValue.ben_dependent_count"
          @input="update('ben_dependent_count', $event.target.value)"
          placeholder="0"
          dir="ltr"
          class="w-full px-4 py-3 bg-gray-50/60 border border-gray-100 rounded-xl outline-none text-sm"
        />
      </div>

      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.haveChildren') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.have_children"
          @change="update('have_children', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border border-gray-100 rounded-xl outline-none text-sm text-gray-600 appearance-none"
        >
          <option value="">{{ t('registration.familyDetails.yesNo') }}</option>
          <option value="Yes">{{ t('registration.familyDetails.yes') }}</option>
          <option value="No">{{ t('registration.familyDetails.no') }}</option>
        </select>
      </div>

      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.otherDependents') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.visa_dependent"
          @change="update('visa_dependent', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border border-gray-100 rounded-xl outline-none text-sm text-gray-600 appearance-none"
        >
          <option value="">{{ t('registration.familyDetails.yesNo') }}</option>
          <option value="Yes">{{ t('registration.familyDetails.yes') }}</option>
          <option value="No">{{ t('registration.familyDetails.no') }}</option>
        </select>
      </div>

      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.afifAssistance') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.afif_charity_assistance"
          @change="update('afif_charity_assistance', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border border-gray-100 rounded-xl outline-none text-sm text-gray-600 appearance-none"
        >
          <option value="">{{ t('registration.familyDetails.yesNo') }}</option>
          <option value="Yes">{{ t('registration.familyDetails.yes') }}</option>
          <option value="No">{{ t('registration.familyDetails.no') }}</option>
        </select>
      </div>

    </div>
  </div>
</template>

<script setup>
import { useLanguage } from '@/composables/useLanguage'

const { t, isRTL } = useLanguage()
const props = defineProps({ modelValue: { type: Object, required: true } })
const emit = defineEmits(['update:modelValue'])

function update(field, value) {
  emit('update:modelValue', { ...props.modelValue, [field]: value })
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
