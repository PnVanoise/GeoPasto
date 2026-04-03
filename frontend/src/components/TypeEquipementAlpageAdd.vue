<template>
  <div>
    <h1>Ajouter un type d'équipement d'alpage</h1>
    <TypeEquipementAlpageForm
      :initialForm="form"
      :isEdit="false"
      :onSubmit="submitForm"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import auth from "../../auth";
import TypeEquipementAlpageForm from "./TypeEquipementAlpageForm.vue";
import config from "../../config";
import { useMainStore } from "../store";

const form = ref({
  nom: "",
  description: "",
});

const router = useRouter();
const mainStore = useMainStore();

const submitForm = async (formData) => {
  try {
    const response = await auth.axiosInstance.post(
      `${config.API_BASE_URL}/api/typeqptAA/`,
      formData
    );
    console.log("Response received:", response);
    mainStore.setSuccessMessage("Type d'équipement ajouté avec succès!");
    router.push("/TypeEquipementAlpages");
  } catch (error) {
    console.error("There was an error!", error);
    mainStore.setErrorMessage(
      "Une erreur s'est produite lors de l'ajout du type d'équipement."
    );
  }
};

// watch(successMessage, (newVal, oldVal) => {
//     console.log(`successMessage changed from "${oldVal}" to "${newVal}"`);
// });

// Hooks de cycle de vie pour déboguer
onMounted(() => {
  console.log("typeequipementadd component mounted");
});

onBeforeUnmount(() => {
  console.log("typeequipementadd component before unmount");
});
</script>

<style scoped></style>
