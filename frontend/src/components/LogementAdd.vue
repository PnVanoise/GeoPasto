<template>
  <div>
    <h1>Ajouter un logement</h1>
    <LogementForm :initialForm="form" :isEdit="false" :onSubmit="submitForm" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

import auth from "../../auth";

import LogementForm from "./LogementForm.vue";
import config from "../../config.js";
import { useMainStore } from "../store";

const form = ref({
  properties: {
    unite_pastorale,
    logement_code: "",
    statut: "",
    acces_final: "",
    propriete: "",
    type_logement: "",
    multiusage: "",
    activite_laitiere: "",
    etat_batiment: "",
    accueil_public: "",
    mixite_possible: "",
    surface_logement: "",
    presence_douche: "",
    type_wc: "",
    alim_elec: "",
    alim_eau: "",
    origine_eau: "",
    qualite_eau: "",
    dispo_eau: "",
    assainissement: "",
    chauffe_eau: "",
    chauffage: "",
    stockage_indep: "",
  },
  geometry: {
    type: "Point",
    coordinates: [],
  },
});

const mainStore = useMainStore();

const submitForm = async (formData) => {
  try {
    const response = await auth.axiosInstance.post(
      `${config.API_BASE_URL}/api/logement/`,
      formData
    );
    console.log("Form successfully submitted, response:", response);

    // Afficher un message de succès
    mainStore.setSuccessMessage("Logement ajouté avec succès!");

    // Vérifier si le message est bien défini dans le store
    console.log("Success message set:", mainStore.successMessage);

    // Ajouter un petit délai pour vérifier l'affichage du message avant la redirection
    setTimeout(() => {
      router.push("/Logements");
    }, 500); // Petit délai pour s'assurer que le message est vu
  } catch (error) {
    mainStore.setErrorMessage(
      "Une erreur s'est produite lors de l'ajout du logement." + error
    );
    console.error("There was an error!", error);
  }
};
</script>

<style scoped>
/* Ajoutez vos styles ici */
</style>
