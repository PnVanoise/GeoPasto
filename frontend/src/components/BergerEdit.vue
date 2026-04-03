<template>
  <div>
    <h1>{{ title }}</h1>
    <BergerForm
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
import BergerForm from "./BergerForm.vue";

const form = ref({
  nom_berger: "",
  prenom_berger: "",
  tel_berger: "",
  mail_berger: "",
  adresse_berger: "",
  commentaire: "",
});

const route = useRoute();
const router = useRouter();
const id = route.params.id;
const mainStore = useMainStore();

const isReadOnly = computed(() => route.query.readonly === 'true');
const title = computed(() =>
  isReadOnly.value ? "Consulter un berger" : "Éditer un berger"
);

const fetchBerger = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/berger/${id}/`)
    .then((response) => {
      console.log("response.data:", response.data);
      form.value = response.data;
    })
    .catch((error) => {
      mainStore.setErrorMessage("Erreur de lecture du berger.");
      console.error("bergerEdit fetchberger error: ", error);
    });
};

const submitForm = async (formData) => {
  try {
    const response = await auth.axiosInstance.put(
      `${config.API_BASE_URL}/api/berger/${id}/`,
      formData
    );
    mainStore.setSuccessMessage("berger modifié!");
    router.push("/Bergers");
  } catch (error) {
    mainStore.setErrorMessage("Erreur d'enregistrement du berger.");
    console.error("berger submitForm error: ", error);
  }
};

onMounted(fetchBerger);
</script>

<style scoped></style>
