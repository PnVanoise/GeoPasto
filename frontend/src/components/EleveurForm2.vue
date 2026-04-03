<template>
  <h3 class="w3-center w3-margin">{{ formTitle }}</h3>
  
  <form @submit.prevent="submitForm">
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-text-field
          id="nom"
          v-model="form.nom_eleveur"
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
          v-model="form.prenom_eleveur"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Prénom"
          dense
          hide-details
          clearable
        />
      </div>
    </div>
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-text-field
          id="tel"
          v-model="form.tel_eleveur"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Téléphone"
          dense
          hide-details
          clearable
        />
      </div>
      <div class="w3-half form-cell">
        <v-text-field
          id="mail"
          v-model="form.mail_eleveur"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Email"
          dense
          hide-details
          clearable
        />
      </div>
    </div>
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-text-field
          id="adresse"
          v-model="form.adresse_eleveur"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Adresse"
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

    <div class="form-actions">
      <v-btn density="comfortable" color="info" @click="closeModal" prepend-icon="mdi-arrow-left-circle">Retour</v-btn>
      <v-btn density="comfortable" v-if="props.mode !== 'view'" color="success" type="submit" prepend-icon="mdi-content-save">{{ btTitle }}</v-btn>
    </div>
  </form>
</template>s

<script setup>
import { reactive, watch, computed, onMounted } from "vue";
import { usePermissions } from "../composables/usePermissions";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" }, // add | change | view
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("eleveur");

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
  id_eleveur: null,
  nom_eleveur: "",
  prenom_eleveur: "",
  tel_eleveur: "",
  mail_eleveur: "",
  adresse_eleveur: "",
  commentaire: "",
});

watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) {
      Object.assign(form, newVal);
      // assurer l'ID pour le mode "change" (compatibilité id / id_eleveur)
      if (newVal.id_eleveur) form.id_eleveur = newVal.id_eleveur;
      else if (newVal.id) form.id_eleveur = newVal.id;
    }
  },
  { immediate: true }
);

onMounted(() => {
});

// Submit
const submitForm = () => {
  if (!props.onSubmit) return;
  // payload propre (deep copy) : enlever champs read-only et n'envoyer l'id que pour update
  const payload = JSON.parse(JSON.stringify(form));
  if (props.mode === 'add') delete payload.id_eleveur;
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
