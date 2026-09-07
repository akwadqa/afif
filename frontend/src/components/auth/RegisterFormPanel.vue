<template>
  <div
    class="w-full md:w-1/2 p-8 md:p-8 lg:px-16 lg:py-20 flex flex-col justify-center bg-white mt-[35px] rounded-[0_10px]"
    :dir="isRTL ? 'rtl' : 'ltr'"
  >
    <!-- Success state -->
    <div v-if="success" class="text-center space-y-4">
      <div class="w-16 h-16 rounded-full flex items-center justify-center mx-auto" style="background-color: #E0F4FD;">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="#34B0EE" class="w-8 h-8">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
        </svg>
      </div>
      <p class="text-sm text-gray-600">{{ t('register.successMsg') }}</p>
      <router-link
        to="/signin"
        class="inline-block text-sm font-semibold text-[#0570B6] hover:underline"
      >
        {{ t('register.loginLink') }}
      </router-link>
    </div>

    <!-- Form state -->
    <template v-else>
      <!-- Header -->
      <div class="mb-6">
        <h2 class="text-[32px] leading-[40px] md:text-2xl md:leading-8 lg:text-[32px] lg:leading-[40px] font-medium text-[#0570B6] mb-2">
          {{ t('register.title') }}
        </h2>
        <p class="text-xl leading-7 md:text-base md:leading-6 lg:text-xl lg:leading-7 text-[#3E4850]">
          {{ t('register.subtitle') }}
        </p>
      </div>

      <form class="space-y-6" @submit.prevent="handleSubmit">

        <!-- Full Name -->
        <div class="space-y-[15px]">
          <label class="block text-base font-normal text-[#141D23] tracking-[0.28px]">
            {{ t('register.fullName') }}
          </label>
          <div class="relative">
            <input
              :value="fullName"
              @input="onFullNameInput"
              type="text"
              :placeholder="t('register.fullNamePlaceholder')"
              autocomplete="name"
              required
              class="w-full h-[53px] px-4 py-[11px] bg-[#F8FAFC] border border-[#F3F3F3] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#34B0EE] focus:bg-white placeholder-[#AEAFB0] text-base leading-[25px] transition-all"
              :class="isRTL ? 'pr-4 pl-11 text-right' : 'pl-4 pr-11 text-left'"
            />
            <span
              class="absolute top-1/2 -translate-y-1/2 text-[#AEAFB0] pointer-events-none"
              :class="isRTL ? 'left-4' : 'right-4'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
              </svg>
            </span>
          </div>
          <p v-if="nameNumberWarning" class="text-xs text-red-500">
            {{ t('registration.validation.noNumbers') }}
          </p>
        </div>

        <!-- Email -->
        <div class="space-y-[15px]">
          <label class="block text-base font-normal text-[#141D23] tracking-[0.28px]">
            {{ t('register.email') }}
          </label>
          <div class="relative">
            <input
              v-model="email"
              type="email"
              :placeholder="t('register.emailPlaceholder')"
              autocomplete="email"
              required
              class="w-full h-[53px] px-4 py-[11px] bg-[#F8FAFC] border border-[#F3F3F3] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#34B0EE] focus:bg-white placeholder-[#AEAFB0] text-base leading-[25px] transition-all"
              :class="isRTL ? 'pr-4 pl-11 text-right' : 'pl-4 pr-11 text-left'"
            />
            <span
              class="absolute top-1/2 -translate-y-1/2 text-[#AEAFB0] pointer-events-none"
              :class="isRTL ? 'left-4' : 'right-4'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25H4.5A2.25 2.25 0 0 1 2.25 17.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5H4.5a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75" />
              </svg>
            </span>
          </div>
        </div>

        <!-- Error message -->
        <p v-if="errorMsg" class="text-sm text-red-500 text-center -mt-1">
          {{ errorMsg }}
        </p>

        <!-- Submit -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full h-[60px] text-white rounded-xl text-xl font-bold tracking-[-0.35px] shadow-[0_2px_10px_rgba(0,0,0,0.25)] transition-all hover:opacity-90 active:scale-[0.99] disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          style="background-color: #34B0EE;"
        >
          <svg v-if="loading" class="animate-spin w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          {{ t('register.registerBtn') }}
        </button>
      </form>

      <!-- Login link -->
      <div class="flex items-center justify-center gap-[7px] text-base text-[#3E4850] mt-6">
        {{ t('register.hasAccount') }}
        <router-link to="/signin" class="text-sm font-semibold text-[#0570B6] hover:underline">
          {{ t('register.loginLink') }}
        </router-link>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { createResource } from 'frappe-ui'
import { useLanguage } from '@/composables/useLanguage'

const { t, isRTL } = useLanguage()

const fullName = ref('')
const email = ref('')
const success = ref(false)
const serverError = ref(null)
const nameNumberWarning = ref(false)

const signUp = createResource({
  url: 'frappe.core.doctype.user.user.sign_up',
  onSuccess(data) {
    // data is an array [status_code, message] from Frappe sign_up
    const status = Array.isArray(data) ? data[0] : data
    if (status === 0) {
      // email already exists
      serverError.value = t('register.emailExists')
    } else {
      success.value = true
    }
  },
  onError() {
    serverError.value = t('register.errorMsg')
  },
})

const loading = computed(() => signUp.loading)

const errorMsg = computed(() => serverError.value)

function onFullNameInput(event) {
  const raw = event.target.value
  const val = raw.replace(/[0-9]/g, '')
  event.target.value = val
  fullName.value = val
  nameNumberWarning.value = raw !== val
}

function handleSubmit() {
  serverError.value = null
  signUp.submit({
    email: email.value,
    full_name: fullName.value,
    redirect_to: '/beneficiary-profile',
  })
}
</script>
