<template>
  <div v-if="isLoading" class="w3-center">
    <img src="/spinner_2.gif" />
  </div>
  <div v-else class="main-container">
    <div class="main-item">
      <CrudList2
        title="Unités pastorales"
        modelName="unitepastorale"
        apiRouteName="unitePastorale"
        :geojsonMode="true"
        itemLabel="une unité pastorale"
        idField="id"
        :columns="columns"
        :formComponent="UnitePastoraleForm2"
        :bgColor="'#808080'"
      />
    </div>
    <div class="main-item">
      <h2>Où les trouve-t-on ?</h2>
      <div class="maps-stack">
        <section class="map-section">
          <h3>Carte Leaflet (historique git)</h3>
          <MapContainer v-model="mapRef">
            <BaseLayersControl :map="mapRef" />
            <GeoJsonLayer
              v-if="mapRef && unitepastorales?.features?.length"
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
        </section>

        <section class="map-section">
          <h3>Carte OpenLayers (branche feat/frontend-openalyers-map)</h3>
          <OpenLayersGeoJsonMap
            :geoData="unitepastorales"
            :mPolygonStyle="layerStyle"
            popupRoute="/UnitePastorale/edit"
            popupAttribute="nom_up"
            @open-popup-item="onMapPopupItem"
          />
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";

import OpenLayersGeoJsonMap from "./ListMap/OpenLayersGeoJsonMap.vue";
import MapContainer from "./ListMap/MapContainer.vue";
import BaseLayersControl from "./ListMap/BaseLayersControl.vue";
import GeoJsonLayer from "./ListMap/GeoJsonLayer.vue";

import config from "../../config";

import auth from "../../auth";
import UnitePastoraleForm2 from "./UnitePastoraleForm2.vue";
import CrudList2 from "./CrudList2.vue";

const columns = [
  { field: "nom_up", label: "UP", sortable: true },
  { field: "annee_version", label: "Année", sortable: true },
];

const isLoading = ref(true);
const mapRef = ref(null);
const router = useRouter();

// Data --> props
// Zone de recherche et grille

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
      // if (unitepastorales.value.type === "FeatureCollection") {
      //   // Transformer les features en tableau
      //   features.value = unitepastorales.value.features.map((feature) => {
      //     return {
      //       ...feature.properties, // Ajoute toutes les propriétés
      //       id: feature.id, // Ajoute l'id
      //     };
      //   });
      // }
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

const onMapPopupItem = (payload) => {
  const id = payload?.id;
  if (!id) return;

  try {
    window.dispatchEvent(new CustomEvent("crud-open-view", {
      detail: {
        modelName: "unitepastorale",
        id,
      },
    }));
  } catch (err) {
    console.warn("Could not dispatch crud-open-view event", err);
  }
};

onMounted(fetchUnitePastorales);

// Refresh when other components notify that geo data changed
const onGeoDataChanged = (e) => {
  try {
    const model = e?.detail?.modelName;
    if (!model || model === 'unitepastorale') fetchUnitePastorales();
  } catch (err) {
    fetchUnitePastorales();
  }
};

window.addEventListener('geo-data-changed', onGeoDataChanged);

onBeforeUnmount(() => {
  window.removeEventListener('geo-data-changed', onGeoDataChanged);
});
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

.maps-stack {
  display: grid;
  gap: 24px;
}

.map-section h3 {
  margin-bottom: 12px;
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
