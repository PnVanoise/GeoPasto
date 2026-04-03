<template>
  <div>
    <h1>Ajouter une convention d'exploitation</h1>
    <ConventionForm :initialForm="form" :isEdit="false" :onSubmit="submitForm" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

import auth from "../../auth";

import config from "../../config";
import { useMainStore } from "../store";

import ConventionForm from "./ConventionForm.vue";

const form = ref({
  properties: {
    surface_location: "",
    surface_exploitable: "",
    date_debut: "",
    date_fin: "",
    effectif_bovin: "",
    effectif_ovin: "",
    effectif_caprin: "",
    effectif_porcin: "",
    debut_periode_expl: "",
    fin_periode_expl: "",
    up_nom: "",
    exploitant_nom: "",
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
      `${config.API_BASE_URL}/api/conventionExploitation/`,
      formData
    );
    console.log("Form successfully submitted, response:", response);

    // Afficher un message de succès
    mainStore.setSuccessMessage("Convention ajoutée avec succès!");

    // Vérifier si le message est bien défini dans le store
    console.log("Success message set:", mainStore.successMessage);

    // Ajouter un petit délai pour vérifier l'affichage du message avant la redirection
    setTimeout(() => {
      router.push("/Conventions");
    }, 500); // Petit délai pour s'assurer que le message est vu
  } catch (error) {
    mainStore.setErrorMessage(
      "Une erreur s'est produite lors de l'ajout de la convention." + error
    );
    console.error("There was an error!", error);
  }
};
</script>

<style scoped></style>
