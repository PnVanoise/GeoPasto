<template>
  <div>
    <h1>Éditer un équipement d'alpage</h1>
    <EquipementForm :initialForm="form" :isEdit="true" :onSubmit="submitForm" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import axios from "axios";
import EquipementForm from "./EquipementForm.vue";

import config from "../../config";
import { useMainStore } from "../store";

const form = ref({
  etat: "",
  information_complementaire: "",
  type_eqpt_aa: "",
  quartier_up: "",
});

const route = useRoute();
const router = useRouter();
const id = route.params.id;
const mainStore = useMainStore();

const fetchEquipement = () => {
  axios
    .get(`${config.API_BASE_URL}/api/eqptAA/${id}/`)
    .then((response) => {
      console.log("response.data:", response.data);
      form.value = response.data.properties;
    })
    .catch((error) => {
      mainStore.setErrorMessage("Erreur de lecture de l''équipement.");
      console.error("EquipementEdit fetchEquipement error: ", error);
    });
};

const submitForm = async (formData) => {
  try {
    const response = await axios.put(
      `${config.API_BASE_URL}/api/eqptAA/${id}/`,
      formData
    );
    mainStore.setSuccessMessage("Equipement modifié.");
    router.push("/Equipements");
  } catch (error) {
    mainStore.setErrorMessage("Erreur d'enregistrement de l'équipement.");
    console.error("EquipementEdit submitForm error: ", error);
  }
};

onMounted(fetchEquipement);
</script>

<style scoped>
/* Ajoutez vos styles ici */
</style>
