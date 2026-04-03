<template>
  <div>
    <h1>Ajouter un équipement</h1>
    <EquipementForm :initialForm="form" :isEdit="false" :onSubmit="submitForm" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import EquipementForm from "./EquipementForm.vue";
import config from "../../config";
import { useMainStore } from "../store";

const form = ref({
  information_complementaire: "",
  etat: "",
  type_eqpt_aa: "",
  quartier_up: "",
});

const router = useRouter();
const mainStore = useMainStore();

const submitForm = async (formData) => {
  try {
    const response = await axios.post(`${config.API_BASE_URL}/api/eqptAA/`, formData);
    mainStore.setSuccessMessage("Equipement ajouté avec succès!");
    console.log("Response received:", response);
    router.push("/Equipements");
  } catch (error) {
    mainStore.setErrorMessage(
      "Une erreur s'est produite lors de l'ajout de l'équipement."
    );
    console.error("There was an error!", error);
  }
};
</script>

<style scoped></style>
