<template>
  <div v-if="isLoading" class="w3-center">
    <img src="/spinner_2.gif" />
  </div>
  <div v-else class="main-container">
    <div class="main-item">
      <div class="w3-container">
        <h2 class="w3-center">Liste des unités pastorales</h2>
      </div>
      <div v-if="unitepastorales">
        <div class="header-actions">
          <form id="search" class="search-form">
            Rechercher <input name="query" v-model="searchQuery" />
          </form>
          <span class="w3-button add-up" @click="goToAddPage">
            <font-awesome-icon icon="plus" /> Ajouter une UP
          </span>
        </div>
        <div class="grid-container">
          <Grid
            :data="features"
            :columns="gridColumns"
            :filter-key="searchQuery"
            :bgColor="'#f7ba0b'"
            :columnLabels="columnLabels"
            @edit="onEdit"
            @view="onView"
            @delete="onDelete"
          >
          </Grid>
        </div>
      </div>
      <div v-else>Aucune donnée disponible.</div>
    </div>
    <div class="main-item">
      <!-- <MapList
        geoObjectName="unitePastorale"
        :style="quartierUPStyle"
        popupRoute="/UnitePastorale"
        :legendInnerHtml="legendHtml"
      /> -->

      <h2>Où les trouve-t-on ?</h2>
      <MapContainer v-model="mapRef">
        <BaseLayersControl :map="mapRef" />
        <GeoJsonLayer
          v-if="mapRef"
          :map="mapRef"
          :geoData="unitepastorales"
          geoObjectName="unitePastorale"
          :mPolygonStyle="layerStyle"
          popupRoute="/UnitePastorale/edit"
          geomType="Polygon"
          objectLib="Unité pastorale"
          popupAttribute="nom_up"
        />
      </MapContainer>
      <!-- <LegendControl :map="mapRef" :legendHtml="legendContent" /> -->
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

import MapList from "./MapList.vue";
import MapContainer from "./ListMap/MapContainer.vue";
import BaseLayersControl from "./ListMap/BaseLayersControl.vue";
import GeoJsonLayer from "./ListMap/GeoJsonLayer.vue";
import LegendControl from "./ListMap/LegendControl.vue";

import Grid from "./Grid.vue";
import config from "../../config";

import auth from "../../auth";

const isLoading = ref(true);
const mapRef = ref(null);
const router = useRouter();

// Data --> props
// Zone de recherche et grille
const searchQuery = ref("");
const gridColumns = ref(["nom_up", "annee_version"]);
const columnLabels = ref({
  nom_up: "Nom",
  annee_version: "Année",
});
const features = ref([]); // Données pour la grille (à plat : id et properties)
// GeoJSONLayer
const unitepastorales = ref([]); // Features GeoJSON pour la carte
// Style de la couche
const layerStyle = {
  color: "#008000",
  weight: 2,
  fillOpacity: 0.3,
};

const fetchUnitePastorales = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/unitePastorale/`)
    .then((response) => {
      unitepastorales.value = response.data;
      console.log("list response data:", response.data);
      console.log("unitepastorales.value:", unitepastorales.value);
      if (unitepastorales.value.type === "FeatureCollection") {
        // Transformer les features en tableau
        features.value = unitepastorales.value.features.map((feature) => {
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
      console.log("fetchUPs done");
    });
};

const goToAddPage = () => {
  router.push("/UnitePastorale/add");
};

// Méthode pour gérer l'édition
function onEdit(entry) {
  console.log("Éditer:", entry.id);

  router.push(`/UnitePastorale/edit/${entry.id}`);
}

function onView(entry) {
  console.log("View:", entry);
  router.push({
    path: `/UnitePastorale/edit/${entry.id}`,
    query: { readonly: 'true'}
  });
}

// Méthode pour gérer la suppression
function onDelete(entry) {
  console.log("Supprimer:", entry.id);
  deleteUP(entry.id);
}

const deleteUP = (id) => {
  auth.axiosInstance
    .delete(`${config.API_BASE_URL}/api/unitePastorale/${id}/`)
    .then((response) => {
      fetchUnitePastorales();
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

onMounted(fetchUnitePastorales);
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
  /* Arrondi des coins de la grille */
  overflow: hidden;
  /* Assure que le contenu s'adapte à l'arrondi */
}
</style>
