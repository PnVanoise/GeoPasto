<template>
  <div>
    <h1>Ajouter une garde</h1>
    <GardeTroupeauForm :initialForm="form" :isEdit="false" :onSubmit="submitForm" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

import auth from "../../auth";
import config from "../../config";
import { useMainStore } from "../store";

import GardeTroupeauForm from "./GardeTroupeauForm.vue";

const form = ref({
  berger: "",
  situation_exploitation: "",
  date_debut: "",
  date_fin: "",
  commentaire: "",
});

const router = useRouter();
const mainStore = useMainStore();

const submitForm = async (formData) => {
  try {
    const response = await auth.axiosInstance.post(
      `${config.API_BASE_URL}/api/gardeSituation/`,
      formData
    );
    console.log("Form successfully submitted, response:", response);

    // Afficher un message de succès
    mainStore.setSuccessMessage("Garde ajoutée avec succès!");

    // Vérifier si le message est bien défini dans le store
    console.log("Success message set:", mainStore.successMessage);

    // Ajouter un petit délai pour vérifier l'affichage du message avant la redirection
    setTimeout(() => {
      router.push("/GardeTroupeaux");
    }, 500); // Petit délai pour s'assurer que le message est vu
  } catch (error) {
    mainStore.setErrorMessage(
      "Une erreur s'est produite lors de l'ajout de la garde." + error
    );
    console.error("There was an error!", error);
  }
};
</script>

<style scoped></style>
