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
      <p class="text-sm text-gray-600">{{ t('resetPassword.successMsg') }}</p>
      <RouterLink
        to="/signin"
        class="inline-block text-sm font-semibold hover:underline"
        style="color: #34B0EE;"
      >
        {{ t('resetPassword.backToLogin') }}
      </RouterLink>
    </div>

    <!-- Form state -->
    <template v-else>
      <!-- Header -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold mb-2" style="color: #34B0EE;">
          {{ t('resetPassword.title') }}
        </h2>
        <p class="text-sm text-gray-500">
          {{ t('resetPassword.subtitle') }}
        </p>
      </div>

      <form class="space-y-5" @submit.prevent="handleSubmit">

        <!-- Email -->
        <div class="space-y-1.5">
          <label class="block text-sm font-medium text-gray-700">
            {{ t('resetPassword.email') }}
          </label>
          <div class="relative">
            <input
              v-model="email"
              type="email"
              :placeholder="t('resetPassword.emailPlaceholder')"
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
          {{ t('resetPassword.submitBtn') }}
        </button>
      </form>

      <!-- Back to login -->
      <div class="text-center text-sm text-gray-500 mt-6">
        <RouterLink to="/signin" class="font-semibold hover:underline" style="color: #34B0EE;">
          {{ t('resetPassword.backToLogin') }}
        </RouterLink>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { createResource } from 'frappe-ui'
import { useLanguage } from '@/composables/useLanguage'

const { t, isRTL } = useLanguage()

const email = ref('')
const success = ref(false)
const serverError = ref(null)

const resetPassword = createResource({
  url: 'frappe.core.doctype.user.user.reset_password',
  onSuccess() {
    success.value = true
  },
  onError() {
    serverError.value = t('resetPassword.errorMsg')
  },
})

const loading = computed(() => resetPassword.loading)

const errorMsg = computed(() => serverError.value)

function handleSubmit() {
  serverError.value = null
  resetPassword.submit({ user: email.value })
}
</script>
