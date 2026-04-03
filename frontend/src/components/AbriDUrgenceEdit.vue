<template>
  <div>
    <h1>{{ title }}</h1>
    <AbriDUrgenceForm
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
import AbriDUrgenceForm from "./AbriDUrgenceForm.vue";

const form = ref({
  description: "",
  etat: "",
});

const route = useRoute();
const router = useRouter();
const id = route.params.id;
const mainStore = useMainStore();

const isReadOnly = computed(() => route.query.readonly === 'true');
const title = computed(() =>
  isReadOnly.value ? "Consulter un abri d'urgence" : "Éditer un abri d'urgence"
);

const fetchAbri = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/abriDUrgence/${id}/`)
    .then((response) => {
      console.log("response.data:", response.data);
      form.value = response.data;
    })
    .catch((error) => {
      mainStore.setErrorMessage("Erreur de lecture de l'abri.");
      console.error("AbriEdit fetchAbri error: ", error);
    });
};

const submitForm = async (formData) => {
  try {
    const response = await auth.axiosInstance.put(
      `${config.API_BASE_URL}/api/abriDUrgence/${id}/`,
      formData
    );
    mainStore.setSuccessMessage("Abri modifié!");
    router.push("/AbriUrgences");
  } catch (error) {
    mainStore.setErrorMessage("Erreur d'enregistrement de l'abri.");
    console.error("Abri submitForm error: ", error);
  }
};

onMounted(fetchAbri);
</script>

<style scoped></style>
