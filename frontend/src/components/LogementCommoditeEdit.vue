<template>
  <div>
    <h1>Éditer un logement / commodité</h1>
    <LogementCommoditeForm :initialForm="form" :isEdit="true" :onSubmit="submitForm" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";

import auth from "../../auth";
import config from "../../config";
import { useMainStore } from "../store";

import LogementCommoditeForm from "./LogementCommoditeForm.vue";

const form = ref({
  logement: "",
  commodite: "",
  etat: "",
  quantite: "",
  commentaire: "",
});

const route = useRoute();
const router = useRouter();
const id = route.params.id;
const mainStore = useMainStore();

const fetchLCommodite = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/logementCommodite/${id}/`)
    .then((response) => {
      console.log("response.data:", response.data);
      form.value = response.data;
    })
    .catch((error) => {
      mainStore.setErrorMessage("Erreur de lecture de la commodité logement.");
      console.error("LogementCommodite fetchLCommodite error: ", error);
    });
};

const submitForm = async (formData) => {
  try {
    const response = await auth.axiosInstance.put(
      `${config.API_BASE_URL}/api/logementCommodite/${id}/`,
      formData
    );
    console.log("Form successfully submitted, response:", response);
    mainStore.setSuccessMessage("Garde modifiée!");
    router.push("/LogementCommodites");
  } catch (error) {
    mainStore.setErrorMessage("Erreur d'enregistrement du logement / commodité.");
    console.error("LCommEdit submitForm error: ", error);
  }
};

onMounted(fetchLCommodite);
</script>

<style scoped></style>
