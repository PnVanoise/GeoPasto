<template>
  <div v-if="isLoading" class="w3-center">
    <img src="/spinner_2.gif" />
  </div>
  <div v-else class="main-container">
    <div class="main-item">
      <div class="w3-container">
        <h2 class="w3-center">Liste des évènements</h2>
      </div>
      <div v-if="evenements">
        <div class="header-actions">
          <form id="search" class="search-form">
            Rechercher <input name="query" v-model="searchQuery" />
          </form>
          <span class="w3-button add-up" @click="goToAddPage">
            <font-awesome-icon icon="plus" /> Ajouter évènement
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
        <GeoJsonLayer :map="mapRef" :geoData="evenements" geoObjectName="evenement" :style="layerStyle"
          popupRoute="/evenement/edit" popupAttribute="description" geomType="Point" iconFile="marqueur_bleu.png"
          iconHighlightFile="marqueur_rouge.png" objectLib="Evenement" />
        <!-- <LegendControl :map="mapRef" :legendHtml="legendContent" /> -->
      </MapContainer>
      <!-- <MapList
        geoObjectName="evenement"
        :style="evenement"
        popupRoute="/Evenement"
        geomType="Point"
        :legendInnerHtml="legendHtml"
      /> -->
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

import auth from "../../auth";

import MapList from "./MapList.vue";
import Grid from "./Grid.vue";
import MapContainer from "./ListMap/MapContainer.vue";
import BaseLayersControl from "./ListMap/BaseLayersControl.vue";
import GeoJsonLayer from "./ListMap/GeoJsonLayer.vue";
import LegendControl from "./ListMap/LegendControl.vue";

import config from "../../config";

const evenements = ref([]);

const isLoading = ref(true);
const mapRef = ref(null);
const router = useRouter();

const searchQuery = ref("");
const gridColumns = ref(["date_evenement", "observateur", "date_observation", "source", "description"]);
const columnLabels = ref({
  description: "Description",
  date_evenement: "Date évènement",
  observateur: "Observateur",
  date_observation: "Date observation",
  source: "Source"
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
// Légende HTML avec le style appliqué aux symboles
const legendContent = `
  <div style="font-size: 14px;">
    <p>Légende des évènements</p>
    <p><span style="${symbolStyle}"></span> Evènement</p>
  </div>
`;

console.log("symbolStyle:", symbolStyle);

const evenementStyle = ref({
  radius: 8,
  fillColor: "#ff7800",
  color: "#000",
  weight: 1,
  opacity: 1,
  fillOpacity: 0.8,
});

const legendHtml = ref(null);
legendHtml.value = `
        <h4>Evènements<br>en coeur de Parc</h4>
        <i class="circle" style="background: rgba(255,120,0,0.8);"></i> Evènement
`;

const fetchEvenements = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/evenement/`)
    .then((response) => {
      evenements.value = response.data;
      console.log("list response data:", response.data);
      console.log("evenements.value:", evenements.value);

      if (evenements.value.type === "FeatureCollection") {
        // Transformer les features en tableau
        features.value = evenements.value.features.map((feature) => {
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
      console.log("fetchEvenements done");
    });
};

const goToAddPage = () => {
  router.push("/Evenement/add");
};

// Méthode pour gérer l'édition
function onEdit(entry) {
  console.log("Éditer:", entry.id);

  router.push(`/Evenement/edit/${entry.id}`);
}

// Méthode pour gérer la suppression
function onDelete(entry) {
  console.log("Supprimer:", entry.id);
  deleteEvenement(entry.id);
}

const deleteEvenement = (id) => {
  auth.axiosInstance
    .delete(`${config.API_BASE_URL}/api/evenement/${id}/`)
    .then((response) => {
      fetchEvenements();
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

onMounted(fetchEvenements);
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
