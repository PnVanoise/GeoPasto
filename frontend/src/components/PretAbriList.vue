<template>
  <div v-if="isLoading" class="w3-center">
    <img src="/spinner_2.gif" />
  </div>
  <div v-else class="main-container-one">
    <div class="main-item">
      <div class="w3-container">
        <h2 class="w3-center">Liste des prêts d'abri</h2>
      </div>
      <div v-if="prets">
        <div class="header-actions">
          <form id="search" class="search-form">
            Rechercher <input name="query" v-model="searchQuery" />
          </form>
          <span class="w3-button add-up" @click="goToAddPage">
            <font-awesome-icon icon="plus" /> Ajouter un prêt d'abri
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
            @delete="onDelete"
            @view="onView"
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
          v-if="mapRef"
          :map="mapRef"
          :geoData="prets"
          geoObjectName="unitePastorale"
          :mPolygonStyle="layerStyle"
          popupRoute="/PretAbri/edit"
          geomType="Point"
          iconFile="marqueur_bleu.png"
          iconHighlightFile="marqueur_rouge.png"
          objectLib="Abri d'urgence"
          popupAttribute="exploitant.nom_exploitant"
        />
      </MapContainer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

import auth from "../../auth";

import config from "../../config";
import { useMainStore } from "../store";

import Grid from "./Grid.vue";
import MapContainer from "./ListMap/MapContainer.vue";
import BaseLayersControl from "./ListMap/BaseLayersControl.vue";
import GeoJsonLayer from "./ListMap/GeoJsonLayer.vue";

const prets = ref([]);
const features = ref([]); // Données pour la grille (à plat : id et properties)

const isLoading = ref(true);
const mapRef = ref(null);
const router = useRouter();
const mainStore = useMainStore();

const searchQuery = ref("");
const gridColumns = ref(["exploitant_nom", "abri_description"]);
const columnLabels = ref({
  exploitant_nom: "Exploitant",
  abri_description: "Abri",
});

const fetchPrets = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/beneficierDe/`)
    .then((response) => {
      prets.value = response.data;
      console.log("list response data:", response.data);
      console.log("beneficierde.value:", prets.value);
      if (prets.value.type === "FeatureCollection") {
        // Transformer les features en tableau
        features.value = prets.value.features.map((feature) => {
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
      console.log("fetchPrets done");
    });
};

const goToAddPage = () => {
  console.log("Ajouter un prêt");
  router.push("/PretAbri/add");
};

// Méthode pour gérer l'édition
function onEdit(entry) {
  console.log("Éditer:", entry);
  router.push(`/PretAbri/edit/${entry.id}`);
}

// Méthode pour gérer l'affichage
function onView(entry) {
  console.log("View:", entry);
  router.push({
    path: `/PretAbri/edit/${entry.id}`,
    query: { readonly: 'true'}
  });
}

// Méthode pour gérer la suppression
function onDelete(entry) {
  console.log("Supprimer:", entry.id);
  deletePret(entry.id);
}

const deletePret = (id) => {
  auth.axiosInstance
    .delete(`${config.API_BASE_URL}/api/beneficierDe/${id}/`)
    .then((response) => {
      fetchPrets();
      mainStore.setSuccessMessage("Prêt supprimé!");
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

onMounted(fetchPrets);

import L from "leaflet";

const addZoomDisplayControl = (map) => {
  const zoomLabel = L.control({ position: "topleft" });

  zoomLabel.onAdd = function () {
    const div = L.DomUtil.create("div", "leaflet-zoom-label");
    div.innerHTML = `Zoom : ${map.getZoom()}`;

    map.on("zoomend", () => {
      div.innerHTML = `Zoom : ${map.getZoom()}`;
    });

    return div;
  };

  zoomLabel.addTo(map);
};

import { watch } from "vue";

watch(mapRef, (map) => {
  if (map) {
    addZoomDisplayControl(map);
  }
});

</script>

<style scoped>
.title-container {
  display: flex;
  align-items: center;
}

.loading-image {
  margin-right: 10px;
}

.main-container-one {
  display: grid;
  grid-template-columns: 100%;
}

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

.leaflet-zoom-label {
  background-color: white;
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  box-shadow: 0 1px 4px rgba(0,0,0,0.3);
}
/* Ajoutez vos styles ici */
</style>
