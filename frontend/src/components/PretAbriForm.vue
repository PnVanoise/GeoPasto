<template>
  <p>Mode lecture seule : {{ isReadOnly }}</p>
  <form @submit.prevent="submitForm">
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <label for="exploitant">Exploitant:</label>
        <select
          class="w3-input w3-border"
          v-model="form.properties.exploitant"
          id="exploitant"
          :disabled="props.isReadOnly"
        >
          <option
            v-for="exploitant in exploitants"
            :key="exploitant.id_exploitant"
            :value="exploitant.id_exploitant"
          >
            {{ exploitant.nom_exploitant }}
          </option>
        </select>
      </div>
      <div class="w3-half form-cell">
        <label for="abri">Abri:</label>
        <select
          class="w3-input w3-border"
          v-model="form.properties.abri_urgence"
          id="abri"
          :disabled="props.isReadOnly"
        >
          <option
            v-for="abri in abris"
            :key="abri.id_abri_urgence"
            :value="abri.id_abri_urgence"
          >
            {{ abri.description }}
          </option>
        </select>
      </div>
      <div class="w3-half form-cell">
        <label for="dateDebut">Date de début:</label>
        <input
          class="w3-input w3-border"
          type="date"
          id="dateDebut"
          v-model="form.properties.date_debut"
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
          v-model="form.properties.date_fin"
          @keydown.prevent
          @paste.prevent
          :disabled="props.isReadOnly"
        />
      </div>
      <!-- next id pour debug -->
      <div v-if="!isEdit" class="form-cell">
        (Next ID:
        {{ nextId }}
        )
      </div>
    </div>
    <div class="form-cell">
      Géométrie:
      <MapEditMultipolygon2
        :key="form.geometry.coordinates"
        v-model="form.geometry"
        :geometryType="'Point'"
      />
    </div>
    <button v-if="!props.isReadOnly" type="submit">Enregistrer</button>
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
  isReadOnly: {
    type: Boolean,
    default: false
  },
  onSubmit: Function,
});

const exploitants = ref([]);
const abris = ref([]);

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

watch(
  () => props.initialForm,
  (newForm) => {
    form.value = { ...newForm };
  },
  { deep: true }
);

// Hooks de cycle de vie pour déboguer
onMounted(() => {
  console.log("AbriForm component mounted");

  if (!props.isEdit) {
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/beneficierDe/getNextId/`)
      .then((response) => {
        nextId.value = response.data.next_id;
        form.value.id = nextId.value;
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération du Next ID", error);
      });
  }

  // Récupère les exploitants
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/exploitant/`)
    .then((response) => {
      exploitants.value = response.data;
      console.log("exploitants:", exploitants.value);
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération de la liste des exploitants", error);
    });

  // Récupère les abris
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/abriDUrgence/`)
    .then((response) => {
      abris.value = response.data;
      console.log("abris:", abris.value);
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération de la liste des abris", error);
    });
});

onBeforeUnmount(() => {
  console.log("AbriForm component before unmount");
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
