<template>
  <div class="project-card" :dir="isRTL ? 'rtl' : 'ltr'">
    <div class="card-image">
      <img v-if="project.image" :src="project.image" :alt="project.title" />
      <button type="button" class="share-btn" :aria-label="t('donation.detail.share')" @click="share">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M7.217 10.907a2.25 2.25 0 1 0 0 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186 9.566-5.314m-9.566 7.5 9.566 5.314m0-12.814a2.25 2.25 0 1 0 4.5 0 2.25 2.25 0 0 0-4.5 0Zm0 12.814a2.25 2.25 0 1 0 4.5 0 2.25 2.25 0 0 0-4.5 0Z" />
        </svg>
      </button>
    </div>

    <div class="card-body">
      <h4 class="project-title">{{ project.title }}</h4>
      <div class="location-badge">
        <span class="flag-icon" v-html="qatarFlagSvg" />
        <span>{{ locationLabel }}</span>
      </div>

      <div class="funding-block">
        <div class="funding-row">
          <span class="paid-label">{{ t('donation.partiallyFundedLabel') }} {{ formatAmount(project.donated_amount) }}</span>
          <span class="percentage-label">{{ coveragePercentage }}%</span>
        </div>
        <div class="progress-bar-container">
          <div class="progress-bar-fill" :class="{ 'fully-funded': coveragePercentage >= 100 }" :style="{ width: animatedWidth + '%' }" />
        </div>
        <div class="target-line">
          {{ t('donation.targetAmount') }} {{ formatAmount(project.required_amount) }} {{ t('donation.currency') }}
        </div>
      </div>

      <div class="divider" />

      <div class="actions-row">
        <button type="button" class="primary-btn" @click="openDonationDialog(project)">
          {{ t('donation.donateNow') }}
        </button>
        <router-link :to="{ name: 'DonationProject', params: { name: project.name } }" class="secondary-btn">
          {{ t('donation.detail.details') }}
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useLanguage } from '@/composables/useLanguage'
import { useDonationDialog } from '@/composables/useDonationDialog'
import { qatarFlagSvg } from '@/config/donationIcons'

const props = defineProps({
  project: { type: Object, required: true },
})

const { t, isRTL } = useLanguage()
const { openDonationDialog } = useDonationDialog()

const coveragePercentage = computed(() => Math.min(Math.round(props.project.percentage || 0), 100))

// Starts at 0 and animates up to the real percentage once mounted, so the
// progress bar fills in on page load instead of appearing pre-filled.
const animatedWidth = ref(0)
onMounted(() => {
  requestAnimationFrame(() => {
    animatedWidth.value = coveragePercentage.value
  })
})

const locationLabel = computed(() =>
  props.project.location === 'outside_qatar' ? t('donation.location.outsideQatar') : t('donation.location.insideQatar')
)

function formatAmount(value) {
  return new Intl.NumberFormat('en-US').format(Math.round(value || 0))
}

async function share() {
  const url = `${window.location.origin}/donate/project/${props.project.name}`
  if (navigator.share) {
    try {
      await navigator.share({ title: props.project.title, url })
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
.project-card {
  @apply flex-none w-[260px] sm:w-[316px] flex flex-col overflow-hidden;
  background: #f8fafc;
  border: 1px solid rgba(189, 200, 209, 0.2);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  border-radius: 12px;
  scroll-snap-align: start;
}

.card-image {
  @apply relative w-full shrink-0;
  aspect-ratio: 314 / 224;
  background: linear-gradient(359.92deg, rgba(0, 173, 239, 0.2) 0.07%, rgba(255, 255, 255, 0.2) 99.93%), #e6eff8;
}

.card-image img {
  @apply w-full h-full object-cover absolute inset-0;
}

.share-btn {
  @apply absolute w-8 h-8 sm:w-10 sm:h-10 flex items-center justify-center rounded-full transition-colors hover:bg-sky-50;
  top: 12px;
  inset-inline-end: 12px;
  background: #ffffff;
  border: 1px solid #d3d3d3;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  color: #0570b6;
}

@media (min-width: 640px) {
  .share-btn {
    top: 15px;
    inset-inline-end: 15px;
  }
}

.card-body {
  @apply flex flex-col items-start;
  padding: 18px 16px;
}

@media (min-width: 640px) {
  .card-body {
    padding: 24px 20px;
  }
}

.project-title {
  font-weight: 700;
  font-size: 16px;
  line-height: 20px;
  color: #141d23;
  margin-bottom: 5.5px;
}

@media (min-width: 640px) {
  .project-title {
    font-size: 18px;
    line-height: 22px;
  }
}

.location-badge {
  @apply flex items-center gap-1.5;
  font-size: 14px;
  color: #64748b;
  margin-bottom: 10px;
}

@media (min-width: 640px) {
  .location-badge {
    font-size: 16px;
    margin-bottom: 12px;
  }
}

.flag-icon {
  @apply inline-flex w-[15px] h-[15px] sm:w-[18px] sm:h-[18px] shrink-0;
}

.funding-block {
  @apply flex flex-col gap-2 w-full;
}

.funding-row {
  @apply flex items-center justify-between;
}

.percentage-label {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.28px;
  color: #141d23;
}

.paid-label {
  font-size: 13px;
  color: #6b7280;
}

.target-line {
  font-size: 13px;
  color: #6b7280;
}

@media (min-width: 640px) {
  .percentage-label,
  .paid-label,
  .target-line {
    font-size: 14px;
  }
}

.progress-bar-container {
  @apply flex overflow-hidden;
  background: #dbe4ed;
  border-radius: 9999px;
  height: 8px;
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

.divider {
  border-top: 1px solid #dbe4ed;
  @apply w-full my-4 sm:my-5;
}

.actions-row {
  @apply flex items-center gap-2 sm:gap-3 w-full;
}

.secondary-btn {
  @apply flex-1 h-9 sm:h-10 flex items-center justify-center text-xs sm:text-sm font-medium transition-colors hover:bg-sky-50 whitespace-nowrap;
  background: #ffffff;
  border: 1px solid #d3d3d3;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  border-radius: 12px;
  color: #0570b6;
}

.primary-btn {
  @apply flex-1 h-9 sm:h-10 flex items-center justify-center text-xs sm:text-sm font-medium text-white transition-opacity hover:opacity-90 whitespace-nowrap border-none;
  background: #00adef;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  border-radius: 12px;
}
</style>
