<template>
  <div
    class="w-full md:w-1/2 p-8 md:p-12 flex flex-col justify-center"
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
        to="/login"
        class="inline-block text-sm font-semibold hover:underline"
        style="color: #34B0EE;"
      >
        {{ t('register.loginLink') }}
      </router-link>
    </div>

    <!-- Form state -->
    <template v-else>
      <!-- Header -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold mb-2" style="color: #34B0EE;">
          {{ t('register.title') }}
        </h2>
        <p class="text-sm text-gray-500">
          {{ t('register.subtitle') }}
        </p>
      </div>

      <form class="space-y-5" @submit.prevent="handleSubmit">

        <!-- Full Name -->
        <div class="space-y-1.5">
          <label class="block text-sm font-medium text-gray-700">
            {{ t('register.fullName') }}
          </label>
          <div class="relative">
            <input
              v-model="fullName"
              type="text"
              :placeholder="t('register.fullNamePlaceholder')"
              autocomplete="name"
              required
              class="w-full py-3 bg-gray-50 border border-gray-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#34B0EE] focus:bg-white placeholder-gray-300 text-sm transition-all"
              :class="isRTL ? 'pr-4 pl-11 text-right' : 'pl-4 pr-11 text-left'"
            />
            <span
              class="absolute top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
              :class="isRTL ? 'left-4' : 'right-4'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
              </svg>
            </span>
          </div>
        </div>

        <!-- Email -->
        <div class="space-y-1.5">
          <label class="block text-sm font-medium text-gray-700">
            {{ t('register.email') }}
          </label>
          <div class="relative">
            <input
              v-model="email"
              type="email"
              :placeholder="t('register.emailPlaceholder')"
              autocomplete="email"
              required
              class="w-full py-3 bg-gray-50 border border-gray-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#34B0EE] focus:bg-white placeholder-gray-300 text-sm transition-all"
              :class="isRTL ? 'pr-4 pl-11 text-right' : 'pl-4 pr-11 text-left'"
            />
            <span
              class="absolute top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
              :class="isRTL ? 'left-4' : 'right-4'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25H4.5A2.25 2.25 0 0 1 2.25 17.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5H4.5a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75" />
              </svg>
            </span>
          </div>
        </div>

        <!-- Password -->
        <div class="space-y-1.5">
          <label class="block text-sm font-medium text-gray-700">
            {{ t('register.password') }}
          </label>
          <div class="relative">
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              :placeholder="t('register.passwordPlaceholder')"
              autocomplete="new-password"
              required
              minlength="8"
              class="w-full py-3 bg-gray-50 border border-gray-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#34B0EE] focus:bg-white placeholder-gray-300 text-sm transition-all"
              :class="isRTL ? 'pr-4 pl-20 text-right' : 'pl-4 pr-20 text-left'"
            />
            <!-- Lock icon -->
            <span
              class="absolute top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
              :class="isRTL ? 'left-10' : 'right-10'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" />
              </svg>
            </span>
            <!-- Toggle show/hide -->
            <button
              type="button"
              class="absolute top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
              :class="isRTL ? 'left-4' : 'right-4'"
              :aria-label="showPassword ? 'Hide password' : 'Show password'"
              @click="showPassword = !showPassword"
            >
              <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" />
              </svg>
            </button>
          </div>
          <p v-if="passwordTooShort" class="text-xs text-red-500 mt-1">
            {{ t('register.passwordMin') }}
          </p>
        </div>

        <!-- Error message -->
        <p v-if="errorMsg" class="text-sm text-red-500 text-center -mt-1">
          {{ errorMsg }}
        </p>

        <!-- Submit -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full text-white py-3 px-4 rounded-xl font-medium shadow-md transition-all hover:opacity-90 active:scale-[0.99] disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
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
      <div class="text-center text-sm text-gray-500 mt-6">
        {{ t('register.hasAccount') }}
        <router-link to="/login" class="font-semibold hover:underline mx-1" style="color: #34B0EE;">
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
const password = ref('')
const showPassword = ref(false)
const success = ref(false)
const serverError = ref(null)

const passwordTooShort = computed(() => password.value.length > 0 && password.value.length < 8)

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

function handleSubmit() {
  if (password.value.length < 8) return
  serverError.value = null
  signUp.submit({
    email: email.value,
    full_name: fullName.value,
    redirect_to: '/frontend/home',
  })
}
</script>
