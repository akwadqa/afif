<template>
  <div class="relative flex-1 flex items-center justify-center p-4 py-8 min-h-screen" dir="rtl">
    <img
      :src="bgImg"
      alt=""
      aria-hidden="true"
      fetchpriority="high"
      class="absolute inset-0 w-full h-full object-cover -z-10 select-none pointer-events-none"
    />

    <div class="bg-white rounded-[2.5rem] shadow-2xl max-w-lg w-full p-10 flex flex-col items-center text-center border border-gray-50">

      <div class="relative mb-8">
        <div class="absolute inset-0 bg-sky-200 rounded-full blur-2xl opacity-40"></div>
        <div class="relative w-24 h-24 bg-[#34B0EE] rounded-full flex items-center justify-center shadow-lg shadow-sky-200">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="3" stroke="white" class="w-12 h-12">
            <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
          </svg>
        </div>
      </div>

      <h2 class="text-2xl font-bold text-sky-900 mb-6 leading-tight">
        لقد تم حفظ التسجيل بنجاح
      </h2>

      <p class="text-gray-500 text-base leading-relaxed mb-10 px-4">
        شكراً لتسجيلك، ستتلقى تحديثات حول حالة تسجيلك، يرجى التحقق من صندوق البريد الإلكتروني الخاص بك للحصول على تعليمات إضافية إذا كانت هناك.
      </p>

      <div class="w-full space-y-6">
        <button
          @click="$emit('view-status')"
          class="w-full flex items-center justify-center gap-2 bg-[#34B0EE] text-white py-4 px-6 rounded-2xl font-bold shadow-xl shadow-sky-100 hover:opacity-90 active:scale-[0.98] transition-all"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="w-5 h-5 shrink-0">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
          </svg>
          <span>الاطلاع على حالة تسجيل الملف</span>
        </button>

        <button
          v-if="showEditAnswers"
          @click="$emit('edit-answers')"
          class="flex items-center gap-2 text-sky-500 hover:text-sky-600 transition-colors mx-auto font-semibold text-sm group"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="w-4 h-4 shrink-0">
            <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125" />
          </svg>
          <span class="border-b border-transparent group-hover:border-sky-500">تعديل أجوبتك</span>
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import bgImg from '@/assets/images/background.png'

defineProps({
  showEditAnswers: { type: Boolean, default: true },
})
defineEmits(['view-status', 'edit-answers'])
</script>
