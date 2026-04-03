<template>
  <div>
    <h1>Éditer un Propriétaire / UP</h1>
    <UPProprietaireForm :initialForm="form" :isEdit="true" :onSubmit="submitForm" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";

import auth from "../../auth";
import config from "../../config";
import { useMainStore } from "../store";

import UPProprietaireForm from "./UPProprietaireForm.vue";

const form = ref({
  unite_pastorale: "",
  proprietaire: "",
});

const route = useRoute();
const router = useRouter();
const id = route.params.id;
const mainStore = useMainStore();

const fetchUPPropr = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/upproprietaire/${id}/`)
    .then((response) => {
      console.log("response.data:", response.data);
      form.value = response.data;
    })
    .catch((error) => {
      mainStore.setErrorMessage("Erreur de lecture du Propriétaire / UP.");
      console.error("UPProprietaire fetchUPPropr error: ", error);
    });
};

const submitForm = async (formData) => {
  try {
    const response = await auth.axiosInstance.put(
      `${config.API_BASE_URL}/api/upproprietaire/${id}/`,
      formData
    );
    console.log("Form successfully submitted, response:", response);
    mainStore.setSuccessMessage("Garde modifiée!");
    router.push("/UPProprietaires");
  } catch (error) {
    mainStore.setErrorMessage("Erreur d'enregistrement du Propriétaire / UP.");
    console.error("UPPropr submitForm error: ", error);
  }
};

onMounted(fetchUPPropr);
</script>

<style scoped></style>
