<template>
  <div>
    <h1>Ajouter un quartier</h1>
    <QuartierPastoForm :initialForm="form" :isEdit="false" :onSubmit="submitForm" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

import auth from "../../auth";

import QuartierPastoForm from "./QuartierPastoForm.vue";
import config from "../../config";
import { useMainStore } from "../store";

const route = useRoute();

const form = ref({
  properties: {
    code_quartier: "",
    nom_quartier: "",
    unite_pastorale: route.params.UPId || "",
  },
  geometry: {
    type: "Polygon",
    coordinates: [],
  },
});

const router = useRouter();
const mainStore = useMainStore();

const submitForm = async (formData) => {
  try {
    const response = await auth.axiosInstance.post(
      `${config.API_BASE_URL}/api/quartierPasto/`,
      formData
    );
    console.log("Form successfully submitted, response:", response);

    // Afficher un message de succès
    mainStore.setSuccessMessage("Quartier ajouté avec succès!");

    // Vérifier si le message est bien défini dans le store
    console.log("Success message set:", mainStore.successMessage);

    // Ajouter un petit délai pour vérifier l'affichage du message avant la redirection
    setTimeout(() => {
      router.push("/QuartierPastos");
    }, 500); // Petit délai pour s'assurer que le message est vu
  } catch (error) {
    mainStore.setErrorMessage(
      "Une erreur s'est produite lors de l'ajout du quartier." + error
    );
    console.error("There was an error!", error);
  }
};
</script>

<style scoped></style>
