<template>
  <div>
    <h1>Éditer une ruche</h1>
    <RucheForm :initialForm="form" :isEdit="true" :onSubmit="submitForm" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";

import auth from "../../auth";
import config from "../../config";
import { useMainStore } from "../store";

import RucheForm from "./RucheForm.vue";

const form = ref({
  properties: {
    description: "",
    situation_exploitation: "",
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

const fetchRuche = () => {
  console.log("fetchRuche");
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/ruche/${id}/`)
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
      `${config.API_BASE_URL}/api/ruche/${id}/`,
      formData
    );
    mainStore.setSuccessMessage("Ruche modifiée!");
    router.push("/Ruches");
  } catch (error) {
    mainStore.setErrorMessage("Erreur d'enregistrement de la ruche.");
    console.error("Ruche submitForm error: ", error);
  }
};

console.log("Before onMounted");
onMounted(() => {
  console.log("Inside onMounted");
  fetchRuche();
});
</script>

<style scoped>
/* Ajoutez vos styles ici */
</style>
