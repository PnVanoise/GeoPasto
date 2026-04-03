<template>
  <div>
    <h1>{{ title }}</h1>
    <SubventionForm
      :initialForm="form"
      :isEdit="true"
      :is-read-only="isReadOnly"
      :onSubmit="!isReadOnly ? submitForm : undefined" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";

import auth from "../../auth";
import config from "../../config";
import { useMainStore } from "../store";
import SubventionForm from "./SubventionForm.vue";

const form = ref({
  description: "",
  montant: "",
  engage: "",
  paye: "",
  exploitant: "",
});

const route = useRoute();
const router = useRouter();
const id = route.params.id;
const mainStore = useMainStore();

const isReadOnly = computed(() => route.query.readonly === 'true');
const title = computed(() =>
  isReadOnly.value ? "Consulter une subvention" : "Éditer une subvention"
);

const fetchSubvention = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/subventionPNV/${id}/`)
    .then((response) => {
      console.log("response.data:", response.data);
      form.value = response.data;
    })
    .catch((error) => {
      mainStore.setErrorMessage("Erreur de lecture de la subvention.");
      console.error("SubventionEdit fetchSubvention error: ", error);
    });
};

const submitForm = async (formData) => {
  try {
    const response = await auth.axiosInstance.put(
      `${config.API_BASE_URL}/api/subventionPNV/${id}/`,
      formData
    );
    mainStore.setSuccessMessage("Subvention modifiée!");
    router.push("/Subventions");
  } catch (error) {
    mainStore.setErrorMessage("Erreur d'enregistrement de la subvention.");
    console.error("subvention submitForm error: ", error);
  }
};

onMounted(fetchSubvention);
</script>

<style scoped></style>
