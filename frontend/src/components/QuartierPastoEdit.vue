<template>
  <div>
    <h1>Éditer un quartier</h1>
    <QuartierPastoForm :initialForm="form" :isEdit="true" :onSubmit="submitForm" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";

import auth from "../../auth";

import { useMainStore } from "../store";

import config from "../../config";
import QuartierPastoForm from "./QuartierPastoForm.vue";

const form = ref({
  properties: {
    code_quartier: "",
    nom_quartier: "",
    unite_pastorale: "",
  },
  geometry: {
    type: "Point",
    coordinates: [], // Initialisation vide pour éviter la valeur null
  },
});

// Vérification et initialisation de la géométrie si elle est null
if (form.value.geometry === null) {
  form.value.geometry = { type: "Point", coordinates: [] };
}

const route = useRoute();
const id = route.params.id;

const router = useRouter();
const mainStore = useMainStore();

const fetchUP = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/quartierPasto/${id}/`)
    .then((response) => {
      console.log("response data : ", response.data);
      form.value.id = response.data.id;
      form.value.properties = response.data.properties;
      form.value.geometry = response.data.geometry;
      console.log("form properties : ", form.value);
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

const submitForm = async (formData) => {
  try {
    const response = await auth.axiosInstance.put(
      `${config.API_BASE_URL}/api/quartierPasto/${id}/`,
      formData
    );
    console.log("Form successfully submitted, response:", response);

    // Afficher un message de succès
    mainStore.setSuccessMessage("Quartier modifiée avec succès!");

    // Vérifier si le message est bien défini dans le store
    console.log("Success message set:", mainStore.successMessage);

    // Ajouter un petit délai pour vérifier l'affichage du message avant la redirection
    setTimeout(() => {
      router.push("/QuartierPastos");
    }, 500); // Petit délai pour s'assurer que le message est vu
  } catch (error) {
    mainStore.setErrorMessage(
      "Une erreur s'est produite lors de la modification du quartier." + error
    );
    console.error("There was an error!", error);
  }
};

onMounted(fetchUP);
</script>

<style scoped>
/* Ajoutez vos styles ici */
</style>
