<template>
  <div
    class="hidden md:flex md:w-1/2 items-center justify-center overflow-hidden"
    aria-hidden="true"
  >
    <img
      :src="logoImg"
      alt=""
      class="w-full h-full object-cover select-none pointer-events-none origin-right md:scale-95 lg:scale-100"
    />
  </div>
</template>

<script setup>
// import maskGroupImg from '@/assets/images/Mask group.png'
import logoImg from '@/assets/images/Artboard.png'
</script>
