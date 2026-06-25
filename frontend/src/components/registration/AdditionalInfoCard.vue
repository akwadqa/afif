<template>
  <div class="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-sm" :dir="isRTL ? 'rtl' : 'ltr'">
    <div class="flex items-center space-x-2 space-x-reverse border-b border-gray-50 pb-4 mb-6 text-[#0570B6]">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 shrink-0">
        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h18v3H3V3Z" />
      </svg>
      <h3 class="text-base font-bold">{{ t('registration.additionalInfo.title') }}</h3>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

      <!-- Relation to Requestor -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.requestorRelation') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.ben_requestor_relationtype || 'The same subvention requestor'"
          disabled
          class="select-field w-full px-4 py-3 bg-gray-100 border rounded-xl outline-none text-sm text-gray-600 appearance-none cursor-not-allowed"
          :class="isInvalid('ben_requestor_relationtype') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        >
          <option value="The same subvention requestor">{{ t('registration.additionalInfo.sameRequestor') }}</option>
        </select>
      </div>

      <!-- Placeholder to keep grid aligned when requestor fields are hidden -->
      <div v-if="modelValue.ben_requestor_relationtype !== 'Relative to the subvention requestor'" />

      <!-- Requestor fields — shown when "Relative to the subvention requestor" -->
      <template v-if="modelValue.ben_requestor_relationtype === 'Relative to the subvention requestor'">

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.requestorName') }} <span class="text-red-500">*</span></label>
          <input
            type="text"
            :value="modelValue.requestor_name"
            @input="onTextOnly('requestor_name', $event)"
            :placeholder="t('registration.additionalInfo.requestorNamePlaceholder')"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
            :class="isInvalid('requestor_name') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
          <p v-if="numberWarnings.has('requestor_name')" class="text-xs text-red-500">
            {{ t('registration.validation.noNumbers') }}
          </p>
        </div>

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.requestorIdType') }} <span class="text-red-500">*</span></label>
          <select
            :value="modelValue.requestor_idtype"
            @change="update('requestor_idtype', $event.target.value)"
            class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
            :class="isInvalid('requestor_idtype') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          >
            <option value="">{{ t('registration.personalInfo.primaryIdTypePlaceholder') }}</option>
            <option value="Qatari Id">{{ t('registration.personalInfo.qatariId') }}</option>
            <option value="Passport">{{ t('registration.personalInfo.passport') }}</option>
            <option value="GCC Id">{{ t('registration.personalInfo.gccId') }}</option>
            <option value="Visa Number">{{ t('registration.personalInfo.visaNumber') }}</option>
          </select>
        </div>

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.requestorIdNumber') }} <span class="text-red-500">*</span></label>
          <input
            type="text"
            :value="modelValue.requestor_idnumber"
            @input="onDigitsOnly('requestor_idnumber', $event, 11)"
            maxlength="11"
            placeholder="00000000000"
            dir="ltr"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
            :class="isInvalid('requestor_idnumber') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
          <p v-if="modelValue.requestor_idnumber && modelValue.requestor_idnumber.length !== 11" class="text-xs text-red-500">
            {{ t('registration.validation.idMustBe11') }}
          </p>
        </div>

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.requestorNationality') }} <span class="text-red-500">*</span></label>
          <input
            type="text"
            list="requestor-country-list"
            :value="modelValue.requestor_nationality"
            @input="onTextOnly('requestor_nationality', $event)"
            :placeholder="t('registration.additionalInfo.requestorNationalityPlaceholder')"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
            :class="isInvalid('requestor_nationality') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
          <datalist id="requestor-country-list">
            <option v-for="country in countries" :key="country" :value="country" />
          </datalist>
          <p v-if="numberWarnings.has('requestor_nationality')" class="text-xs text-red-500">
            {{ t('registration.validation.noNumbers') }}
          </p>
        </div>

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.requestorPhone') }} <span class="text-red-500">*</span></label>
          <input
            type="tel"
            :value="modelValue.requestor_number"
            @input="onDigitsOnly('requestor_number', $event, 8)"
            maxlength="8"
            placeholder="00000000"
            dir="ltr"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
            :class="isInvalid('requestor_number') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
          <p v-if="modelValue.requestor_number && modelValue.requestor_number.length !== 8" class="text-xs text-red-500">
            {{ t('registration.validation.phoneMustBe8') }}
          </p>
        </div>

      </template>

      <!-- Secondary ID Type -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.secIdType') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.ben_sec_idtype || 'Passport'"
          disabled
          class="select-field w-full px-4 py-3 bg-gray-100 border rounded-xl outline-none text-sm text-gray-600 appearance-none cursor-not-allowed"
          :class="isInvalid('ben_sec_idtype') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        >
          <option value="Passport">{{ t('registration.personalInfo.passport') }}</option>
        </select>
      </div>

      <!-- Secondary Nationality — shown when secondary ID is Passport -->
      <div v-if="modelValue.ben_sec_idtype === 'Passport'" class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.secNationality') }} <span class="text-red-500">*</span></label>
        <input
          type="text"
          list="sec-country-list"
          :value="modelValue.ben_sec_nationality"
          @input="onTextOnly('ben_sec_nationality', $event)"
          :placeholder="t('registration.personalInfo.nationalityPlaceholder')"
          class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
          :class="isInvalid('ben_sec_nationality') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        />
        <datalist id="sec-country-list">
          <option v-for="country in countries" :key="country" :value="country" />
        </datalist>
        <p v-if="numberWarnings.has('ben_sec_nationality')" class="text-xs text-red-500">
          {{ t('registration.validation.noNumbers') }}
        </p>
      </div>

      <!-- Gulf Country — shown when secondary ID is GCC Id -->
      <div v-if="modelValue.ben_sec_idtype === 'GCC Id'" class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.gulfCountry') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.ben_sec_gulf_country"
          @change="update('ben_sec_gulf_country', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
          :class="isInvalid('ben_sec_gulf_country') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        >
          <option value="">{{ t('registration.additionalInfo.gulfCountryPlaceholder') }}</option>
          <option value="Saudi Arabia">Saudi Arabia</option>
          <option value="Oman">Oman</option>
          <option value="Kuwait">Kuwait</option>
          <option value="United Arab Emirates">United Arab Emirates</option>
          <option value="Bahrain">Bahrain</option>
        </select>
      </div>

      <!-- Secondary ID Number -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.secIdNumber') }}</label>
        <input
          type="text"
          :value="modelValue.ben_sec_idnumber"
          @input="onAlphanumericOnly('ben_sec_idnumber', $event, 9)"
          maxlength="9"
          placeholder="A12345678"
          dir="ltr"
          class="w-full px-4 py-3 bg-gray-50/60 border border-gray-100 rounded-xl outline-none text-sm"
        />
      </div>

      <!-- Currently Working -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.currentlyWorking') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.currently_working"
          @change="update('currently_working', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
          :class="isInvalid('currently_working') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        >
          <option value="">{{ t('registration.additionalInfo.yesNo') }}</option>
          <option value="Yes">{{ t('registration.additionalInfo.yes') }}</option>
          <option value="No">{{ t('registration.additionalInfo.no') }}</option>
        </select>
      </div>

      <!-- Employment fields — shown when currently working = Yes -->
      <template v-if="modelValue.currently_working === 'Yes'">

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.employerName') }} <span class="text-red-500">*</span></label>
          <input
            type="text"
            :value="modelValue.employer_name"
            @input="onTextOnly('employer_name', $event)"
            :placeholder="t('registration.additionalInfo.employerNamePlaceholder')"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
            :class="isInvalid('employer_name') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
          <p v-if="numberWarnings.has('employer_name')" class="text-xs text-red-500">
            {{ t('registration.validation.noNumbers') }}
          </p>
        </div>

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.employerAddress') }} <span class="text-red-500">*</span></label>
          <input
            type="text"
            :value="modelValue.employer_address"
            @input="update('employer_address', $event.target.value)"
            :placeholder="t('registration.additionalInfo.employerAddressPlaceholder')"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
            :class="isInvalid('employer_address') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
        </div>

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.occupation') }} <span class="text-red-500">*</span></label>
          <input
            type="text"
            :value="modelValue.occupation"
            @input="onTextOnly('occupation', $event)"
            :placeholder="t('registration.additionalInfo.occupationPlaceholder')"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
            :class="isInvalid('occupation') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
          <p v-if="numberWarnings.has('occupation')" class="text-xs text-red-500">
            {{ t('registration.validation.noNumbers') }}
          </p>
        </div>

      </template>

      <!-- Worked Before — shown when visa=Residence AND currently_working=No -->
      <div
        v-if="personalInfo.visa_type === 'Residence' && modelValue.currently_working === 'No'"
        class="space-y-1.5"
      >
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.workedBefore') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.worked_before"
          @change="update('worked_before', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
          :class="isInvalid('worked_before') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        >
          <option value="">{{ t('registration.additionalInfo.yesNo') }}</option>
          <option value="Yes">{{ t('registration.additionalInfo.yes') }}</option>
          <option value="No">{{ t('registration.additionalInfo.no') }}</option>
        </select>
      </div>

      <!-- Education Level -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.educationLevel') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.education_level"
          @change="update('education_level', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
          :class="isInvalid('education_level') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
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

      <!-- Sponsor Name -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.sponsorName') }} <span class="text-red-500">*</span></label>
        <input
          type="text"
          :value="modelValue.sponsor_name"
          @input="onTextOnly('sponsor_name', $event)"
          :placeholder="t('registration.additionalInfo.sponsorNamePlaceholder')"
          class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm transition-all"
          :class="isInvalid('sponsor_name') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        />
        <p v-if="numberWarnings.has('sponsor_name')" class="text-xs text-red-500">
          {{ t('registration.validation.noNumbers') }}
        </p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useLanguage } from '@/composables/useLanguage'
import { arabicToWestern } from '@/utils/inputHelpers'

const { t, isRTL } = useLanguage()
const props = defineProps({
  modelValue: { type: Object, required: true },
  personalInfo: { type: Object, default: () => ({}) },
  invalidFields: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue'])

const countries = ref([])
const numberWarnings = ref(new Set())

onMounted(async () => {
  try {
    const res = await fetch('/api/resource/Country?fields=["name"]&limit=300&order_by=name%20asc')
    const data = await res.json()
    countries.value = (data.data || []).map(c => c.name)
  } catch {
    // silently fall back to free-text if the fetch fails
  }
})

function update(field, value) {
  emit('update:modelValue', { ...props.modelValue, [field]: value })
}

function onDigitsOnly(field, event, maxLen) {
  const val = arabicToWestern(event.target.value).replace(/\D/g, '').slice(0, maxLen)
  event.target.value = val
  update(field, val)
}

function onAlphanumericOnly(field, event, maxLen) {
  const val = arabicToWestern(event.target.value).toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, maxLen)
  event.target.value = val
  update(field, val)
}

function onTextOnly(field, event) {
  const raw = event.target.value
  const val = raw.replace(/[0-9]/g, '')
  event.target.value = val
  update(field, val)
  if (raw !== val) numberWarnings.value.add(field)
  else numberWarnings.value.delete(field)
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
