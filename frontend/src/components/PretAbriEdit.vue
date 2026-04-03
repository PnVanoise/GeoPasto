<template>
  <div>
    <h1>{{ title }}</h1>
    <PretAbriForm
      :initialForm="form"
      :isEdit="!isReadOnly"
      :is-read-only="isReadOnly"
      :on-submit="!isReadOnly ? submitForm : undefined" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";

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

const route = useRoute();
const router = useRouter();
const id = route.params.id;
const mainStore = useMainStore();

const isReadOnly = computed(() => route.query.readonly === 'true');
const title = computed(() =>
  isReadOnly.value ? "Consulter un prêt d'abri" : "Éditer un prêt d'abri"
);

const fetchPret = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/beneficierDe/${id}/`)
    .then((response) => {
      console.log("response.data:", response.data);
      form.value = response.data;
    })
    .catch((error) => {
      mainStore.setErrorMessage("Erreur de lecture du prêt.");
      console.error("PretEdit fetchPret error: ", error);
    });
};

const submitForm = async (formData) => {
  try {
    const response = await auth.axiosInstance.put(
      `${config.API_BASE_URL}/api/beneficierDe/${id}/`,
      formData
    );
    console.log("Form successfully submitted, response:", response);
    mainStore.setSuccessMessage("Prêt modifié!");
    router.push("/PretAbris");
  } catch (error) {
    mainStore.setErrorMessage("Erreur d'enregistrement du prêt.");
    console.error("Pret submitForm error: ", error);
  }
};

onMounted(fetchPret);
</script>

<style scoped></style>
