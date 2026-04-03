<template>
  <h3 class="w3-center w3-margin">{{ formTitle }}</h3>
  <form @submit.prevent="submitForm">
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-text-field
          id="nom"
          v-model="form.nom_berger"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Nom"
          dense
          hide-details
          clearable
        />
      </div>
      <div class="w3-half form-cell">
        <v-text-field
          id="prenom"
          v-model="form.prenom_berger"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Prénom"
          dense
          hide-details
          clearable
        />
      </div>
      <div class="w3-half form-cell">
        <v-text-field
          id="tel"
          v-model="form.tel_berger"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Téléphone"
          dense
          hide-details
          clearable
        />
      </div>
      <div class="w3-half form-cell">
        <v-text-field
          id="adresse"
          v-model="form.adresse_berger"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Adresse"
          dense
          hide-details
          clearable
        />
      </div>
      <div class="w3-half form-cell">
        <v-text-field
          id="comm"
          v-model="form.commentaire"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Commentaire"
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

const { can } = usePermissions("berger");

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
  nom_berger: "",
  prenom_berger: "",
  tel_berger: "",
  adresse_berger: "",
  commentaire: "",
 });

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
      .get(`${config.API_BASE_URL}/api/berger/getNextId/`)
      .then(res => {
        nextId.value = res.data.next_id;
        form.id_berger = nextId.value;
      })
      .catch(err => console.error("Erreur Next ID", err));
  };
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
