<template>
  <form @submit.prevent="submitForm">
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <label for="description">Description:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="description"
          v-model="form.description"
          required
          :disabled="props.isReadOnly"
        />
      </div>
      <div class="w3-half form-cell">
        <label for="dateDebut">Date de début:</label>
        <input
          class="w3-input w3-border"
          type="date"
          id="dateDebut"
          v-model="form.date_debut"
          @keydown.prevent
          @paste.prevent
          :disabled="props.isReadOnly"
        />
      </div>
      <div class="w3-half form-cell">
        <label for="dateFin">Date de fin:</label>
        <input
          class="w3-input w3-border"
          type="date"
          id="dateFin"
          v-model="form.date_fin"
          @keydown.prevent
          @paste.prevent
          :disabled="props.isReadOnly"
        />
      </div>
      <div class="w3-half form-cell">
        <label for="typedesuivi">Type de suivi:</label>
        <select
          class="w3-input w3-border"
          v-model="form.type_suivi"
          id="typedesuivi"
          :disabled="props.isReadOnly"
        >
          <option
            v-for="typesuivi in typesuivis"
            :key="typesuivi.id_type_suivi"
            :value="typesuivi.id_type_suivi"
          >
            {{ typesuivi.description }}
          </option>
        </select>
      </div>
      <div class="w3-half form-cell">
        <label for="unitepastorale">Unité pastorale:</label>
        <select
          class="w3-input w3-border"
          v-model="form.unite_pastorale"
          id="unitepastorale"
          :disabled="props.isReadOnly"
        >
          <option v-for="up in ups.features" :key="up.id" :value="up.id">
            {{ up.properties.nom_up }}
          </option>
        </select>
      </div>
    </div>
    <button v-if="!isReadOnly" type="submit">Enregistrer</button>
  </form>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from "vue";

import config from "../../config";
import auth from "../../auth";

const props = defineProps({
  initialForm: Object,
  isEdit: Boolean,
  isReadOnly: {
    type: Boolean,
    default: false,
  },
  onSubmit: Function,
});

const typesuivis = ref([]);
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
  },
  { deep: true }
);

onMounted(() => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/typeSuivi/`)
    .then((response) => {
      typesuivis.value = response.data;
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération de la liste des types de suivi", error);
    });

  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/unitePastorale/`)
    .then((response) => {
      ups.value = response.data;
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération de la liste des unités pastorales", error);
    });
});

onBeforeUnmount(() => {
  console.log("TypeDeSuiviForm component before unmount");
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
