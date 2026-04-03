<template>
  <div v-if="isLoading" class="w3-center">
    <img src="/spinner_2.gif" />
  </div>
  <div v-else class="main-container">
    <div class="main-item">
      <div class="w3-container">
        <h2 class="w3-center">Liste des ruches</h2>
      </div>
      <div v-if="ruches">
        <div class="header-actions">
          <form id="search" class="search-form">
            Rechercher <input name="query" v-model="searchQuery" />
          </form>
          <span class="w3-button add-up" @click="goToAddPage">
            <font-awesome-icon icon="plus" /> Ajouter ruche
          </span>
        </div>
        <div class="grid-container">
          <Grid :data="features" :columns="gridColumns" :filter-key="searchQuery" :bgColor="'#9b2423'"
            :columnLabels="columnLabels" @edit="onEdit" @delete="onDelete">
          </Grid>
        </div>
      </div>
      <div v-else>Aucune donnée disponible.</div>
    </div>
    <div class="main-item">
      <h2>Où les trouve-t-on ?</h2>
      <MapContainer v-model="mapRef">
        <BaseLayersControl :map="mapRef" />
        <GeoJsonLayer :map="mapRef" :geoData="ruches" geoObjectName="ruche" :style="layerStyle" popupRoute="/Ruche/edit"
          geomType="Point" iconFile="marqueur_bleu.png" iconHighlightFile="marqueur_rouge.png" objectLib="Ruche" />
      </MapContainer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

import auth from "../../auth";

import Grid from "./Grid.vue";
import MapContainer from "./ListMap/MapContainer.vue";
import BaseLayersControl from "./ListMap/BaseLayersControl.vue";
import GeoJsonLayer from "./ListMap/GeoJsonLayer.vue";

import config from "../../config";

const ruches = ref([]);

const isLoading = ref(true);
const mapRef = ref(null);
const router = useRouter();

const searchQuery = ref("");
const gridColumns = ref(["description"]);
const columnLabels = ref({
  description: "Description",
});
const features = ref([]);

const layerStyle = {
  radius: 8,
  fillColor: "#ff7800",
  color: "#000",
  weight: 1,
  opacity: 1,
  fillOpacity: 0.2,
};
// LegendControl
// Conversion de layerStyle en styles CSS
const symbolStyle = `
  background-color: ${layerStyle.color};
  border: ${layerStyle.weight}px solid ${layerStyle.color};
  opacity: ${layerStyle.fillOpacity};
  width: 20px;
  height: 20px;
  display: inline-block;
`;

console.log("symbolStyle:", symbolStyle);

// Méthode pour récupérer les données
const fetchRuches = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/ruche/`)
    .then((response) => {
      ruches.value = response.data;
      console.log("list response data:", response.data);
      console.log("ruches.value:", ruches.value);

      if (ruches.value.type === "FeatureCollection") {
        // Transformer les features en tableau
        features.value = ruches.value.features.map((feature) => {
          return {
            ...feature.properties, // Ajoute toutes les propriétés
            id: feature.id, // Ajoute l'id
          };
        });
      }
    })
    .catch((error) => {
      console.error("There was an error!", error);
    })
    .finally(() => {
      isLoading.value = false;
      console.log("fetchRuches done");
    });
};

const goToAddPage = () => {
  console.log("goToAddPage RUCHE");
  router.push("/Ruche/add");
};

// Méthode pour gérer l'édition
function onEdit(entry) {
  console.log("Éditer:", entry.id);
  router.push(`/Ruche/edit/${entry.id}`);
}

// Méthode pour gérer la suppression
function onDelete(entry) {
  console.log("Supprimer:", entry.id);
  deleteRuche(entry.id);
}

const deleteRuche = (id) => {
  auth.axiosInstance
    .delete(`${config.API_BASE_URL}/api/ruche/${id}/`)
    .then((response) => {
      fetchRuches();
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

onMounted(fetchRuches);
</script>

<style scoped>
.main-container {
  display: grid;
  grid-template-columns: 50% 50%;
}

.main-item {
  padding: 20px;
  margin: 10px;
  text-align: center;
}

/* Style pour aligner le formulaire de recherche et le bouton d'ajout */
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  margin-bottom: 10px;
  max-height: 30px;
}

/* Style pour le formulaire de recherche */
.search-form {
  display: inline-block;
}

/* Style pour le bouton d'ajout */
.add-up {
  background-color: #bdc3c7;
  color: 2c3e50;
  padding: 10px 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  border-radius: 5px;
}

.add-up:hover {
  background-color: #aab2b7;
}

/* Style pour l'input de recherche */
#search input {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.grid-container {
  border-radius: 5px;
  overflow: hidden;
}
</style>
