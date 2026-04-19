<template>
  <h3 class="w3-center w3-margin">{{ formTitle }}</h3>

  <form @submit.prevent="submitForm">
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-text-field
          id="description" 
          v-model="form.description"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Description"
          dense
          hide-details
          clearable
        />
      </div>
      <div class="w3-half form-cell">
        <v-select
          id="production"
          v-model="form.production"
          :items="productions"
          item-title="description"
          item-value="id_production"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Production"
          dense
          hide-details
          clearable
        />
      </div>
    </div>
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-select
          id="race"
          v-model="form.race"
          :items="races"
          item-title="description"
          item-value="id_race"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Race"
          dense
          hide-details
          clearable
        />
      </div>
      <div class="w3-half form-cell">
        <v-select
          id="pension"
          v-model="form.pension"
          :items="pensions"
          item-title="description"
          item-value="id_categorie_pension"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Pension"
          dense
          hide-details
          clearable
        />
      </div>
      <div class="w3-half form-cell">
        <v-text-field
          id="coefficient_UGB"
          v-model.number="form.coefficient_UGB"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Coefficient UGB"
          type="number"
          min="0"
          max="1"
          step="0.01"
          dense
          hide-details
        />
      </div>
    </div>
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-select
          id="categorie_animaux"
          v-model="form.categorie_animaux"
          :items="categories"
          item-title="description"
          item-value="id_categorie_animaux"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Catégorie d'animaux"
          dense
          hide-details
          clearable
        />
      </div>
    </div>
    
    <div class="form-actions">
      <v-btn density="comfortable" color="info" @click="closeModal" prepend-icon="mdi-arrow-left-circle">Retour</v-btn>
      <v-btn density="comfortable" v-if="props.mode !== 'view'" color="success" type="submit" prepend-icon="mdi-content-save">{{ btTitle }}</v-btn>
    </div>
  </form>
</template>

<script setup>
import { reactive, watch, ref, computed, onMounted } from "vue";
import config from "../../config";
import auth from "../../auth";
import { usePermissions } from "../composables/usePermissions";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" }, // add | change | view
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("type_cheptel");

const formTitle = computed(() => {
  if (props.mode === "add") return `Ajouter ${props.itemLabel}`;
  if (props.mode === "change") return `Modifier ${props.itemLabel}`;
  if (props.mode === "view") return `Voir les détails d'${props.itemLabel}`;
  return "";
});

const btTitle = computed(() => {
  if (props.mode === "add") return "Ajouter";
  if (props.mode === "change") return "Enregistrer";
  return "";
});

// Formulaire réactif
const form = reactive({
  description: "",
  coefficient_UGB: 0,
  production: "",
  pension: "",
  race: "",
  categorie_animaux: "",
});

const productions = ref([]);
const pensions = ref([]);
const races = ref([]);
const categories = ref([]);

watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) {
      Object.assign(form, newVal);
      // assurer l'ID pour le mode "change" (compatibilité id / id_type_cheptel)
      if (newVal.id_type_cheptel !== undefined && newVal.id_type_cheptel !== null) {
        form.id_type_cheptel = newVal.id_type_cheptel;
      } else if (newVal.id !== undefined && newVal.id !== null) {
        form.id_type_cheptel = newVal.id;
      }
    }
  },
  { immediate: true }
);

onMounted(() => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/production/`)
    .then((response) => {
      productions.value = response.data;
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération de la liste des productions", error);
    });

  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/categorie_pension/`)
    .then((response) => {
      pensions.value = response.data;
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération de la liste des catégories de pensions", error);
    });

  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/categorie_animaux/`)
    .then((response) => {
      categories.value = response.data;
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération de la liste des catégories d'animaux", error);
    });

  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/race/`)
    .then((response) => {
      races.value = response.data;
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération de la liste des races", error);
    });

});


// Submit
const submitForm = () => {
  if (!props.onSubmit) return;
  // payload propre (deep copy) : enlever champs read-only et n'envoyer l'id que pour update
  const payload = JSON.parse(JSON.stringify(form));
  if (props.mode === 'add') delete payload.id_type_cheptel;
  props.onSubmit(payload)
    .then(() => console.log("Form submitted OK"))
    .catch(err => console.error(err));
};

// Close
const closeModal = () => {
  props.onClose?.();
};
</script>
<style scoped>
.form-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.disable-events {
  pointer-events: none
}
</style>
