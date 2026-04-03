<template>
  <div>
    <h1>Ajouter un logement commodité</h1>
    <LogementCommoditeForm
      :initialForm="form"
      :isEdit="false"
      :logementId="form.logement"
      :onSubmit="submitForm"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

import auth from "../../auth";
import config from "../../config";
import { useMainStore } from "../store";

import LogementCommoditeForm from "./LogementCommoditeForm.vue";

const route = useRoute();
console.log("route", route.params);

const form = ref({
  logement: route.params.logementId || "", // Utilisez l'ID de logement depuis les paramètres de la route
  commodite: "",
  etat: "",
  quantite: "",
  commentaire: "",
});

console.log("route id", route.params.logementId);
console.log("form", form.value);

const router = useRouter();
const mainStore = useMainStore();

const submitForm = async (formData) => {
  try {
    const response = await auth.axiosInstance.post(
      `${config.API_BASE_URL}/api/logementCommodite/`,
      formData
    );
    console.log("Form successfully submitted, response:", response);

    // Afficher un message de succès
    mainStore.setSuccessMessage("Logement / Commodité ajouté avec succès!");

    // Vérifier si le message est bien défini dans le store
    console.log("Success message set:", mainStore.successMessage);

    // Ajouter un petit délai pour vérifier l'affichage du message avant la redirection
    setTimeout(() => {
      router.push("/LogementCommodites");
    }, 500); // Petit délai pour s'assurer que le message est vu
  } catch (error) {
    mainStore.setErrorMessage(
      "Une erreur s'est produite lors de l'ajout du logement / commodité." + error
    );
    console.error("There was an error!", error);
  }
};
</script>

<style scoped></style>
