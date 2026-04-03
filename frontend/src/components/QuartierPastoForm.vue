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
          <label for="code_up">Code quartier:</label>
          <input
            class="w3-input w3-border"
            type="text"
            id="code_up"
            v-model="form.properties.code_quartier"
            required
          />
        </div>
        <div class="form-cell">
          <label for="nom_up">Nom quartier:</label>
          <input
            class="w3-input w3-border"
            type="text"
            id="nom_up"
            v-model="form.properties.nom_quartier"
            required
          />
        </div>
        <div class="form-cell">
          <label for="unitepastorale">Unité pastorale :</label>
          <select
            class="w3-input w3-border"
            v-model="form.properties.unite_pastorale"
            id="unitepastorale"
          >
            <option v-for="up in ups.features" :key="up.id" :value="up.id">
              {{ up.properties.nom_up }}
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
            :key="form.geometry?.coordinates || ''"
            v-model="form.geometry"
            :geometryType="'Polygon'"
          />
          <!-- <MapEditMultipolygon2
            :key="form.geometry"
            v-model="form.geometry"
            :geometryType="'Polygon'"
          /> -->
        </div>
      </div>
    </div>
    <button type="submit">Enregistrer</button>
  </form>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";

import auth from "../../auth";

import config from "../../config";
import MapEditMultipolygon2 from "./MapEditMultipolygon2.vue";

const props = defineProps({
  initialForm: Object,
  isEdit: Boolean,
  onSubmit: Function,
});

const ups = ref([]);

const form = ref({ ...props.initialForm });

// Variable pour stocker le nextId
const nextId = ref(null);

const submitForm = () => {
  console.log("Form submitted with:", form.value);

  if (!props.isEdit) {
    form.value.id = nextId.value;
  }

  props
    .onSubmit(form.value)
    .then(() => {
      console.log("Form submission then block executed");
    })
    .catch((error) => {
      console.error("There was an error in form submission!", error);
    });
};

onMounted(() => {
  console.log("Form mounted with geometry:", form.value.geometry);

  // Récupére le prochain ID si on est en mode création uniquement
  if (!props.isEdit) {
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/quartierPasto/getNextId/`)
      .then((response) => {
        nextId.value = response.data.next_id;
        form.value.id = nextId.value;
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération du Next ID", error);
      });
  }

  // Récupère les propriétaires
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/unitePastorale/`)
    .then((response) => {
      ups.value = response.data;
      console.log("Unites pastorales récupérées:", ups.value);
    })
    .catch((error) => {
      console.error(
        "Erreur lors de la récupération de la liste des unites pastorales",
        error
      );
    });
});

watch(
  () => props.initialForm,
  (newForm) => {
    form.value = { ...newForm };
  },
  { deep: true }
);
</script>

<style scoped>
.form-ligne {
  padding: 8px;
}

.form-cell {
  padding: 8px;
}
</style>
