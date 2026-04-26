<template>
  <form @submit.prevent="submitForm">
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <label for="unitepastorale">Unité pastorale:</label>
        <select
          class="w3-input w3-border"
          v-model="form.unite_pastorale"
          id="unitepastorale"
        >
          <option v-for="up in ups.features" :key="up.id" :value="up.id">
            {{ up.properties.nom_up }}
          </option>
        </select>
      </div>

      <div class="w3-half form-cell">
        <label for="proprio">Propriétaire:</label>
        <select
          class="w3-input w3-border"
          v-model="form.proprietaire"
          id="unitepastorale"
        >
          <option
            v-for="proprio in proprietaires"
            :key="proprio.id_proprietaire"
            :value="proprio.id_proprietaire"
          >
            {{ proprio.nom_propr }} {{ proprio.prenom_propr }}
          </option>
        </select>
      </div>
    </div>
    <div class="w3-row form-ligne">
      <button type="submit">Enregistrer</button>
    </div>
  </form>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from "vue";

import config from "../../config";
import auth from "../../auth";

const props = defineProps({
  initialForm: Object,
  isEdit: Boolean,
  onSubmit: Function,
  logementId: String,
});

const proprietaires = ref([]);
const ups = ref([]);

const form = ref({ ...props.initialForm });

const submitForm = () => {
  console.log("Form submitted with:", form.value);

  props
    .onSubmit(form.value)
    .then(() => {
      console.log("Form submission then block executed");
    })
    .catch((error) => {
      console.error("There was an error in form submission!", error);
    });
};

watch(
  () => props.initialForm,
  (newForm) => {
    form.value = { ...newForm };
    if (props.logementId) {
      form.value.logement = props.logementId;
    }
  },
  { deep: true, immediate: true }
);

onMounted(() => {
  console.log("UPProprietaireForm component mounted");


  // Récupère les propriétaires
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/proprietaireFoncier/`)
    .then((response) => {
      proprietaires.value = response.data;
      console.log("proprietaires:", proprietaires.value);
    })
    .catch((error) => {
      console.error(
        "Erreur lors de la récupération de la liste des propriétaires",
        error
      );
    });

  // Récupère les unités pastorales
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/unitePastorale/`)
    .then((response) => {
      ups.value = response.data;
      console.log("ups:", ups.value);
    })
    .catch((error) => {
      console.error(
        "Erreur lors de la récupération de la liste des unités pastorales",
        error
      );
    });
});

onBeforeUnmount(() => {
  console.log("LogementCommodites component before unmount");
});
</script>

<style scoped>
.form-ligne {
  padding: 8px;
}

.form-cell {
  padding: 8px;
}
</style>
