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
        <!-- next id is readonly -->
        <div v-if="!isEdit" class="form-cell">
          (Next ID:
          {{ nextId }}
          )
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

// Variable pour stocker le nextId
const nextId = ref(null);

const submitForm = () => {
  if (!props.isEdit) {
    form.value.id = nextId.value;
  }

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

  if (!props.isEdit) {
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/ruche/getNextId/`)
      .then((response) => {
        nextId.value = response.data.next_id;
        form.value.id = nextId.value; // Optionnel: lier cet ID au formulaire si besoin
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération du Next ID", error);
      });
  }

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
