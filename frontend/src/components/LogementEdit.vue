<template>
  <div>
    <h1>Éditer un logement</h1>
    <LogementForm :initialForm="form" :isEdit="true" :onSubmit="submitForm" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";

import auth from "../../auth";

import LogementForm from "./LogementForm.vue";

import config from "../../config";

import { useMainStore } from "../store";

const form = ref({
  properties: {
    logement_code: "",
    statut: "",
    acces_final: "",
    propriete: "",
    type_logement: "",
    multiusage: "",
    activite_laitiere: "",
    etat_batiment: "",
    accueil_public: "",
    mixite_possible: "",
    surface_logement: "",
    presence_douche: "",
    type_wc: "",
    alim_elec: "",
    alim_eau: "",
    origine_eau: "",
    qualite_eau: "",
    dispo_eau: "",
    assainissement: "",
    chauffe_eau: "",
    chauffage: "",
    stockage_indep: "",
  },
  geometry: {
    type: "Point",
    coordinates: [0, 0],
  },
});

const route = useRoute();
const router = useRouter();
const id = route.params.id;
const mainStore = useMainStore();

const fetchLogement = () => {
  console.log("fetchLogement");
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/logement/${id}/`)
    .then((response) => {
      console.log("Données reçues de l'API : ", response.data);

      if (response.data.geometry && response.data.geometry.coordinates) {
        form.value = response.data; // Assigner toutes les données
      } else {
        console.error("La géométrie est manquante ou invalide dans les données de l'API");
      }
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération du logement!", error);
    });
};

// const submitForm = (formData) => {
//   return auth.axiosInstance.put(`${config.API_BASE_URL}/api/logement/${id}/`, formData);
// };

const submitForm = async (formData) => {
  try {
    const response = await auth.axiosInstance.put(
      `${config.API_BASE_URL}/api/logement/${id}/`,
      formData
    );
    mainStore.setSuccessMessage("Logement modifié!");
    router.push("/Logements");
  } catch (error) {
    mainStore.setErrorMessage("Erreur d'enregistrement du logement.");
    console.error("Logement submitForm error: ", error);
  }
};

console.log("Before onMounted");
onMounted(() => {
  console.log("Inside onMounted");
  fetchLogement();
});
</script>

<style scoped>
/* Ajoutez vos styles ici */
</style>
