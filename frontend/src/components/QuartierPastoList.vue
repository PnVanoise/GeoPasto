<template>
  <div v-if="isLoading" class="w3-center">
    <img src="/spinner_2.gif" />
  </div>
  <div v-else class="main-container">
    <div class="main-item">
      <div class="w3-container">
        <h2 v-if="up_id" class="w3-center">Liste des quartiers de l'UP {{ up_name }}</h2>
        <h2 v-else class="w3-center">Liste des quartiers</h2>
      </div>
      <div v-if="quartierPastos">
        <div class="header-actions">
          <form id="search" class="search-form">
            Rechercher <input name="query" v-model="searchQuery" />
          </form>
          <span class="w3-button add-up" @click="goToAddPage">
            <font-awesome-icon icon="plus" /> Ajouter un quartier
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
          :geoData="quartierPastos"
          geoObjectName="quartierPasto"
          :mPolygonStyle="layerStyle"
          popupRoute="/QuartierPasto/edit"
          geomType="Polygon"
          objectLib="Quartier"
          popupAttribute="nom_quartier"
        />
      </MapContainer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";

import Grid from "./Grid.vue";
import MapContainer from "./ListMap/MapContainer.vue";
import BaseLayersControl from "./ListMap/BaseLayersControl.vue";
import GeoJsonLayer from "./ListMap/GeoJsonLayer.vue";

import config from "../../config";
import auth from "../../auth";

const isLoading = ref(true);
const mapRef = ref(null);
const router = useRouter();

const route = useRoute();

const up_id = route.params.up_id;
const up_name = ref("");

// Data --> props
// Zone de recherche et grille
const searchQuery = ref("");
const gridColumns = ref(["code_quartier", "nom_quartier", "unitepastorale_nom"]);
const columnLabels = ref({
  code_quartier: "Code",
  nom_quartier: "Nom",
  unitepastorale_nom: "Unité pastorale",
});
const features = ref([]); // Données pour la grille (à plat : id et properties)
// GeoJSONLayer
const quartierPastos = ref([]); // Features GeoJSON pour la carte
// Style de la couche
const layerStyle = {
  color: "#008080",
  weight: 2,
  fillOpacity: 0.3,
};

const fetchQuartiers = async (upID = null) => {
  const params = upID ? { up_id: upID } : {};
  try {
    const response = await auth.axiosInstance.get(
      `${config.API_BASE_URL}/api/quartierPasto/`,
      { params }
    );
    quartierPastos.value = response.data;

    console.log("list response data:", response.data);
    console.log("quartierpastos.value:", quartierPastos.value);
    if (quartierPastos.value.type === "FeatureCollection") {
      // Transformer les features en tableau
      features.value = quartierPastos.value.features.map((feature) => {
        return {
          ...feature.properties, // Ajoute toutes les propriétés
          id: feature.id, // Ajoute l'id
        };
      });
    }
    if (upID) {
      console.log("upID : ", upID);
      const upResponse = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/unitePastorale/${upID}/`
      );
      console.log("upResponse : ", upResponse.data.properties.nom_up);

      up_name.value = upResponse.data.properties.nom_up;
    }
  } catch (error) {
    console.error("There was an error!", error);
  } finally {
    isLoading.value = false;
    console.log("fetchUPs done");
  }
};

const goToAddPage = () => {
  console.log("Ajout d'une unité pastorale");
  router.push("/QuartierPasto/add");
};

// Méthode pour gérer l'édition
function onEdit(entry) {
  console.log("Éditer:", entry.id);

  router.push(`/QuartierPasto/edit/${entry.id}`);
}

// Méthode pour gérer la suppression
function onDelete(entry) {
  console.log("Supprimer:", entry.id);
  deleteQuartier(entry.id);
}

const deleteQuartier = (id) => {
  auth.axiosInstance
    .delete(`${config.API_BASE_URL}/api/quartierPasto/${id}/`)
    .then((response) => {
      fetchQuartiers();
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

onMounted(() => {
  fetchQuartiers(up_id); // Passe `up_id` comme paramètre à `fetchQuartiers`
});

// onMounted(fetchQuartiers);
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
