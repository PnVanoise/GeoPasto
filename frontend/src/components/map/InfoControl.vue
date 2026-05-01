<template>
  <div class="info-control">{{ infoText }}</div>
</template>

<script setup>
import { ref } from "vue";

const props = defineProps({
  map: Object,
});

const infoText = ref("Survolez une zone");

function updateInfo(newInfo) {
  infoText.value = newInfo ? `Quartier: ${newInfo}` : "Survolez une zone";
}
</script>

<style scoped>
.info-control {
  position: absolute;
  top: 10px;
  left: 10px;
  background: white;
  padding: 8px;
  border: 1px solid black;
}
</style>
