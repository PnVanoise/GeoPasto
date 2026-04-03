<template>
  <div>
    <h1>Ajouter un Propriétaire / UP</h1>
    <UPProprietaireForm :initialForm="form" :isEdit="false" :onSubmit="submitForm" />

    <!-- :logementId="form.logement" -->
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

import auth from "../../auth";
import config from "../../config";
import { useMainStore } from "../store";

import UPProprietaireForm from "./UPProprietaireForm.vue";

const route = useRoute();
console.log("route", route.params);

const form = ref({
  unite_pastorale: route.params.UPId || "", // Utilisez l'ID de logement depuis les paramètres de la route
  proprietaire: "",
});

console.log("route id", route.params.UPId);
console.log("form", form.value);

const router = useRouter();
const mainStore = useMainStore();

const submitForm = async (formData) => {
  try {
    const response = await auth.axiosInstance.post(
      `${config.API_BASE_URL}/api/upproprietaire/`,
      formData
    );
    console.log("Form successfully submitted, response:", response);

    // Afficher un message de succès
    mainStore.setSuccessMessage("Propriétaire / UP ajouté avec succès!");

    // Vérifier si le message est bien défini dans le store
    console.log("Success message set:", mainStore.successMessage);

    // Ajouter un petit délai pour vérifier l'affichage du message avant la redirection
    setTimeout(() => {
      router.push("/UPProprietaires");
    }, 500); // Petit délai pour s'assurer que le message est vu
  } catch (error) {
    mainStore.setErrorMessage(
      "Une erreur s'est produite lors de l'ajout du propriétaire / UP." + error
    );
    console.error("There was an error!", error);
  }
};
</script>

<style scoped></style>
