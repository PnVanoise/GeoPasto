<template>
  <h1>Composant AboutView2</h1>
  <p>
    Composant parent. Définit un quartierUP (multipolygone, geojson), et affiche un
    composant MapEditMultiPolygon
  </p>
  <p>
    {{ quartierUP.geometry }}
  </p>
  <!-- <MapEditMultipolygon2 v-model="quartierUP.geometry" :key="mapKey" /> -->
  <MapEditMultipolygon :quartierUP="quartierUP" :key="mapKey" />
</template>

<script setup>
import { ref } from "vue";
import MapEditMultipolygon from "../components/MapEditMultipolygon.vue";

const mapKey = ref(0);
const quartierUP = ref(null);

quartierUP.value = {
  id: 4,
  type: "Feature",
  geometry: {
    type: "MultiPolygon",
    coordinates: [
      [
        [
          [6.635055541992188, 45.485470029442745],
          [6.806030273437501, 45.485470029442745],
          [6.788177490234376, 45.46091325991065],
        ],
      ],
      [
        [
          [6.855468750000001, 45.47921147686957],
          [7.042922973632813, 45.48450722045331],
          [7.147979736328126, 45.41128558787871],
          [7.028503417968751, 45.46091325991065],
        ],
      ],
    ],
  },
  properties: {
    quartier_code: "UP7304703_4",
    surface: 192.234955998175,
    up_code: "UP7304703",
    up_nom_1: "LES LESCHANS",
    up_nom_2: "SOURCES DE L ARC",
    quartier_code_court: "Q4",
    quartier_nom: "Sources de l'Arc",
  },
};
</script>
