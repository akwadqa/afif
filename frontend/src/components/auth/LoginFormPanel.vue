<template>
  <div
    class="w-full md:w-1/2 p-8 md:p-12 flex flex-col justify-center"
    :dir="isRTL ? 'rtl' : 'ltr'"
  >
    <!-- Header -->
    <div class="mb-8">
      <h2 class="text-2xl font-bold text-sky-600 mb-2">
        {{ t('login.welcomeBack') }}
      </h2>
      <p class="text-sm text-gray-500">
        {{ t('login.subtitle') }}
      </p>
    </div>

    <!-- Form -->
    <form class="space-y-5" @submit.prevent="handleSubmit">

      <!-- Email -->
      <div class="space-y-1.5">
        <label class="block text-sm font-medium text-gray-700">
          {{ t('login.email') }}
        </label>
        <div class="relative">
          <input
            v-model="email"
            type="email"
            :placeholder="t('login.emailPlaceholder')"
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
          {{ t('login.password') }}
        </label>
        <div class="relative">
          <input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            :placeholder="t('login.passwordPlaceholder')"
            autocomplete="current-password"
            required
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
      </div>

      <!-- Forgot password -->
      <div :class="isRTL ? 'text-left' : 'text-right'">
        <a href="#" class="text-xs text-sky-600 hover:underline">
          {{ t('login.forgotPassword') }}
        </a>
      </div>

      <!-- Error message -->
      <p v-if="errorMsg" class="text-sm text-red-500 text-center -mt-1">
        {{ errorMsg }}
      </p>

      <!-- Submit -->
      <button
        type="submit"
        :disabled="session.login.loading"
        class="w-full text-white py-3 px-4 rounded-xl font-medium shadow-md transition-all hover:opacity-90 active:scale-[0.99] disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        style="background-color: #34B0EE;"
      >
        <svg v-if="session.login.loading" class="animate-spin w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        {{ t('login.loginBtn') }}
      </button>
    </form>

    <!-- Divider + Qatar Pass (commented out) -->
    <!--
    <div class="relative my-6 text-center">
      <div class="absolute inset-0 flex items-center">
        <div class="w-full border-t border-gray-100" />
      </div>
      <span class="relative bg-white px-3 text-xs text-gray-400">
        {{ t('login.or') }}
      </span>
    </div>

    <button
      type="button"
      class="w-full flex items-center justify-center border border-gray-200 rounded-xl py-3 px-4 hover:bg-gray-50 transition-colors shadow-sm mb-6 gap-2"
    >
      <span class="text-sm font-medium text-gray-700">
        {{ t('login.qatarPass') }}
      </span>
    </button>
    -->

    <!-- Register link -->
    <div class="text-center text-sm text-gray-500">
      {{ t('login.noAccount') }}
      <RouterLink to="/register" class="text-sky-600 font-semibold hover:underline mx-1">
        {{ t('login.createAccount') }}
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { session } from '@/data/session'
import { useLanguage } from '@/composables/useLanguage'

const { t, isRTL } = useLanguage()

const email = ref('')
const password = ref('')
const showPassword = ref(false)

const errorMsg = computed(() => {
  if (!session.login.error) return null
  return t('login.invalidCredentials')
})

function handleSubmit() {
  session.login.submit({ email: email.value, password: password.value })
}
</script>
