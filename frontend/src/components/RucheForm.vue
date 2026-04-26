<template>
  <form @submit.prevent="submitForm">
    <!-- Add your form fields here -->
    <div
      style="
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        align-items: stretch;
      "
    >
      <div style="">
        <div class="form-cell">
          <label for="description">Description:</label>
          <input
            class="w3-input w3-border"
            type="text"
            id="description"
            v-model="form.properties.description"
            required
          />
        </div>
        <div class="form-cell">
          <label for="situation">Situation d'exploitation :</label>
          <select
            class="w3-input w3-border"
            v-model="form.properties.situation_exploitation"
            id="situation"
          >
            <option
              v-for="situation in situations"
              :key="situation.id_situation"
              :value="situation.id_situation"
            >
              {{ situation.nom_situation }}
            </option>
          </select>
        </div>
      </div>
      <div style="">
        <div class="form-cell">
          Géométrie:
          <MapEditMultipolygon2
            :key="form.geometry.coordinates"
            v-model="form.geometry"
            :geometryType="'Point'"
          />
        </div>
      </div>
    </div>
    <button type="submit">Enregistrer</button>
  </form>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from "vue";

import config from "../../config";
import auth from "../../auth";
import MapEditMultipolygon2 from "./MapEditMultipolygon2.vue";

const props = defineProps({
  initialForm: Object,
  isEdit: Boolean,
  onSubmit: Function,
});

const situations = ref([]);

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
  },
  { deep: true }
);

// Hooks de cycle de vie pour déboguer
onMounted(() => {
  console.log("RucheForm component mounted");

  // Récupère les situations
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/situationExploitation/`)
    .then((response) => {
      situations.value = response.data;
      console.log("Situations récupérées:", situations.value);
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération de la liste des situations", error);
    });
});

onBeforeUnmount(() => {
  console.log("RucheForm component before unmount");
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
