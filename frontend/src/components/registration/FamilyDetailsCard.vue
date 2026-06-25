<template>
  <div class="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-sm" :dir="isRTL ? 'rtl' : 'ltr'">
    <div class="flex items-center space-x-2 space-x-reverse border-b border-gray-50 pb-4 mb-6 text-[#0570B6]">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 shrink-0">
        <path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" />
      </svg>
      <h3 class="text-base font-bold">{{ t('registration.familyDetails.title') }}</h3>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

      <!-- Family Size -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.familySize') }} <span class="text-red-500">*</span></label>
        <input
          type="text"
          inputmode="numeric"
          :value="modelValue.family_size"
          @input="onNumberOnly('family_size', $event)"
          :placeholder="t('registration.familyDetails.familySizePlaceholder')"
          class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm transition-all"
          :class="isInvalid('family_size') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        />
        <p v-if="letterWarnings.has('family_size')" class="text-xs text-red-500">
          {{ t('registration.validation.noLetters') }}
        </p>
      </div>

      <!-- Beneficiary Dependent Count -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.dependentCount') }} <span class="text-red-500">*</span></label>
        <input
          type="text"
          inputmode="numeric"
          :value="modelValue.ben_dependent_count"
          @input="onNumberOnly('ben_dependent_count', $event)"
          placeholder="0"
          class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm transition-all"
          :class="isInvalid('ben_dependent_count') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        />
        <p v-if="letterWarnings.has('ben_dependent_count')" class="text-xs text-red-500">
          {{ t('registration.validation.noLetters') }}
        </p>
      </div>

      <!-- Family Visa Type -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.familyVisa') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.family_visa_type"
          @change="update('family_visa_type', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
          :class="isInvalid('family_visa_type') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        >
          <option value="">{{ t('registration.familyDetails.visaTypePlaceholder') }}</option>
          <option value="Residence">{{ t('registration.familyDetails.residence') }}</option>
          <option value="Visit">{{ t('registration.familyDetails.visit') }}</option>
        </select>
      </div>

      <!-- Others Under Own Visa — only when visa_type = Residence -->
      <div v-if="personalInfo.visa_type === 'Residence'" class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.otherDependents') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.visa_dependent"
          @change="update('visa_dependent', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
          :class="isInvalid('visa_dependent') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        >
          <option value="">{{ t('registration.familyDetails.yesNo') }}</option>
          <option value="Yes">{{ t('registration.familyDetails.yes') }}</option>
          <option value="No">{{ t('registration.familyDetails.no') }}</option>
        </select>
      </div>

      <!-- Names and Relation to Sponsored — shown when visa_dependent = Yes -->
      <div
        v-if="personalInfo.visa_type === 'Residence' && modelValue.visa_dependent === 'Yes'"
        class="space-y-1.5 md:col-span-2"
      >
        <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.namesRelation') }} <span class="text-red-500">*</span></label>
        <input
          type="text"
          :value="modelValue.names_and_relation_to_sponsored"
          @input="onTextOnly('names_and_relation_to_sponsored', $event)"
          :placeholder="t('registration.familyDetails.namesRelationPlaceholder')"
          class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
          :class="isInvalid('names_and_relation_to_sponsored') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        />
        <p v-if="numberWarnings.has('names_and_relation_to_sponsored')" class="text-xs text-red-500">
          {{ t('registration.validation.noNumbers') }}
        </p>
      </div>

      <!-- Have Children -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.haveChildren') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.have_children"
          @change="update('have_children', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
          :class="isInvalid('have_children') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        >
          <option value="">{{ t('registration.familyDetails.yesNo') }}</option>
          <option value="Yes">{{ t('registration.familyDetails.yes') }}</option>
          <option value="No">{{ t('registration.familyDetails.no') }}</option>
        </select>
      </div>

      <!-- Partner Working — shown when marital_status = Married -->
      <div v-if="personalInfo.marital_status === 'Married'" class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.partnerWorking') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.partner_working"
          @change="update('partner_working', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
          :class="isInvalid('partner_working') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        >
          <option value="">{{ t('registration.familyDetails.yesNo') }}</option>
          <option value="Yes">{{ t('registration.familyDetails.yes') }}</option>
          <option value="No">{{ t('registration.familyDetails.no') }}</option>
        </select>
      </div>

      <!-- Children conditional fields — shown when have_children = Yes -->
      <template v-if="modelValue.have_children === 'Yes'">

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.childrenAbove18') }} <span class="text-red-500">*</span></label>
          <select
            :value="modelValue.children_above_eighteen"
            @change="update('children_above_eighteen', $event.target.value)"
            class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
            :class="isInvalid('children_above_eighteen') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          >
            <option value="">{{ t('registration.familyDetails.yesNo') }}</option>
            <option value="Yes">{{ t('registration.familyDetails.yes') }}</option>
            <option value="No">{{ t('registration.familyDetails.no') }}</option>
          </select>
        </div>

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.childrenInSchool') }} <span class="text-red-500">*</span></label>
          <select
            :value="modelValue.children_in_school"
            @change="update('children_in_school', $event.target.value)"
            class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
            :class="isInvalid('children_in_school') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          >
            <option value="">{{ t('registration.familyDetails.yesNo') }}</option>
            <option value="Yes">{{ t('registration.familyDetails.yes') }}</option>
            <option value="No">{{ t('registration.familyDetails.no') }}</option>
          </select>
        </div>

        <!-- Children in school sub-fields -->
        <template v-if="modelValue.children_in_school === 'Yes'">

          <div class="space-y-1.5">
            <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.childrenSchoolType') }} <span class="text-red-500">*</span></label>
            <select
              :value="modelValue.children_school"
              @change="update('children_school', $event.target.value)"
              class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
              :class="isInvalid('children_school') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
            >
              <option value="">{{ t('registration.familyDetails.yesNo') }}</option>
              <option value="Private">{{ t('registration.familyDetails.privateSchool') }}</option>
              <option value="Public">{{ t('registration.familyDetails.publicSchool') }}</option>
            </select>
          </div>

          <div class="space-y-1.5 md:col-span-2">
            <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.childrenSchoolInfo') }} <span class="text-red-500">*</span></label>
            <input
              type="text"
              :value="modelValue.children_school_information"
              @input="update('children_school_information', $event.target.value)"
              :placeholder="t('registration.familyDetails.childrenSchoolInfoPlaceholder')"
              class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
              :class="isInvalid('children_school_information') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
            />
          </div>

        </template>

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.childrenSpecialNeeds') }} <span class="text-red-500">*</span></label>
          <select
            :value="modelValue.children_special_needs"
            @change="update('children_special_needs', $event.target.value)"
            class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
            :class="isInvalid('children_special_needs') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          >
            <option value="">{{ t('registration.familyDetails.yesNo') }}</option>
            <option value="Yes">{{ t('registration.familyDetails.yes') }}</option>
            <option value="No">{{ t('registration.familyDetails.no') }}</option>
          </select>
        </div>

      </template>

      <!-- Received Afif Charity Assistance -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.afifAssistance') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.afif_charity_assistance"
          @change="update('afif_charity_assistance', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
          :class="isInvalid('afif_charity_assistance') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        >
          <option value="">{{ t('registration.familyDetails.yesNo') }}</option>
          <option value="Yes">{{ t('registration.familyDetails.yes') }}</option>
          <option value="No">{{ t('registration.familyDetails.no') }}</option>
        </select>
      </div>

      <!-- Afif assistance amount — shown when afif_charity_assistance = Yes -->
      <div v-if="modelValue.afif_charity_assistance === 'Yes'" class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.familyDetails.afifAssistanceAmount') }} <span class="text-red-500">*</span></label>
        <input
          type="text"
          :value="modelValue.affif_assistance"
          @input="update('affif_assistance', $event.target.value)"
          :placeholder="t('registration.familyDetails.afifAssistancePlaceholder')"
          class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
          :class="isInvalid('affif_assistance') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        />
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useLanguage } from '@/composables/useLanguage'

import { arabicToWestern } from '@/utils/inputHelpers'

const { t, isRTL } = useLanguage()
const props = defineProps({
  modelValue: { type: Object, required: true },
  personalInfo: { type: Object, default: () => ({}) },
  invalidFields: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue'])

const numberWarnings = ref(new Set())
const letterWarnings = ref(new Set())

function update(field, value) {
  emit('update:modelValue', { ...props.modelValue, [field]: value })
}

function onTextOnly(field, event) {
  const raw = event.target.value
  const val = raw.replace(/[0-9]/g, '')
  event.target.value = val
  update(field, val)
  if (raw !== val) numberWarnings.value.add(field)
  else numberWarnings.value.delete(field)
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
</script>

<style scoped>
.select-field {
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23a0aec0%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
  background-repeat: no-repeat;
  background-size: 12px 12px;
}
</style>
