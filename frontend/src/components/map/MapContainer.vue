<template>
  <div id="map-container">
    <div id="map"></div>
    <slot></slot>
    <!-- Le slot permet d'insérer des composants supplémentaires -->
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Props pour recevoir la carte depuis le parent
const props = defineProps({
  modelValue: Object, // La carte sera synchronisée via v-model
});

// Émettre l'événement pour synchroniser la carte avec le parent
const emit = defineEmits(["update:modelValue"]);

const map = ref(null);

onMounted(() => {
  // Initialiser la carte
  map.value = L.map("map", {
    zoom: 10,
    zoomControl: false,
    zoomAnimation: false,
  });

  // Ajouter la couche de base
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map.value);

  // Ajouter les contrôles de zoom et d'échelle
  L.control.zoom({ position: "topright" }).addTo(map.value);
  L.control.scale({ imperial: false, position: "bottomright" }).addTo(map.value);

  // Émettre l'objet map après son initialisation
  emit("update:modelValue", map.value);
});

// Synchroniser la carte si elle est mise à jour depuis le parent
watch(
  () => props.modelValue,
  (newMap) => {
    if (newMap !== map.value) {
      map.value = newMap;
      // Si nécessaire, réinitialiser la vue de la carte ou d'autres propriétés
    }
  }
);
</script>

<style>
#map {
  width: 100%;
  height: 600px;
}
</style>
