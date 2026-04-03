<template>
  <div>
    <h1>Ajouter un prêt d'abri</h1>
    <PretAbriForm :initialForm="form" :isEdit="false" :onSubmit="submitForm" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

import auth from "../../auth";

import config from "../../config";
import { useMainStore } from "../store";
import PretAbriForm from "./PretAbriForm.vue";

const form = ref({
  properties: {
    exploitant: "",
    abri_urgence: "",
    date_debut: "",
    date_fin: "",
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
    const response = await auth.axiosInstance.post(
      `${config.API_BASE_URL}/api/beneficierDe/`,
      formData
    );
    console.log("Form successfully submitted, response:", response);

    // Afficher un message de succès
    mainStore.setSuccessMessage("Prêt ajouté avec succès!");

    // Vérifier si le message est bien défini dans le store
    console.log("Success message set:", mainStore.successMessage);

    // Ajouter un petit délai pour vérifier l'affichage du message avant la redirection
    setTimeout(() => {
      router.push("/PretAbris");
    }, 500); // Petit délai pour s'assurer que le message est vu
  } catch (error) {
    mainStore.setErrorMessage(
      "Une erreur s'est produite lors de l'ajout du prêt." + error
    );
    console.error("There was an error!", error);
  }
};
</script>

<style scoped></style>
