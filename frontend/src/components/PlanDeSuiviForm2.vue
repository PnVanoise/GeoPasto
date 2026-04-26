<template>
  <h3 class="w3-center w3-margin">{{ formTitle }}</h3>
  <form @submit.prevent="submitForm">
    <div class="w3-row form-ligne">
      <div class="form-cell">
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
    </div>
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">        
        <v-text-field type="date" label="Date de début" v-model="form.date_debut" :class="{ 'disable-events': props.mode === 'view' || !can('change') }" dense hide-details clearable />
      </div>
      <div class="w3-half form-cell">
        <v-text-field type="date" label="Date de fin" v-model="form.date_fin" :class="{ 'disable-events': props.mode === 'view' || !can('change') }" dense hide-details clearable />
      </div>
    </div>
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-select
          id="situation"
          v-model="form.type_suivi"
          :items="typesuivis"
          item-title="description"
          item-value="id_type_suivi"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Type de suivi"
          dense
          hide-details
          clearable
        />
      </div>
      <div class="w3-half form-cell">
        <v-select
          id="up"
          v-model="form.unite_pastorale"
          :items="ups"
          item-title="nom_up"
          item-value="id_unite_pastorale"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Unité pastorale"
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

const { can } = usePermissions("plandesuivi");

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

const form = reactive({
  description: "",
  date_debut: "",
  date_fin: "",
  type_suivi: "",
  unite_pastorale: "",
});

const typesuivis = ref([]);
const ups = ref([]);

watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) {
      Object.assign(form, newVal);
    }
  },
  { immediate: true }
);

onMounted(() => {
  // Récupère les types de suivi
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/typeSuivi/`)
    .then((response) => {
      typesuivis.value = response.data;
    })
    .catch((error) => {
      console.error(
        "Erreur lors de la récupération de la liste des types de suivi",
        error
      );
    });

  // Récupère les unités pastorales
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/unitePastorale/light`)
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


// Submits
const submitForm = () => {
  if (props.onSubmit) {
    props.onSubmit(form)
      .then(() => console.log("Form submitted OK"))
      .catch(err => console.error(err));
  }
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
