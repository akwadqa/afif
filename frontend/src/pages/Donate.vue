<template>
  <div class="landing-page" :dir="isRTL ? 'rtl' : 'ltr'" style="background: #EBF4FF;">
    <div class="landing-inner">

      <!-- Category filter chips -->
      <div class="chip-bar">
        <div class="trust-badge">
          <span class="badge-icon" v-html="noFeesIconSvg" />
          <span>{{ t('donation.landing.noFees') }}</span>
        </div>

        <div class="chip-scroll">
          <button
            type="button"
            class="icon-chip all-chip"
            :class="{ active: activeProgram === 'all' }"
            :title="t('donation.landing.allFilter')"
            :aria-label="t('donation.landing.allFilter')"
            @click="activeProgram = 'all'"
          >
            <span class="w-4 h-4 sm:w-5 sm:h-5" v-html="gridIconSvg" />
          </button>

          <button
            v-for="program in programs"
            :key="program.name"
            type="button"
            class="icon-chip"
            :class="{ active: activeProgram === program.name }"
            :title="program.title"
            :aria-label="program.title"
            @click="activeProgram = program.name"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-[24px] h-[24px] sm:w-[30px] sm:h-[30px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" v-html="getProgramIcon(program.icon_key)" />
          </button>
        </div>
      </div>

      <div v-if="landing.loading && !programs.length" class="loading-state">
        <svg class="loading-spinner" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
        </svg>
      </div>

      <p v-else-if="!programs.length" class="empty-state">
        {{ t('donation.landing.noPrograms') }}
      </p>

      <!-- Program sections -->
      <section
        v-for="(program, index) in visiblePrograms"
        :key="program.name"
        class="program-section"
        :style="{ animationDelay: `${index * 80}ms` }"
      >
        <div class="program-header">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 shrink-0 text-sky-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" v-html="getProgramIcon(program.icon_key)" />
          <h2 class="program-title">{{ program.title }}</h2>
        </div>

        <div v-if="program.intro" class="program-quote" v-html="program.intro"></div>

        <p v-if="!program.projects.length" class="empty-state">
          {{ t('donation.landing.noProjects') }}
        </p>
        <div v-else class="projects-wrap">
          <button
            type="button"
            class="nav-btn"
            :class="{ 'nav-btn-active': (activeNavDirection[program.name] ?? -1) === -1 }"
            :aria-label="t('donation.detail.back')"
            @click="scrollRow($event, -1, program.name)"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5" :class="{ 'rotate-180': isRTL }">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
            </svg>
          </button>
          <div class="projects-row">
            <DonationProjectCard v-for="project in program.projects" :key="project.name" :project="project" />
          </div>
          <button
            type="button"
            class="nav-btn"
            :class="{ 'nav-btn-active': activeNavDirection[program.name] === 1 }"
            :aria-label="t('donation.detail.back')"
            @click="scrollRow($event, 1, program.name)"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5" :class="{ 'rotate-180': isRTL }">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
            </svg>
          </button>
        </div>
      </section>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { createResource } from 'frappe-ui'
import { useLanguage } from '@/composables/useLanguage'
import { getProgramIcon, gridIconSvg, noFeesIconSvg } from '@/config/donationIcons'
import DonationProjectCard from '@/components/donation/DonationProjectCard.vue'

const { t, isRTL, currentLang } = useLanguage()

const activeProgram = ref('all')

const landing = createResource({
  url: 'afif.donation_api.get_donation_landing',
  method: 'GET',
})

const programs = computed(() => landing.data || [])

const visiblePrograms = computed(() => {
  if (activeProgram.value === 'all') return programs.value
  return programs.value.filter((program) => program.name === activeProgram.value)
})

function fetchLanding() {
  landing.submit({ lang: currentLang.value })
}

onMounted(fetchLanding)
watch(currentLang, fetchLanding)

const activeNavDirection = reactive({})

function scrollRow(event, direction, programName) {
  activeNavDirection[programName] = direction
  const row = event.currentTarget.closest('.projects-wrap')?.querySelector('.projects-row')
  // In RTL, scrollLeft grows negative as content scrolls toward later items,
  // the opposite of LTR - flip the sign so "forward" always reveals later cards.
  const signedDirection = isRTL.value ? -direction : direction
  row?.scrollBy({ left: signedDirection * 320, behavior: 'smooth' })
}
</script>

<style scoped>
.landing-page {
  @apply min-h-screen py-6 px-3 sm:py-10 sm:px-4;
}

.landing-inner {
  @apply max-w-6xl mx-auto flex flex-col gap-6 sm:gap-10;
}

.chip-bar {
  @apply relative flex items-center justify-center min-h-[42px] sm:min-h-[50px];
}

.chip-scroll {
  @apply flex items-center gap-2.5 sm:gap-[25px] overflow-x-auto max-w-full;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.chip-scroll::-webkit-scrollbar {
  display: none;
}

.icon-chip {
  @apply flex items-center justify-center shrink-0 w-[42px] h-[42px] sm:w-[50px] sm:h-[50px] transition-colors;
  background: #f8fafc;
  border: 1px solid #e1e1e1;
  border-radius: 12px;
  color: #64748b;
}

.icon-chip:hover {
  @apply bg-sky-50;
}

.icon-chip.active {
  background: #0570b6;
  border-color: #0570b6;
  color: #ffffff;
}

.all-chip {
  @apply flex;
}

@media (min-width: 768px) {
  .all-chip {
    position: absolute;
    inset-inline-start: 0;
  }
}

.trust-badge {
  @apply hidden md:flex items-center gap-2 px-4 py-2 rounded-full text-xs font-medium whitespace-nowrap;
  position: absolute;
  inset-inline-end: 0;
  background: #ffffff;
  border: 1px solid rgba(189, 200, 209, 0.3);
  backdrop-filter: blur(6px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
  color: #0570b6;
  letter-spacing: -0.3px;
}

.badge-icon {
  @apply flex items-center justify-center w-6 h-6 rounded-full shrink-0;
  background: rgba(5, 112, 182, 0.1);
  color: #0570b6;
  padding: 4px;
}

.program-section {
  @apply bg-white rounded-2xl sm:rounded-[32px] p-4 sm:p-6 md:p-10 shadow-sm border border-gray-100 flex flex-col gap-4 sm:gap-6;
  animation: section-fade-in 0.45s ease both;
}

@keyframes section-fade-in {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.loading-state {
  @apply flex items-center justify-center py-20;
}

.loading-spinner {
  @apply w-9 h-9 animate-spin;
  color: #34b0ee;
}

.program-header {
  @apply flex items-center justify-start gap-2;
}

.program-title {
  @apply text-base sm:text-lg font-bold;
  color: #0570b6;
}

.program-quote {
  border-inline-start: 4px solid #00adef;
  @apply bg-sky-50 rounded-xl px-4 py-3 sm:px-5 sm:py-4 text-[13px] sm:text-sm leading-relaxed;
  color: #141d23;
}

.projects-wrap {
  @apply flex items-center gap-2 sm:gap-3;
}

.projects-row {
  @apply flex-1 flex gap-3 sm:gap-4 overflow-x-auto scroll-smooth;
  scrollbar-width: none;
  -ms-overflow-style: none;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
}

.projects-row::-webkit-scrollbar {
  display: none;
}

.nav-btn {
  @apply hidden md:flex shrink-0 w-9 h-9 items-center justify-center rounded-full shadow-sm border transition-all active:scale-90;
  background-color: #f9fafb;
  color: #6b7280;
  border-color: #e5e7eb;
}

.nav-btn-active {
  background-color: #0570b6;
  @apply text-white border-transparent;
}

.empty-state {
  @apply text-center text-sm text-gray-400;
}
</style>
