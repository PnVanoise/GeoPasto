<template>
  <div v-if="isLoading" class="w3-center">
    <img src="/spinner_2.gif" />
  </div>
  <div v-else class="main-container">
    <div class="main-item">
      <div class="w3-container">
        <h2 class="w3-left">Liste des unités pastorales</h2>
        <span class="w3-button w3-right" @click="goToAddPage">Ajouter une UP</span>
      </div>
      <div v-if="quartierUPs">
        <div class="w3-container liste-container">
          <ul class="w3-ul w3-card-4">
            <li v-for="quartierUP in quartierUPs.features" :key="quartierUP.id"
              @click="centerOnMap(quartierUP.geometry.coordinates)">
              <span class="w3-bar-item w3-button w3-white w3-right"
                @click.stop="deleteQuartierUP(quartierUP.id)">Supprimer</span>
              <span class="w3-bar-item w3-button w3-white w3-right"
                @click.stop="editQuartierUP(quartierUP.id)">Détails</span>
              <div class="w3-bar-item">
                <span class="w3-large">{{ quartierUP.properties.quartier_code }}</span><br />
                <span>{{ quartierUP.properties.quartier_nom }}</span>
              </div>
            </li>
          </ul>
        </div>
      </div>
      <div v-else>Aucune donnée disponible.</div>
    </div>
    <div class="main-item">
      <MapContainer v-model="mapRef">
        <BaseLayersControl :map="mapRef" />
        <GeoJsonLayer :map="mapRef" :geoData="quartierUPs" geoObjectName="quartierUP" :style="layerStyle"
          popupRoute="/quartiers/details" geomType="Polygon" />
        <LegendControl :map="mapRef" :legendHtml="legendContent" />
        <InfoControl :map="mapRef"
          infoContent="<h4>Informations sur la carte</h4><p>Détails supplémentaires ici.</p>" />
      </MapContainer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import auth from "../../auth";
import MapContainer from './ListMap/MapContainer.vue';
import BaseLayersControl from './ListMap/BaseLayersControl.vue';
import GeoJsonLayer from './ListMap/GeoJsonLayer.vue';
import LegendControl from './ListMap/LegendControl.vue';
import InfoControl from './ListMap/InfoControl.vue';
import config from "../../config";

const quartierUPs = ref([]);
const isLoading = ref(true);
const mapRef = ref(null); // La carte sera référencée ici
const router = useRouter();

// Définir le style pour tes couches Leaflet
const layerStyle = {
  color: 'green',
  weight: 2,
  fillOpacity: 0.7,
};

// Convertir les propriétés de `layerStyle` en styles CSS
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
    <h4>Légende des quartiers</h4>
    <p><span style="${symbolStyle}"></span> Quartier UP</p>
    <p><span style="background-color: blue; border: 2px solid blue; width: 20px; height: 20px; display: inline-block;"></span> Quartier UP 2</p>
    <p><span style="background-color: red; border: 2px solid red; width: 20px; height: 20px; display: inline-block;"></span> Quartier Prioritaire</p>
  </div>
`;

const fetchquartierUPs = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/quartierUP/`)
    .then((response) => {
      quartierUPs.value = response.data;
      console.log("list response data:", response.data);
    })
    .catch((error) => {
      console.error("There was an error!", error);
    })
    .finally(() => {
      isLoading.value = false;
    });
};

const goToAddPage = () => {
  router.push("/Alpage/add");
};

const editQuartierUP = (id) => {
  router.push(`/Alpage/edit/${id}`);
};

const deleteQuartierUP = (id) => {
  auth.axiosInstance
    .delete(`${config.API_BASE_URL}/api/quartierUP/${id}/`)
    .then(() => {
      fetchquartierUPs();
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

const centerOnMap = (coordinates) => {
  if (mapRef.value && coordinates) {
    // Fonction pour centrer la carte sur l'unité sélectionnée
    const latLng = L.latLng(coordinates[1], coordinates[0]);
    mapRef.value.setView(latLng, 13);
  }
};

onMounted(fetchquartierUPs);
</script>

<style scoped>
.main-container {
  display: grid;
  grid-template-columns: 40% 60%;
}

.main-item {
  padding: 20px;
  margin: 10px;
  text-align: center;
}

.liste-container {
  max-height: 600px;
  overflow-y: auto;
}
</style>
