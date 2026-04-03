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
        <v-text-field 
          id="commentaire"
          v-model="form.commentaire"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Commentaire"
          dense
          hide-details
          clearable
        />
      </div>
    </div>
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-text-field
          type="date"
          label="Date de début de période"
          v-model="form.debut_periode"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          dense
          hide-details
          clearable
        />
      </div>
      <div class="w3-half form-cell">
        <v-text-field
          type="date"
          label="Date de fin de période"
          v-model="form.fin_periode"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          dense
          hide-details
          clearable
        />
      </div>
    </div>
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-select
          id="typedemesure"
          v-model="form.type_mesure"
          :items="typemesures"
          item-title="description"
          item-value="id_type_mesure"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Type de mesure"
          dense
          hide-details
          clearable
        />
      </div>
      <div class="w3-half form-cell">
        <v-select
          id="plandesuivi"
          v-model="form.plan_suivi"
          :items="plansuivis"
          item-title="description"
          item-value="id_plan_suivi"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Plan de suivi"
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

const { can } = usePermissions("mesuredeplan");

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
  commentaire: "",
  debut_periode: "",
  fin_periode: "",
});

const typemesures = ref([]);
const plansuivis = ref([]);

watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) {
      Object.assign(form, newVal);
    }
  },
  { immediate: true }
);

// Next ID pour l'ajout
const nextId = ref(null);

onMounted(() => {
  if (props.mode === "add") {
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/mesurePlan/getNextId/`)
      .then((response) => {
        nextId.value = response.data.next_id;
        form.id_mesure_plan = nextId.value; // Optionnel: lier cet ID au formulaire si besoin
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération du Next ID", error);
      });
  }

  // Récupère les types de mesure
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/typeMesure/`)
    .then((response) => {
      typemesures.value = response.data;
    })
    .catch((error) => {
      console.error(
        "Erreur lors de la récupération de la liste des types de mesure",
        error
      );
    });

  // Récupère les plans de suivi
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/planSuivi/`)
    .then((response) => {
      plansuivis.value = response.data;
    })
    .catch((error) => {
      console.error(
        "Erreur lors de la récupération de la liste des plans de suivi",
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
