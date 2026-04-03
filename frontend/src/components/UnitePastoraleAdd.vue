<template>
  <div>
    <h1>Ajouter une Unité pastorale</h1>
    <UnitePastoraleForm :initialForm="form" :isEdit="false" :onSubmit="submitForm" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

import auth from "../../auth";

import UnitePastoraleForm from "./UnitePastoraleForm.vue";
import config from "../../config";
import { useMainStore } from "../store";

const form = ref({
  properties: {
    code_up: "",
    nom_up: "",
    secteur: "",
    annee_version: "",
    version_active: false,
  },
  geometry: {
    type: "MultiPolygon",
    coordinates: [],
  },
});

const router = useRouter();
const mainStore = useMainStore();

const submitForm = async (formData) => {
  try {
    const response = await auth.axiosInstance.post(
      `${config.API_BASE_URL}/api/unitePastorale/`,
      formData
    );
    console.log("Form successfully submitted, response:", response);

    // Afficher un message de succès
    mainStore.setSuccessMessage("Unité Pastorale ajoutée avec succès!");

    // Vérifier si le message est bien défini dans le store
    console.log("Success message set:", mainStore.successMessage);

    // Ajouter un petit délai pour vérifier l'affichage du message avant la redirection
    setTimeout(() => {
      router.push("/UnitePastorales");
    }, 500); // Petit délai pour s'assurer que le message est vu
  } catch (error) {
    mainStore.setErrorMessage(
      "Une erreur s'est produite lors de l'ajout de l'unité pastorale." + error
    );
    console.error("There was an error!", error);
  }
};
</script>

<style scoped></style>
