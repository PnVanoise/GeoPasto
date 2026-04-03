<template>
  <div v-if="isLoading" class="w3-center">
    <img src="/spinner_2.gif" />
  </div>
  <div v-else class="main-container-one">
    <div class="main-item">
      <div class="w3-container">
        <h2 class="w3-left">Liste des équipements d'alpage</h2>
        <span class="w3-button w3-right" @click="goToAddPage">Ajouter un équipement</span>
      </div>
      <div v-if="equipements">
        <div class="w3-container liste-container">
          <ul class="w3-ul w3-card-4">
            <li v-for="equipement in equipements.features" :key="equipement.id">
              <span
                class="w3-bar-item w3-button w3-white w3-right"
                @click="deleteEquipement(equipement.id)"
                >Supprimer</span
              >
              <span
                class="w3-bar-item w3-button w3-white w3-right"
                @click="editEquipement(equipement.id)"
                >Détails</span
              >
              <div class="w3-bar-item">
                <span class="w3-large">{{ equipement.id }}</span
                ><br />
                <span>{{ equipement.properties.information_complementaire }}</span>
              </div>
            </li>
          </ul>
        </div>
      </div>
      <div v-else>Aucune donnée disponible.</div>
    </div>
    <!-- <div class="main-item">
            <MapList geoObjectName="quartierUP" :style="quartierUPStyle" popupRoute="/Alpage" :legendInnerHtml="legendHtml"/>
        </div> -->
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "../services/axios";
// import MapList from './MapList.vue';
import config from "../../config";

const equipements = ref([]);
const isLoading = ref(true);
const router = useRouter();

const fetchEquipements = () => {
  axios
    .get(`${config.API_BASE_URL}/api/eqptAA/`)
    .then((response) => {
      equipements.value = response.data;
      console.log("list response data:", response.data);
      console.log("quartierUPs.value:", equipements.value);
    })
    .catch((error) => {
      console.error("There was an error!", error);
    })
    .finally(() => {
      isLoading.value = false;
      console.log("fetchequipements done");
    });
};

const goToAddPage = () => {
  router.push("/Equipement/add");
};

const editEquipement = (id) => {
  router.push(`/Equipement/edit/${id}`);
};

const deleteEquipement = (id) => {
  axios
    .delete(`${config.API_BASE_URL}/api/eqptAA/${id}/`)
    .then((response) => {
      fetchEquipements();
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

onMounted(fetchEquipements);
</script>

<style scoped>
.main-container-one {
  display: grid;
  grid-template-columns: 100%;
}

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
