<template>
  <div>
    <h1>{{ title }}</h1>
    <UnitePastoraleForm
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

import { useMainStore } from "../store";
import UnitePastoraleForm from "./UnitePastoraleForm.vue";

import config from "../../config";

const form = ref({
  id: null,
  properties: {
    code_up: "",
    nom_up: "",
    secteur: "",
    annee_version: "",
    version_active: false,
  },
  geometry: {
    type: "MultiPolygon",
    coordinates: [],
  },
});

const route = useRoute();
const id = route.params.id;

const router = useRouter();
const mainStore = useMainStore();

const isReadOnly = computed(() => route.query.readonly === 'true');
const title = computed(() =>
  isReadOnly.value ? "Consulter une unité pastorale" : "Éditer une unité pastorale"
);

const fetchUP = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/unitePastorale/${id}/`)
    .then((response) => {
      console.log("response data : ", response.data);
      form.value.id = response.data.id;
      form.value.properties = response.data.properties;
      form.value.geometry = response.data.geometry;
      console.log("form properties : ", form.value);
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

const submitForm = async (formData) => {
  try {
    const response = await auth.axiosInstance.put(
      `${config.API_BASE_URL}/api/unitePastorale/${id}/`,
      formData
    );
    console.log("Form successfully submitted, response:", response);

    // Afficher un message de succès
    mainStore.setSuccessMessage("Unité Pastorale modifiée avec succès!");

    // Vérifier si le message est bien défini dans le store
    console.log("Success message set:", mainStore.successMessage);

    // Ajouter un petit délai pour vérifier l'affichage du message avant la redirection
    setTimeout(() => {
      router.push("/UnitePastorales");
    }, 500); // Petit délai pour s'assurer que le message est vu
  } catch (error) {
    mainStore.setErrorMessage(
      "Une erreur s'est produite lors de la modification de l'unité pastorale." + error
    );
    console.error("There was an error!", error);
  }
};

onMounted(fetchUP);
</script>

<style scoped>
/* Ajoutez vos styles ici */
</style>
