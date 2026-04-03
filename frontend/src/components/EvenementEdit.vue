<template>
  <div>
    <h1>Éditer un évènement</h1>
    <EvenementForm :initialForm="form" :isEdit="true" :onSubmit="submitForm" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";

import auth from "../../auth";

import EvenementForm from "./EvenementForm.vue";

import config from "../../config";

import { useMainStore } from "../store";

const form = ref({
  properties: {
    id_evenement: "",
    date_evenement: "",
    observateur: "",
    date_observation: "",
    source: "",
    description: "",
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

console.log("EVENEMENT EDIT");

const fetchEvenement = () => {
  console.log("fetchEvenement");
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/evenement/${id}/`)
    .then((response) => {
      console.log("Données reçues de l'API : ", response.data);

      form.value = response.data;

      console.log("form.value : ", form.value);
      // if (response.data.geometry && response.data.geometry.coordinates) {
      //   form.value = response.data; // Assigner toutes les données
      // } else {
      //   console.warn("La géométrie est manquante ou invalide dans les données de l'API");
      // }
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération de l'évènement!", error);
    });
};

// const submitForm = (formData) => {
//   return auth.axiosInstance.put(`${config.API_BASE_URL}/api/evenement/${id}/`, formData);
// };

const submitForm = async (formData) => {
  try {
    const response = await auth.axiosInstance.put(
      `${config.API_BASE_URL}/api/evenement/${id}/`,
      formData
    );
    mainStore.setSuccessMessage("Evènement modifié!");
    router.push("/Evenements");
  } catch (error) {
    mainStore.setErrorMessage("Erreur d'enregistrement de l'évènement.");
    console.error("Evènement submitForm error: ", error);
  }
};

console.log("Before onMounted");
onMounted(() => {
  console.log("Inside onMounted");
  fetchEvenement();
});
</script>

<style scoped>
/* Ajoutez vos styles ici */
</style>
