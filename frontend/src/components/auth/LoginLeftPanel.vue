<template>
  <div
    class="hidden md:flex md:w-1/2 items-center justify-center overflow-hidden"
    style="background: linear-gradient(180deg, #34B0EE 0%, #F5F5F5 100%);"
    aria-hidden="true"
  >
    <img
      :src="maskGroupImg"
      alt=""
      class="w-4/5 max-w-xs object-contain select-none pointer-events-none"
    />
  </div>
</template>

<script setup>
import maskGroupImg from '@/assets/images/Mask group.png'
</script>
