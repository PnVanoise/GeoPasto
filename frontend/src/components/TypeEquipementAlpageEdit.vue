<template>
  <div>
    <h1>Éditer un type d'équipement d'alpage</h1>
    <TypeEquipementAlpageForm :initialForm="form" :isEdit="true" :onSubmit="submitForm" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import auth from "../../auth";
import TypeEquipementAlpageForm from "./TypeEquipementAlpageForm.vue";

import config from "../../config";
import { useMainStore } from "../store";

const form = ref({
  nom: "",
  description: "",
});

const route = useRoute();
const router = useRouter();
const id = route.params.id;
const mainStore = useMainStore();

const fetchTypeEqpt = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/typeqptAA/${id}/`)
    .then((response) => {
      console.log("response.data:", response.data);
      form.value = response.data;
    })
    .catch((error) => {
      mainStore.setErrorMessage("Erreur de lecture du type d'équipement.");
      console.error("TypeEquipement fetchTypeEqpt error: ", error);
    });
};

const submitForm = async (formData) => {
  try {
    const response = await auth.axiosInstance.put(
      `${config.API_BASE_URL}/api/typeqptAA/${id}/`,
      formData
    );
    mainStore.setSuccessMessage("Type d'équipement modifié!");
    router.push("/TypeEquipementAlpages");
  } catch (error) {
    mainStore.setErrorMessage("Erreur d'enregistrement du type d'équipement.");
    console.error("TypeEquipement submitForm error: ", error);
  }
};

onMounted(fetchTypeEqpt);
</script>

<style scoped></style>
