<template>
  <div v-if="isLoading" class="w3-center">
    <img src="/spinner_2.gif" />
  </div>
  <div v-else class="main-container">
    <div class="main-item">
      <div class="w3-container">
        <h2 class="w3-center">Liste des logements</h2>
      </div>
      <div v-if="logements">
        <div class="header-actions">
          <form id="search" class="search-form">
            Rechercher <input name="query" v-model="searchQuery" />
          </form>
          <span class="w3-button add-up" @click="goToAddPage">
            <font-awesome-icon icon="plus" /> Ajouter logement
          </span>
        </div>
        <div class="grid-container">
          <Grid
            :data="logementsWithDesc"
            :columns="gridColumns"
            :filter-key="searchQuery"
            :bgColor="'#005187'"
            :columnLabels="columnLabels"
            @edit="onEdit"
            @delete="onDelete"
          >
          </Grid>
        </div>
      </div>
      <div v-else>Aucune donnée disponible.</div>
    </div>
    <div class="main-item">
      <h2>Où les trouve-t-on ?</h2>
      <MapContainer v-model="mapRef">
        <BaseLayersControl :map="mapRef" />
        <GeoJsonLayer
          :map="mapRef"
          :geoData="logements"
          geoObjectName="logement"
          :style="layerStyle"
          popupRoute="/logement/edit"
          geomType="Point"
          iconFile="marqueur_bleu.png"
          iconHighlightFile="marqueur_rouge.png"
          objectLib="Logement"
        />
        <!-- <LegendControl :map="mapRef" :legendHtml="legendContent" /> -->
      </MapContainer>
      <!-- <MapList
        geoObjectName="logement"
        :style="logementStyle"
        popupRoute="/Logement"
        geomType="Point"
        :legendInnerHtml="legendHtml"
      /> -->
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";

import auth from "../../auth";

import Grid from "./Grid.vue";
import MapContainer from "./ListMap/MapContainer.vue";
import BaseLayersControl from "./ListMap/BaseLayersControl.vue";
import GeoJsonLayer from "./ListMap/GeoJsonLayer.vue";

import config from "../../config";

const logements = ref([]);

const isLoading = ref(true);
const mapRef = ref(null);
const router = useRouter();

const searchQuery = ref("");
const gridColumns = ref(["logement_code", "nom_logement", "nom_up", "statut"]);
const columnLabels = ref({
  logement_code: "Code",
  nom_logement: "Nom",
  nom_up : "UP",
  statut: "Statut",
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
    <p>Légende des logements</p>
    <p><span style="${symbolStyle}"></span> Logement</p>
  </div>
`;

console.log("symbolStyle:", symbolStyle);

const logementsWithDesc = computed(() => {
  console.log("features: ", features.value);
  return features.value.map(exp => ({
    ...exp,
    nom_up: exp.unite_pastorale_detail?.nom_up || "",
  }));
});

const fetchLogements = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/logement/`)
    .then((response) => {
      logements.value = response.data;
      console.log("list response data:", response.data);
      console.log("logements.value:", logements.value);

      if (logements.value.type === "FeatureCollection") {
        // Transformer les features en tableau
        features.value = logements.value.features.map((feature) => {
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
      console.log("fetchLogements done");
    });
};

const goToAddPage = () => {
  router.push("/Logement/add");
};

// Méthode pour gérer l'édition
function onEdit(entry) {
  console.log("Éditer:", entry.id);

  router.push(`/Logement/edit/${entry.id}`);
}

// Méthode pour gérer la suppression
function onDelete(entry) {
  console.log("Supprimer:", entry.id);
  deleteLogement(entry.id);
}

const deleteLogement = (id) => {
  auth.axiosInstance
    .delete(`${config.API_BASE_URL}/api/logement/${id}/`)
    .then((response) => {
      fetchLogements();
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

onMounted(fetchLogements);
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
