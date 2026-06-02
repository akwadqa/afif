<template>
  <div class="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-sm" :dir="isRTL ? 'rtl' : 'ltr'">
    <div class="flex items-center space-x-2 space-x-reverse border-b border-gray-50 pb-4 mb-6 text-[#0570B6]">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 shrink-0">
        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h18v3H3V3Z" />
      </svg>
      <h3 class="text-base font-bold">{{ t('registration.additionalInfo.title') }}</h3>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.requestorRelation') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.ben_requestor_relationtype"
          @change="update('ben_requestor_relationtype', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border border-gray-100 rounded-xl outline-none text-sm text-gray-600 appearance-none"
        >
          <option value="">{{ t('registration.additionalInfo.requestorRelationPlaceholder') }}</option>
          <option value="The same subvention requestor">{{ t('registration.additionalInfo.sameRequestor') }}</option>
          <option value="Relative to the subvention requestor">{{ t('registration.additionalInfo.relativeRequestor') }}</option>
        </select>
      </div>

      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.secIdType') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.ben_sec_idtype"
          @change="update('ben_sec_idtype', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border border-gray-100 rounded-xl outline-none text-sm text-gray-600 appearance-none"
        >
          <option value="">{{ t('registration.additionalInfo.secIdTypePlaceholder') }}</option>
          <option value="Qatari Id">{{ t('registration.personalInfo.qatariId') }}</option>
          <option value="Passport">{{ t('registration.personalInfo.passport') }}</option>
          <option value="GCC Id">{{ t('registration.personalInfo.gccId') }}</option>
          <option value="Visa Number">{{ t('registration.personalInfo.visaNumber') }}</option>
          <option value="None">{{ t('registration.additionalInfo.noId') }}</option>
        </select>
      </div>

      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.secIdNumber') }}</label>
        <input
          type="text"
          :value="modelValue.ben_sec_idnumber"
          @input="update('ben_sec_idnumber', $event.target.value)"
          placeholder="00000000000"
          dir="ltr"
          class="w-full px-4 py-3 bg-gray-50/60 border border-gray-100 rounded-xl outline-none text-sm"
        />
      </div>

      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.currentlyWorking') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.currently_working"
          @change="update('currently_working', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border border-gray-100 rounded-xl outline-none text-sm text-gray-600 appearance-none"
        >
          <option value="">{{ t('registration.additionalInfo.yesNo') }}</option>
          <option value="Yes">{{ t('registration.additionalInfo.yes') }}</option>
          <option value="No">{{ t('registration.additionalInfo.no') }}</option>
        </select>
      </div>

      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.educationLevel') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.education_level"
          @change="update('education_level', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border border-gray-100 rounded-xl outline-none text-sm text-gray-600 appearance-none"
        >
          <option value="">{{ t('registration.additionalInfo.educationLevelPlaceholder') }}</option>
          <option value="Ignorant">{{ t('registration.additionalInfo.ignorant') }}</option>
          <option value="Primary School Graduate">{{ t('registration.additionalInfo.primary') }}</option>
          <option value="Industrial School">{{ t('registration.additionalInfo.industrial') }}</option>
          <option value="Secondary School Graduate">{{ t('registration.additionalInfo.secondary') }}</option>
          <option value="High Education Level">{{ t('registration.additionalInfo.high') }}</option>
          <option value="Above High Education Level">{{ t('registration.additionalInfo.aboveHigh') }}</option>
        </select>
      </div>

      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.sponsorName') }} <span class="text-red-500">*</span></label>
        <input
          type="text"
          :value="modelValue.sponsor_name"
          @input="update('sponsor_name', $event.target.value)"
          :placeholder="t('registration.additionalInfo.sponsorNamePlaceholder')"
          class="w-full px-4 py-3 bg-gray-50/60 border border-gray-100 rounded-xl outline-none text-sm"
        />
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
