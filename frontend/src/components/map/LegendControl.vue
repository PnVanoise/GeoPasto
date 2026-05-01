<template>
  <!-- Pas de rendu dans le template, tout se fait dans le script -->
</template>

<script setup>
import { onMounted, watch } from "vue";
import L from "leaflet";

const props = defineProps({
  map: Object,
  legendHtml: String,
});

// Utilisation de onMounted pour s'assurer que le composant est monté avant d'ajouter la légende
onMounted(() => {
  if (props.map) {
    // Créez un contrôle de légende
    const legend = L.control({ position: "bottomleft" });

    // Fonction d'ajout de la légende
    legend.onAdd = function () {
      const div = L.DomUtil.create("div", "legend");
      div.innerHTML = props.legendHtml; // Injecte le HTML de la légende
      return div;
    };

    legend.addTo(props.map); // Ajoute la légende à la carte
  }
});

watch(
  () => props.map,
  (newMap) => {
    if (newMap) {
      // Retirer la légende de l'ancienne carte si elle existe
      newMap.eachLayer((layer) => {
        if (layer instanceof L.Control) {
          newMap.removeControl(layer);
        }
      });

      // Ajouter la légende à la nouvelle carte
      const legend = L.control({ position: "bottomleft" });

      legend.onAdd = function () {
        const div = L.DomUtil.create("div", "legend");
        div.innerHTML = props.legendHtml;
        return div;
      };

      legend.addTo(newMap);
    }
  }
);
</script>

<style scoped>
.legend {
  padding: 6px 8px;
  background: white;
  line-height: 24px;
  border: 1px solid black;
  border-radius: 4px;
  /* Ajout d'un peu de style */
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
  /* Ajout d'une ombre */
}
</style>
