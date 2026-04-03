<template>
  <div>
    <h1>{{ title }}</h1>
    <MesureDePlanForm
      :initialForm="form"
      :isEdit="true"
      :is-read-only="isReadOnly"
      :onSubmit="!isReadOnly ? submitForm : undefined"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";

import auth from "../../auth";
import config from "../../config";
import { useMainStore } from "../store";

import MesureDePlanForm from "./MesureDePlanForm.vue";

const form = ref({
  description: "",
  commentaire: "",
  debut_periode: "",
  fin_periode: "",
});

const route = useRoute();
const router = useRouter();
const id = route.params.id;
const mainStore = useMainStore();

const isReadOnly = computed(() => route.query.readonly === 'true');
const title = computed(() =>
  isReadOnly.value ? "Consulter une mesure de plan" : "Éditer une mesure de plan"
);

const fetchMesureDePlan = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/mesurePlan/${id}/`)
    .then((response) => {
      console.log("response.data:", response.data);
      form.value = response.data;
    })
    .catch((error) => {
      mainStore.setErrorMessage("Erreur de lecture de la mesure de plan.");
      console.error("MesureDePlan fecthMesureDePlan error: ", error);
    });
};

const submitForm = async (formData) => {
  try {
    const response = await auth.axiosInstance.put(
      `${config.API_BASE_URL}/api/mesurePlan/${id}/`,
      formData
    );
    mainStore.setSuccessMessage("Mesure de plan modifiée!");
    router.push("/MesurePlans");
  } catch (error) {
    mainStore.setErrorMessage("Erreur d'enregistrement de la mesure de plan.");
    console.error("Mesure de plan submitForm error: ", error);
  }
};

onMounted(fetchMesureDePlan);
</script>

<style scoped></style>
