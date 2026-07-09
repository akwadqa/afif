<template>
  <div class="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-sm" :dir="isRTL ? 'rtl' : 'ltr'">

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

      <!-- Arabic Name -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.arName') }} <span class="text-red-500">*</span></label>
        <input
          type="text"
          :value="modelValue.ar_name"
          @input="onArabicOnly('ar_name', $event)"
          :placeholder="t('registration.personalInfo.arNamePlaceholder')"
          dir="rtl"
          class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
          :class="isInvalid('ar_name') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        />
        <p v-if="numberWarnings.has('ar_name')" class="text-xs text-red-500">
          {{ t('registration.validation.arabicOnly') }}
        </p>
      </div>

      <!-- English Name -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.enName') }} <span class="text-red-500">*</span></label>
        <input
          type="text"
          :value="modelValue.en_name"
          @input="onTextOnly('en_name', $event)"
          :placeholder="t('registration.personalInfo.enNamePlaceholder')"
          dir="ltr"
          class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
          :class="isInvalid('en_name') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        />
        <p v-if="modelValue.en_name && hasArabicLetters(modelValue.en_name)" class="text-xs text-red-500">
          {{ t('registration.validation.englishOnly') }}
        </p>
        <p v-if="numberWarnings.has('en_name')" class="text-xs text-red-500">
          {{ t('registration.validation.noNumbers') }}
        </p>
      </div>

      <!-- Primary ID Type -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.primaryIdType') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.ben_primary_idtype || 'Qatari Id'"
          disabled
          class="select-field w-full px-4 py-3 bg-gray-100 border rounded-xl outline-none text-sm text-gray-600 appearance-none cursor-not-allowed"
          :class="isInvalid('ben_primary_idtype') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        >
          <option value="Qatari Id">{{ t('registration.personalInfo.qatariId') }}</option>
        </select>
      </div>

      <!-- Primary ID Number -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.primaryIdNumber') }} <span class="text-red-500">*</span></label>
        <input
          type="text"
          :value="modelValue.ben_primary_idnumber"
          @input="onDigitsOnly('ben_primary_idnumber', $event, 11)"
          maxlength="11"
          placeholder="00000000000"
          dir="ltr"
          class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
          :class="isInvalid('ben_primary_idnumber') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        />
        <p v-if="modelValue.ben_primary_idnumber && modelValue.ben_primary_idnumber.length !== 11" class="text-xs text-red-500">
          {{ t('registration.validation.idMustBe11') }}
        </p>
      </div>


      <!-- ID Expiry Date -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.idExpiryDate') }} <span class="text-red-500">*</span></label>
        <DatePicker
          :modelValue="modelValue.id_expiry_date"
          @change="(val) => update('id_expiry_date', val)"
          placeholder="YYYY-MM-DD"
          :clearable="false"
          class="w-full"
        >
          <template #target="{ togglePopover, inputValue }">
            <div
              @click="togglePopover"
              class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm transition-all cursor-pointer flex items-center justify-between"
              :class="isInvalid('id_expiry_date') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
              dir="ltr"
            >
              <span :class="(inputValue || modelValue.id_expiry_date) ? 'text-gray-900' : 'text-gray-400'">
                {{ inputValue || modelValue.id_expiry_date || 'YYYY-MM-DD' }}
              </span>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 text-gray-400">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5" />
              </svg>
            </div>
          </template>
        </DatePicker>
      </div>

      <!-- Passport Number -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.passportNumber') }} <span class="text-red-500">*</span></label>
        <input
          type="text"
          :value="modelValue.passport_number"
          @input="onPassportInput($event)"
          maxlength="9"
          placeholder="A12345678"
          dir="ltr"
          class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
          :class="isInvalid('passport_number') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        />
        <p v-if="modelValue.passport_number && !isValidPassport(modelValue.passport_number)" class="text-xs text-red-500">
          {{ t('registration.validation.passportFormat') }}
        </p>
      </div>

      <!-- Nationality + Gender -->
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.nationality') }} <span class="text-red-500">*</span></label>
          <Autocomplete
            :options="countryOptions"
            :modelValue="modelValue.ben_nationality"
            @change="(opt) => update('ben_nationality', opt?.value || '')"
          >
            <template #target="{ togglePopover }">
              <div
                @click="togglePopover"
                class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm appearance-none transition-all cursor-pointer"
                :class="isInvalid('ben_nationality') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
              >
                <span :class="modelValue.ben_nationality ? 'text-gray-900' : 'text-gray-400'">
                  {{ modelValue.ben_nationality ? countryLabel(modelValue.ben_nationality) : t('registration.personalInfo.nationalityPlaceholder') }}
                </span>
              </div>
            </template>
          </Autocomplete>
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
          <DatePicker
            :modelValue="modelValue.date_of_birth"
            @change="(val) => update('date_of_birth', val)"
            placeholder="YYYY-MM-DD"
            :clearable="false"
            class="w-full"
          >
            <template #target="{ togglePopover, inputValue }">
              <div
                @click="togglePopover"
                class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm transition-all cursor-pointer flex items-center justify-between"
                :class="isInvalid('date_of_birth') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
                dir="ltr"
              >
                <span :class="(inputValue || modelValue.date_of_birth) ? 'text-gray-900' : 'text-gray-400'">
                  {{ inputValue || modelValue.date_of_birth || 'YYYY-MM-DD' }}
                </span>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 text-gray-400">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5" />
                </svg>
              </div>
            </template>
          </DatePicker>
  
          <p v-if="modelValue.date_of_birth && !isAtLeast21(modelValue.date_of_birth)" class="text-xs text-red-500">
            {{ t('registration.validation.minimumAge') }}
          </p>
        </div>
        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.phone') }} <span class="text-red-500">*</span></label>
          <input
            type="tel"
            :value="modelValue.phone_number"
            @input="onDigitsOnly('phone_number', $event, 8)"
            maxlength="8"
            placeholder="00000000"
            dir="ltr"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
            :class="isInvalid('phone_number') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
          <p v-if="modelValue.phone_number && modelValue.phone_number.length !== 8" class="text-xs text-red-500">
            {{ t('registration.validation.phoneMustBe8') }}
          </p>
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
          @input="onDigitsOnly('partners_phone_number', $event, 8)"
          maxlength="8"
          placeholder="00000000"
          dir="ltr"
          class="w-full px-4 py-3 bg-gray-50/60 border border-gray-100 rounded-xl outline-none text-sm"
        />
        <p v-if="modelValue.partners_phone_number && modelValue.partners_phone_number.length !== 8" class="text-xs text-red-500">
          {{ t('registration.validation.phoneMustBe8') }}
        </p>
      </div>

      <!-- Partner Name — shown when Married -->
      <template v-if="modelValue.marital_status === 'Married'">
        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.partnerName') }} <span class="text-red-500">*</span></label>
          <input
            type="text"
            :value="modelValue.partner_name"
            @input="onTextOnly('partner_name', $event)"
            :placeholder="t('registration.personalInfo.partnerNamePlaceholder')"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
            :class="isInvalid('partner_name') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
          <p v-if="numberWarnings.has('partner_name')" class="text-xs text-red-500">
            {{ t('registration.validation.noNumbers') }}
          </p>
        </div>
      </template>

      <!-- Ex-Partner Name — shown when Divorced or Widowed -->
      <template v-if="modelValue.marital_status === 'Divorced' || modelValue.marital_status === 'Widowed'">
        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.exPartnerName') }} <span class="text-red-500">*</span></label>
          <input
            type="text"
            :value="modelValue.expartner_name"
            @input="onTextOnly('expartner_name', $event)"
            :placeholder="t('registration.personalInfo.exPartnerNamePlaceholder')"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
            :class="isInvalid('expartner_name') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
          <p v-if="numberWarnings.has('expartner_name')" class="text-xs text-red-500">
            {{ t('registration.validation.noNumbers') }}
          </p>
        </div>
      </template>

      <!-- Visa Type — fixed field, always shown -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.visaType') }} <span class="text-red-500">*</span></label>
        <select
          :value="modelValue.visa_type || 'Residence'"
          disabled
          class="select-field w-full px-4 py-3 bg-gray-100 border rounded-xl outline-none text-sm text-gray-600 appearance-none cursor-not-allowed"
          :class="isInvalid('visa_type') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        >
          <option value="Residence">{{ t('registration.personalInfo.residence') }}</option>
        </select>
      </div>

      <!-- Years of Residence — depends on visa type = Residence, always shown -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.personalInfo.residenceYears') }} <span class="text-red-500">*</span></label>
        <input
          type="text"
          :value="modelValue.residence_years"
          @input="update('residence_years', $event.target.value)"
          :placeholder="t('registration.personalInfo.residenceYearsPlaceholder')"
          class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm transition-all"
          :class="isInvalid('residence_years') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        />
      </div>

    </div>

    <!-- Additional Info section — starts on a new row -->
    <div class="border-t border-gray-100 my-6"></div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

      <!-- Relation to Requestor -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.requestorRelation') }} <span class="text-red-500">*</span></label>
        <select
          :value="additionalInfo.ben_requestor_relationtype || 'The same subvention requestor'"
          disabled
          class="select-field w-full px-4 py-3 bg-gray-100 border rounded-xl outline-none text-sm text-gray-600 appearance-none cursor-not-allowed"
          :class="isInvalid('ben_requestor_relationtype') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        >
          <option value="The same subvention requestor">{{ t('registration.additionalInfo.sameRequestor') }}</option>
        </select>
      </div>

      <!-- Placeholder to keep grid aligned when requestor fields are hidden -->
      <div v-if="additionalInfo.ben_requestor_relationtype !== 'Relative to the subvention requestor'" />

      <!-- Requestor fields — shown when "Relative to the subvention requestor" -->
      <template v-if="additionalInfo.ben_requestor_relationtype === 'Relative to the subvention requestor'">

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.requestorName') }} <span class="text-red-500">*</span></label>
          <input
            type="text"
            :value="additionalInfo.requestor_name"
            @input="onTextOnlyAdditional('requestor_name', $event)"
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
            :value="additionalInfo.requestor_idtype"
            @change="updateAdditional('requestor_idtype', $event.target.value)"
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
            :value="additionalInfo.requestor_idnumber"
            @input="onDigitsOnlyAdditional('requestor_idnumber', $event, 11)"
            maxlength="11"
            placeholder="00000000000"
            dir="ltr"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
            :class="isInvalid('requestor_idnumber') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
          <p v-if="additionalInfo.requestor_idnumber && additionalInfo.requestor_idnumber.length !== 11" class="text-xs text-red-500">
            {{ t('registration.validation.idMustBe11') }}
          </p>
        </div>

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.requestorNationality') }} <span class="text-red-500">*</span></label>
          <Autocomplete
            :options="countryOptions"
            :modelValue="additionalInfo.requestor_nationality"
            @change="(opt) => updateAdditional('requestor_nationality', opt?.value || '')"
          >
            <template #target="{ togglePopover }">
              <div
                @click="togglePopover"
                class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm appearance-none transition-all cursor-pointer"
                :class="isInvalid('requestor_nationality') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
              >
                <span :class="additionalInfo.requestor_nationality ? 'text-gray-900' : 'text-gray-400'">
                  {{ additionalInfo.requestor_nationality ? countryLabel(additionalInfo.requestor_nationality) : t('registration.additionalInfo.requestorNationalityPlaceholder') }}
                </span>
              </div>
            </template>
          </Autocomplete>
        </div>

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.requestorPhone') }} <span class="text-red-500">*</span></label>
          <input
            type="tel"
            :value="additionalInfo.requestor_number"
            @input="onDigitsOnlyAdditional('requestor_number', $event, 8)"
            maxlength="8"
            placeholder="00000000"
            dir="ltr"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
            :class="isInvalid('requestor_number') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
          <p v-if="additionalInfo.requestor_number && additionalInfo.requestor_number.length !== 8" class="text-xs text-red-500">
            {{ t('registration.validation.phoneMustBe8') }}
          </p>
        </div>

      </template>

      <!-- Secondary ID Type -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.secIdType') }} <span class="text-red-500">*</span></label>
        <select
          :value="additionalInfo.ben_sec_idtype || 'Passport'"
          disabled
          class="select-field w-full px-4 py-3 bg-gray-100 border rounded-xl outline-none text-sm text-gray-600 appearance-none cursor-not-allowed"
          :class="isInvalid('ben_sec_idtype') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        >
          <option value="Passport">{{ t('registration.personalInfo.passport') }}</option>
        </select>
      </div>

      <!-- Secondary Nationality — shown when secondary ID is Passport -->
      <div v-if="additionalInfo.ben_sec_idtype === 'Passport'" class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.secNationality') }} <span class="text-red-500">*</span></label>
        <Autocomplete
          :options="countryOptions"
          :modelValue="additionalInfo.ben_sec_nationality"
          @change="(opt) => updateAdditional('ben_sec_nationality', opt?.value || '')"
        >
          <template #target="{ togglePopover }">
            <div
              @click="togglePopover"
              class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm appearance-none transition-all cursor-pointer"
              :class="isInvalid('ben_sec_nationality') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
            >
              <span :class="additionalInfo.ben_sec_nationality ? 'text-gray-900' : 'text-gray-400'">
                {{ additionalInfo.ben_sec_nationality ? countryLabel(additionalInfo.ben_sec_nationality) : t('registration.personalInfo.nationalityPlaceholder') }}
              </span>
            </div>
          </template>
        </Autocomplete>
      </div>

      <!-- Gulf Country — shown when secondary ID is GCC Id -->
      <div v-if="additionalInfo.ben_sec_idtype === 'GCC Id'" class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.gulfCountry') }} <span class="text-red-500">*</span></label>
        <select
          :value="additionalInfo.ben_sec_gulf_country"
          @change="updateAdditional('ben_sec_gulf_country', $event.target.value)"
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
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.secIdNumber') }} <span class="text-red-500">*</span></label>
        <input
          type="text"
          :value="additionalInfo.ben_sec_idnumber"
          @input="onAlphanumericOnly('ben_sec_idnumber', $event, 9)"
          maxlength="9"
          placeholder="A12345678"
          dir="ltr"
          class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
          :class="isInvalid('ben_sec_idnumber') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        />
      </div>

      <!-- Currently Working -->
      <div class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.currentlyWorking') }} <span class="text-red-500">*</span></label>
        <select
          :value="additionalInfo.currently_working"
          @change="updateAdditional('currently_working', $event.target.value)"
          class="select-field w-full px-4 py-3 bg-gray-50/60 border rounded-xl outline-none text-sm text-gray-600 appearance-none transition-all"
          :class="isInvalid('currently_working') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
        >
          <option value="">{{ t('registration.additionalInfo.yesNo') }}</option>
          <option value="Yes">{{ t('registration.additionalInfo.yes') }}</option>
          <option value="No">{{ t('registration.additionalInfo.no') }}</option>
        </select>
      </div>

      <!-- Employment fields — shown when currently working = Yes -->
      <template v-if="additionalInfo.currently_working === 'Yes'">

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.employerName') }} <span class="text-red-500">*</span></label>
          <input
            type="text"
            :value="additionalInfo.employer_name"
            @input="onTextOnlyAdditional('employer_name', $event)"
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
            :value="additionalInfo.employer_address"
            @input="updateAdditional('employer_address', $event.target.value)"
            :placeholder="t('registration.additionalInfo.employerAddressPlaceholder')"
            class="w-full px-4 py-3 bg-gray-50/60 border rounded-xl focus:ring-2 focus:ring-[#34B0EE] focus:bg-white outline-none text-sm transition-all"
            :class="isInvalid('employer_address') ? 'border-red-400 bg-red-50' : 'border-gray-100'"
          />
        </div>

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.occupation') }} <span class="text-red-500">*</span></label>
          <input
            type="text"
            :value="additionalInfo.occupation"
            @input="onTextOnlyAdditional('occupation', $event)"
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
        v-if="isResidence && additionalInfo.currently_working === 'No'"
        class="space-y-1.5"
      >
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.workedBefore') }} <span class="text-red-500">*</span></label>
        <select
          :value="additionalInfo.worked_before"
          @change="updateAdditional('worked_before', $event.target.value)"
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
          :value="additionalInfo.education_level"
          @change="updateAdditional('education_level', $event.target.value)"
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

      <!-- Sponsor Name — hidden when nationality is Qatar -->
      <div v-if="modelValue.ben_nationality !== 'Qatar'" class="space-y-1.5">
        <label class="text-sm font-medium text-gray-700">{{ t('registration.additionalInfo.sponsorName') }} <span class="text-red-500">*</span></label>
        <input
          type="text"
          :value="additionalInfo.sponsor_name"
          @input="onTextOnlyAdditional('sponsor_name', $event)"
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
import { ref, computed, onMounted, watch } from 'vue'
import { DatePicker, Autocomplete } from 'frappe-ui'
import { useLanguage } from '@/composables/useLanguage'
import { arabicToWestern } from '@/utils/inputHelpers'

const { t, isRTL } = useLanguage()


const props = defineProps({
  modelValue: { type: Object, required: true },
  additionalInfo: { type: Object, default: () => ({}) },
  invalidFields: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue', 'update:additionalInfo'])

const countries = ref([])
const numberWarnings = ref(new Set())

const countryOptions = computed(() =>
  countries.value.map(name => {
    const key = 'countries.' + name
    const label = t(key)
    return { label: label === key ? name : label, value: name }
  })
)

const isResidence = computed(() => (props.modelValue.visa_type || 'Residence') === 'Residence')

onMounted(async () => {
  if (!props.modelValue.visa_type) {
    update('visa_type', 'Residence')
  }

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

function updateAdditional(field, value) {
  emit('update:additionalInfo', { ...props.additionalInfo, [field]: value })
}

function hasArabicLetters(val) {
  return /[؀-ۿ]/.test(val)
}

function onTextOnly(field, event) {
  const raw = event.target.value
  const val = raw.replace(/[0-9]/g, '')
  event.target.value = val
  update(field, val)
  if (raw !== val) numberWarnings.value.add(field)
  else numberWarnings.value.delete(field)
}

function onArabicOnly(field, event) {
  const raw = event.target.value
  const val = raw.replace(/[^ء-ي\s]/g, '')
  event.target.value = val
  update(field, val)
  if (raw !== val) numberWarnings.value.add(field)
  else numberWarnings.value.delete(field)
}

function onTextOnlyAdditional(field, event) {
  const raw = event.target.value
  const val = raw.replace(/[0-9]/g, '')
  event.target.value = val
  updateAdditional(field, val)
  if (raw !== val) numberWarnings.value.add(field)
  else numberWarnings.value.delete(field)
}

function isAtLeast21(dob) {
  if (!dob) return true
  const today = new Date()
  const birthDate = new Date(dob)
  let age = today.getFullYear() - birthDate.getFullYear()
  const monthDiff = today.getMonth() - birthDate.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--
  }
  return age >= 21
}

function onDigitsOnly(field, event, maxLen) {
  const val = arabicToWestern(event.target.value).replace(/\D/g, '').slice(0, maxLen)
  event.target.value = val
  update(field, val)
}

function onDigitsOnlyAdditional(field, event, maxLen) {
  const val = arabicToWestern(event.target.value).replace(/\D/g, '').slice(0, maxLen)
  event.target.value = val
  updateAdditional(field, val)
}

function onAlphanumericOnly(field, event, maxLen) {
  const val = arabicToWestern(event.target.value).toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, maxLen)
  event.target.value = val
  updateAdditional(field, val)
}

function onPassportInput(event) {
  let val = arabicToWestern(event.target.value).toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 9)
  event.target.value = val
  update('passport_number', val)
}

function isValidPassport(val) {
  return /^[A-Z0-9]{1,9}$/.test(val)
}

function countryLabel(name) {
  if (!name) return ''
  const key = 'countries.' + name
  const label = t(key)
  return label === key ? name : label
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
