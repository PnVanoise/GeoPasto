<template>
  <div>
    <h1>Ajouter un événement</h1>
    <EvenementForm :initialForm="form" :isEdit="false" :onSubmit="submitForm" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

import auth from "../../auth";

import config from "../../config";
import { useMainStore } from "../store";
import EvenementForm from "./EvenementForm.vue";

const form = ref({
  id: "",
  properties: {
    date_evenement: "",
    observateur: "",
    date_observation: "",
    source: "",
    description: "",
  },
  geometry: {
    type: "Point",
    coordinates: [],
  },
});

const router = useRouter();
const mainStore = useMainStore();

const submitForm = async (formData) => {
  try {

    // Vérifier si les coordonnées sont vides
    if (!formData.geometry.coordinates || formData.geometry.coordinates.length === 0) {
      mainStore.setErrorMessage("Veuillez renseigner les coordonnées avant de soumettre.");
      console.error("Les coordonnées sont vides.");
      return; // Bloquer la soumission
    }

    console.log("Form submitted:", formData);
    const response = await auth.axiosInstance.post(
      `${config.API_BASE_URL}/api/evenement/`,
      formData
    );
    console.log("Form successfully submitted, response:", response);

    // Afficher un message de succès
    mainStore.setSuccessMessage("Evénement ajouté avec succès!");

    // Vérifier si le message est bien défini dans le store
    console.log("Success message set:", mainStore.successMessage);

    // Ajouter un petit délai pour vérifier l'affichage du message avant la redirection
    setTimeout(() => {
      router.push("/Evenements");
    }, 500); // Petit délai pour s'assurer que le message est vu
  } catch (error) {
    mainStore.setErrorMessage(
      "Une erreur s'est produite lors de l'ajout d'événement'." + error
    );
    console.error("There was an error!", error);
  }
};
</script>

<style scoped></style>
