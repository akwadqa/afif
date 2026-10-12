<template>
  <div class="detail-page" :dir="isRTL ? 'rtl' : 'ltr'" style="background: #EBF4FF;">
    <div class="detail-inner" :class="{ 'is-wide': isWide }" v-if="project">

      <nav class="back-btn" aria-label="breadcrumb">
        <a href="#" class="crumb-link" @click.prevent="router.push({ name: 'Donate' })">{{ t('donation.detail.mainPage') }}</a>
        <template v-if="project.program_title">
          <span class="crumb-sep">/</span>
          <a href="#" class="crumb-link" @click.prevent="router.push({ name: 'Donate' })">{{ project.program_title }}</a>
        </template>
        <span class="crumb-sep">/</span>
        <span class="crumb-current">{{ project.title }}</span>
      </nav>

      <div class="intro-row">
        <div class="quotes-box">
          <div class="box-header">
            <span class="title-icon">
              <img v-if="project.program_icon" :src="project.program_icon" alt="" />
              <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" aria-hidden="true" v-html="programIconFallback" />
            </span>
            <h2 class="box-title">{{ project.title }}</h2>
          </div>
          <div v-if="project.body" class="project-body" v-html="project.body"></div>
        </div>

        <div class="image-wrap" :style="imageRatio ? { aspectRatio: imageRatio } : null">
          <img v-if="project.image" :src="project.image" :alt="project.title" @load="onImageLoad" />
          <div class="location-badge">
            <span class="flag-icon" v-html="qatarFlagSvg" />
            <span>{{ locationLabel }}</span>
          </div>
        </div>
      </div>

      <!-- Progress hidden: one compact bar with the project info at the start and share + donate at the end -->
      <div v-if="!hasProgress" class="compact-card">
        <div class="compact-info">
          <span v-if="project.program_title" class="type-badge">{{ project.program_title }}</span>
          <span class="compact-number">
            {{ t('donation.detail.projectNumber') }}
            <span class="compact-number-value">{{ project.name }}</span>
          </span>
        </div>
        <div class="compact-actions">
          <button type="button" class="icon-btn" :aria-label="t('donation.detail.share')" :title="t('donation.detail.share')" @click="share">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 sm:w-6 sm:h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7.217 10.907a2.25 2.25 0 1 0 0 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186 9.566-5.314m-9.566 7.5 9.566 5.314m0-12.814a2.25 2.25 0 1 0 4.5 0 2.25 2.25 0 0 0-4.5 0Zm0 12.814a2.25 2.25 0 1 0 4.5 0 2.25 2.25 0 0 0-4.5 0Z" />
            </svg>
          </button>
          <button type="button" class="primary-btn compact-donate" @click="openDonationDialog(project)">
            {{ t('donation.donateNow') }}
          </button>
        </div>
      </div>

      <div v-else class="widget-card">
        <div class="title-row">
          <div class="info-col">
            <span v-if="project.program_title" class="type-badge">{{ project.program_title }}</span>
          </div>
          <div class="meta-col">
            <span class="project-number">{{ project.name }}</span>
            <button type="button" class="icon-btn" :aria-label="t('donation.detail.share')" @click="share">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 sm:w-6 sm:h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M7.217 10.907a2.25 2.25 0 1 0 0 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186 9.566-5.314m-9.566 7.5 9.566 5.314m0-12.814a2.25 2.25 0 1 0 4.5 0 2.25 2.25 0 0 0-4.5 0Zm0 12.814a2.25 2.25 0 1 0 4.5 0 2.25 2.25 0 0 0-4.5 0Z" />
              </svg>
            </button>
          </div>
        </div>

        <div class="financial-progress">
          <div class="totals-row">
            <div class="total-block">
              <span class="total-label">{{ t('donation.partiallyFundedLabel') }}</span>
              <span class="total-value paid-value">{{ formatAmount(project.donated_amount) }} {{ t('donation.currency') }}</span>
            </div>
            <div class="total-block">
              <span class="total-label">{{ t('donation.targetAmount') }}</span>
              <span class="total-value">{{ formatAmount(project.required_amount) }} {{ t('donation.currency') }}</span>
            </div>
          </div>

          <div class="progress-bar-container">
            <div class="progress-bar-fill" :class="{ 'fully-funded': coveragePercentage >= 100 }" :style="{ width: animatedWidth + '%' }" />
          </div>

          <div class="required-row">
            <span class="percentage-label">{{ coveragePercentage }}%</span>
            <span>{{ t('donation.detail.remaining') }} {{ formatAmount(remainingAmount) }} {{ t('donation.currency') }}</span>
          </div>
        </div>

        <div class="action-area">
          <button type="button" class="primary-btn" @click="openDonationDialog(project)">
            {{ t('donation.donateNow') }}
          </button>
        </div>
      </div>
    </div>

    <div v-else-if="detail.loading" class="loading-state">
      <svg class="loading-spinner" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
      </svg>
    </div>

    <p v-else class="not-found">{{ t('donation.detail.notFound') }}</p>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { projectDetail, projectDetails, loadProjectDetail } from '@/data/donation'
import { useSidebar } from '@/composables/useSidebar'
import { session } from '@/data/session'
import { useLanguage } from '@/composables/useLanguage'
import { useDonationDialog } from '@/composables/useDonationDialog'
import { programIconFallback, qatarFlagSvg } from '@/config/donationIcons'

const route = useRoute()
const router = useRouter()
const { sidebarOpen } = useSidebar()
// Use the full width when the sidebar isn't taking space
const isWide = computed(() => !(session.isLoggedIn && sidebarOpen.value))
const { t, isRTL, currentLang } = useLanguage()
const { openDonationDialog } = useDonationDialog()

const detail = projectDetail
const project = computed(() => projectDetails[`${route.params.name}:${currentLang.value}`] || null)

const hasProgress = computed(() => project.value?.show_progress !== 0)

const coveragePercentage = computed(() => Math.min(Math.round(project.value?.percentage || 0), 100))

// Starts at 0 and animates up to the real percentage whenever a project
// loads (including switching between projects and coming back to an already-loaded
// one), instead of appearing pre-filled.
const animatedWidth = ref(0)
watch(
  project,
  (newProject) => {
    if (!newProject) return
    animatedWidth.value = 0
    requestAnimationFrame(() => {
      animatedWidth.value = coveragePercentage.value
    })
  },
  { immediate: true }
)

const remainingAmount = computed(() =>
  Math.max((project.value?.required_amount || 0) - (project.value?.donated_amount || 0), 0)
)

// The photo's own width/height ratio, so the frame takes the photo's shape
// instead of cropping it or leaving empty strips beside it.
const imageRatio = ref(null)
watch(() => project.value?.image, () => {
  imageRatio.value = null
})

function onImageLoad(event) {
  const { naturalWidth, naturalHeight } = event.target
  if (naturalWidth && naturalHeight) imageRatio.value = naturalWidth / naturalHeight
}

const locationLabel = computed(() =>
  project.value?.location === 'outside_qatar' ? t('donation.location.outsideQatar') : t('donation.location.insideQatar')
)

function formatAmount(value) {
  return new Intl.NumberFormat('en-US').format(Math.round(value || 0))
}

function fetchDetail() {
  loadProjectDetail(route.params.name, currentLang.value)
}

onMounted(fetchDetail)
watch(currentLang, fetchDetail)
watch(() => route.params.name, fetchDetail)

async function share() {
  const url = window.location.href
  if (navigator.share) {
    try {
      await navigator.share({ title: project.value?.title, url })
      return
    } catch {
      return
    }
  }
  try {
    await navigator.clipboard.writeText(url)
  } catch {
    /* no-op: clipboard unavailable */
  }
}
</script>

<style scoped>
.detail-page {
  @apply min-h-screen py-6 px-3 sm:py-10 sm:px-4;
}

.detail-inner {
  @apply max-w-5xl mx-auto flex flex-col gap-5 sm:gap-8;
  animation: detail-fade-in 0.4s ease both;
}

@keyframes detail-fade-in {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.loading-state {
  @apply flex items-center justify-center py-24;
}

.loading-spinner {
  @apply w-9 h-9 animate-spin;
  color: #34b0ee;
}

.back-btn {
  @apply flex items-center flex-wrap gap-2 text-sm text-gray-500 font-medium;
}

.crumb-link {
  @apply hover:text-sky-600 transition-colors;
}

.crumb-sep {
  @apply text-gray-400;
}

.crumb-current {
  @apply text-gray-800;
}

.intro-row {
  @apply flex flex-col md:flex-row md:items-stretch gap-4 sm:gap-6;
}

.image-wrap {
  @apply relative w-full md:w-[42%] rounded-xl overflow-hidden shrink-0 self-start;
  aspect-ratio: 473 / 314;
  background: linear-gradient(359.92deg, rgba(0, 173, 239, 0.2) 0.07%, rgba(255, 255, 255, 0.2) 99.93%), #e6eff8;
}

/* Side by side, the photo gets a fixed, moderate height and its width follows the
   photo's own shape (aspect-ratio set from the loaded image), so the frame fits the
   photo exactly and a short description doesn't sit beside a huge image. The text
   box takes the remaining width. Very wide panoramas are capped at half the row. */
@media (min-width: 768px) {
  .image-wrap {
    width: auto;
    height: 260px;
    max-width: 50%;
  }
}

@media (min-width: 1024px) {
  .image-wrap {
    height: 280px;
  }
}

.image-wrap img {
  @apply w-full h-full object-cover absolute inset-0;
}

.location-badge {
  @apply absolute bottom-3 sm:bottom-4 flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-1 sm:py-1.5 rounded-xl text-xs sm:text-sm font-bold;
  inset-inline-end: 12px;
  background: rgba(246, 250, 255, 0.9);
  backdrop-filter: blur(2px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
  color: #141d23;
}

.flag-icon {
  @apply inline-flex w-[13px] h-[16px] sm:w-[16px] sm:h-[20px] shrink-0;
}

.quotes-box {
  @apply flex-1 flex flex-col justify-start gap-4 sm:gap-5 bg-white rounded-xl p-5 sm:p-7 lg:px-9 lg:py-8;
  border-inline-start: 4px solid #00adef;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.box-header {
  @apply flex items-center gap-3;
}

.title-icon {
  @apply flex items-center justify-center shrink-0 w-10 h-10 sm:w-12 sm:h-12 rounded-xl p-2;
  background: #e6f6fd;
  color: #0570b6;
}

.title-icon img,
.title-icon svg {
  @apply w-full h-full object-contain;
}

.box-title {
  @apply text-xl sm:text-2xl lg:text-[26px] font-bold;
  line-height: 1.35;
  color: #141d23;
}

.project-body {
  font-size: 15px;
  line-height: 26px;
  font-weight: 400;
  color: #1f2937;
}

@media (min-width: 640px) {
  .project-body {
    font-size: 17px;
    line-height: 30px;
  }
}

@media (min-width: 1024px) {
  .project-body {
    font-size: 18px;
    line-height: 32px;
  }
}

.widget-card {
  @apply bg-white rounded-xl p-5 sm:p-6 md:p-10 flex flex-col gap-5 sm:gap-6;
  border: 1px solid #bdc8d1;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.title-row {
  @apply flex items-start justify-between gap-3 sm:gap-4;
}

.info-col {
  @apply flex-1 flex flex-col items-start gap-2;
}

.meta-col {
  @apply flex flex-col items-end gap-2 shrink-0;
}

.type-badge {
  @apply inline-flex px-3 py-1 rounded-full text-xs sm:text-sm font-medium whitespace-nowrap;
  background: #e6eff8;
  color: #3e4850;
}

.project-number {
  font-size: 11px;
  color: #6b7280;
  white-space: nowrap;
}

@media (min-width: 640px) {
  .project-number {
    font-size: 12px;
  }
}

.icon-btn {
  @apply w-9 h-9 sm:w-11 sm:h-11 flex items-center justify-center bg-white border border-gray-200 rounded-xl shrink-0 shadow-sm transition-colors hover:bg-sky-50;
  color: #0570b6;
}

.financial-progress {
  @apply flex flex-col gap-3 sm:gap-4 p-4 sm:p-5 rounded-2xl;
  background: #f8fafc;
  border: 1px solid #dbe4ed;
}

.totals-row {
  @apply flex items-center justify-between gap-3 sm:gap-6 flex-wrap;
}

.total-block {
  @apply flex flex-col gap-1;
}

.total-block:last-child {
  @apply items-end text-end;
}

.total-label {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.28px;
  color: #3e4850;
}

.total-value {
  font-size: 16px;
  color: #3e4850;
}

.paid-value {
  font-size: 20px;
  font-weight: 700;
  color: #00658d;
}

@media (min-width: 640px) {
  .total-label {
    font-size: 14px;
  }

  .total-value {
    font-size: 18px;
  }

  .paid-value {
    font-size: 24px;
  }
}

.progress-bar-container {
  @apply flex overflow-hidden;
  background: #e0e3e8;
  border-radius: 9999px;
  height: 12px;
}

.progress-bar-fill {
  @apply h-full;
  background: linear-gradient(90deg, #83cfff 0%, #00658d 100%);
  border-radius: 9999px;
  transition: width 0.8s ease-out;
}

[dir='rtl'] .progress-bar-fill {
  background: linear-gradient(270deg, #00658d 0%, #83cfff 100%);
}

.progress-bar-fill.fully-funded {
  width: 100% !important;
}

.required-row {
  @apply flex items-center justify-between;
  font-size: 12px;
  color: #3e4850;
}

.percentage-label {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.28px;
  color: #141d23;
}

.action-area {
  @apply pt-3;
  border-top: 1px solid #bdc8d1;
}

.compact-card {
  @apply bg-white rounded-xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4;
  border: 1px solid #bdc8d1;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.compact-info {
  @apply flex flex-wrap items-center gap-2 sm:gap-3 min-w-0;
}

.compact-number {
  @apply inline-flex items-center gap-1.5 whitespace-nowrap text-xs sm:text-sm;
  color: #64748b;
}

.compact-number-value {
  @apply font-semibold;
  color: #141d23;
  direction: ltr;
  unicode-bidi: isolate;
}

.compact-actions {
  @apply flex items-center gap-2 sm:gap-3 shrink-0;
}

.primary-btn.compact-donate {
  @apply flex-1 sm:flex-none sm:w-[220px] h-9 sm:h-11 text-sm sm:text-base;
}

.primary-btn {
  @apply w-full h-[52px] sm:h-[60px] flex items-center justify-center text-white text-base sm:text-lg font-bold rounded-xl transition-opacity hover:opacity-90 border-none;
  background-color: #00adef;
}

.not-found {
  @apply text-center text-sm text-gray-400 mt-20;
}

.detail-inner.is-wide {
  max-width: 1600px;
}
</style>
