<template>
  <div class="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-sm" :dir="isRTL ? 'rtl' : 'ltr'">
    <div class="flex items-center space-x-2 space-x-reverse border-b border-gray-50 pb-4 mb-6 text-[#0570B6]">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 shrink-0">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
      </svg>
      <h3 class="text-base font-bold">{{ t('registration.personalInfo.title') }}</h3>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

      <!-- Arabic Name -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.arName') }} <span class="text-red-500">*</span></label>
        <input
          type="text"
          :value="modelValue.ar_name"
          @input="update('ar_name', $event.target.value)"
          :placeholder="t('registration.personalInfo.arNamePlaceholder')"
          dir="rtl"
          class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
          :class="isInvalid('ar_name') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        />
      </div>

      <!-- English Name -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.enName') }} <span class="text-red-500">*</span></label>
        <input
          type="text"
          :value="modelValue.en_name"
          @input="update('en_name', $event.target.value)"
          :placeholder="t('registration.personalInfo.enNamePlaceholder')"
          dir="ltr"
          class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
          :class="isInvalid('en_name') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        />
      </div>

      <!-- Primary ID Type -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.primaryIdType') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.ben_primary_idtype"
          @change="update('ben_primary_idtype', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] outline-none text-sm text-gray-600 appearance-none"
          :class="isInvalid('ben_primary_idtype') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        >
          <option value="">{{ t('registration.personalInfo.primaryIdTypePlaceholder') }}</option>
          <option value="Qatari Id">{{ t('registration.personalInfo.qatariId') }}</option>
          <option value="Passport">{{ t('registration.personalInfo.passport') }}</option>
          <option value="GCC Id">{{ t('registration.personalInfo.gccId') }}</option>
          <option value="Visa Number">{{ t('registration.personalInfo.visaNumber') }}</option>
        </select>
      </div>

      <!-- Primary ID Number -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.primaryIdNumber') }} <span class="text-red-500">*</span></label>
        <input
          type="text"
          :value="modelValue.ben_primary_idnumber"
          @input="update('ben_primary_idnumber', $event.target.value)"
          placeholder="00000000000"
          dir="ltr"
          class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
          :class="isInvalid('ben_primary_idnumber') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        />
      </div>

      <!-- Passport Number -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.passportNumber') }}</label>
        <input
          type="text"
          :value="modelValue.passport_number"
          @input="update('passport_number', $event.target.value)"
          placeholder="A00000000"
          dir="ltr"
          class="w-full px-4 py-3 bg-gray-50/60 border border-gray-100 rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
        />
      </div>

      <!-- Nationality + Gender -->
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.nationality') }} <span class="text-red-500">*</span></label>
          <input
            type="text"
            list="country-list"
            :value="modelValue.ben_nationality"
            @input="update('ben_nationality', $event.target.value)"
            :placeholder="t('registration.personalInfo.nationalityPlaceholder')"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm transition-all"
            :class="isInvalid('ben_nationality') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
          <datalist id="country-list">
            <option v-for="country in countries" :key="country" :value="country" />
          </datalist>
        </div>
        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.gender') }} <span class="text-red-500">*</span></label>
          <select
            :value="modelValue.gender"
            @change="update('gender', $event.target.value)"
            class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
            :class="isInvalid('gender') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          >
            <option value="">{{ t('registration.personalInfo.genderPlaceholder') }}</option>
            <option value="Male">{{ t('registration.personalInfo.male') }}</option>
            <option value="Female">{{ t('registration.personalInfo.female') }}</option>
          </select>
        </div>
      </div>

      <!-- DOB + Phone -->
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.dob') }} <span class="text-red-500">*</span></label>
          <input
            type="date"
            :value="modelValue.date_of_birth"
            @input="update('date_of_birth', $event.target.value)"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm transition-all"
            :class="isInvalid('date_of_birth') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
            dir="ltr"
          />
        </div>
        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.phone') }} <span class="text-red-500">*</span></label>
          <input
            type="tel"
            :value="modelValue.phone_number"
            @input="update('phone_number', $event.target.value)"
            placeholder="0097400000000"
            dir="ltr"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm transition-all"
            :class="isInvalid('phone_number') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
        </div>
      </div>

      <!-- Marital Status -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.maritalStatus') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.marital_status"
          @change="update('marital_status', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
          :class="isInvalid('marital_status') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        >
          <option value="">{{ t('registration.personalInfo.maritalStatusPlaceholder') }}</option>
          <option value="Single">{{ t('registration.personalInfo.single') }}</option>
          <option value="Married">{{ t('registration.personalInfo.married') }}</option>
          <option value="Divorced">{{ t('registration.personalInfo.divorced') }}</option>
          <option value="Widowed">{{ t('registration.personalInfo.widowed') }}</option>
          <option value="Separated">{{ t('registration.personalInfo.separated') }}</option>
        </select>
      </div>

      <!-- Partner Phone (always shown) -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.partnerPhone') }}</label>
        <input
          type="tel"
          :value="modelValue.partners_phone_number"
          @input="update('partners_phone_number', $event.target.value)"
          placeholder="55000000"
          dir="ltr"
          class="w-full px-4 py-3 bg-gray-50/60 border border-gray-100 rounded-xl outline-none text-sm"
        />
      </div>

      <!-- Partner Name — shown when Married -->
      <template v-if="modelValue.marital_status === 'Married'">
        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.partnerName') }} <span class="text-red-500">*</span></label>
          <input
            type="text"
            :value="modelValue.partner_name"
            @input="update('partner_name', $event.target.value)"
            :placeholder="t('registration.personalInfo.partnerNamePlaceholder')"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
            :class="isInvalid('partner_name') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
        </div>
      </template>

      <!-- Ex-Partner Name — shown when Divorced or Widowed -->
      <template v-if="modelValue.marital_status === 'Divorced' || modelValue.marital_status === 'Widowed'">
        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.exPartnerName') }} <span class="text-red-500">*</span></label>
          <input
            type="text"
            :value="modelValue.expartner_name"
            @input="update('expartner_name', $event.target.value)"
            :placeholder="t('registration.personalInfo.exPartnerNamePlaceholder')"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
            :class="isInvalid('expartner_name') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
        </div>
      </template>

      <!-- Visa Type — only when nationality is NOT Qatar -->
      <template v-if="modelValue.ben_nationality && modelValue.ben_nationality !== 'Qatar'">
        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.visaType') }} <span class="text-red-500">*</span></label>
          <select
            :value="modelValue.visa_type"
            @change="update('visa_type', $event.target.value)"
            class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
            :class="isInvalid('visa_type') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          >
            <option value="">{{ t('registration.personalInfo.visaTypePlaceholder') }}</option>
            <option value="Residence">{{ t('registration.personalInfo.residence') }}</option>
            <option value="Visit">{{ t('registration.personalInfo.visit') }}</option>
          </select>
        </div>

        <!-- Years of Residence -->
        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.residenceYears') }} <span class="text-red-500">*</span></label>
          <input
            type="text"
            :value="modelValue.residence_years"
            @input="update('residence_years', $event.target.value)"
            :placeholder="t('registration.personalInfo.residenceYearsPlaceholder')"
            dir="ltr"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm transition-all"
            :class="isInvalid('residence_years') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
        </div>
      </template>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useLanguage } from '@/composables/useLanguage'

const { t, isRTL } = useLanguage()
const props = defineProps({
  modelValue: { type: Object, required: true },
  invalidFields: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue'])

const countries = ref([])

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
