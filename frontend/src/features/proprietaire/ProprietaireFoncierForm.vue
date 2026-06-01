<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <form class="proprietaire-form" @submit.prevent="submitForm">
    <section class="layout-card">
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-text-field
            id="nom"
            v-model="form.nom_propr"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Nom"
            dense
            variant="underlined"
            hide-details
            clearable
          />
        </div>
        <div class="w3-half form-cell">
          <v-text-field
            id="prenom"
            v-model="form.prenom_propr"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Prénom"
            dense
            variant="underlined"
            hide-details
            clearable
          />
        </div>
      </div>
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-text-field
            id="telephone"
            v-model="form.tel_propr"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Téléphone"
            dense
            variant="underlined"
            hide-details
            clearable
          />
        </div>
        <div class="w3-half form-cell">
          <v-text-field
            id="email"
            v-model="form.mail_propr"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Email"
            dense
            variant="underlined"
            hide-details
            clearable
          />
        </div>
      </div>
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-text-field
            id="adresse"
            v-model="form.adresse_propr"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Adresse"
            dense
            variant="underlined"
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
            variant="underlined"
            hide-details
            clearable
          />
        </div>
      </div>
    </section>

    <div class="form-actions">
      <v-btn
        density="comfortable"
        color="info"
        @click="closeModal"
        prepend-icon="mdi-arrow-left-circle"
        >Retour</v-btn
      >
      <v-btn
        density="comfortable"
        v-if="props.mode !== 'view'"
        color="success"
        type="submit"
        prepend-icon="mdi-content-save"
        >{{ btTitle }}</v-btn
      >
    </div>
  </form>
</template>

<script setup>
import { reactive, watch, computed } from "vue";
import config from "../../../config";
import auth from "@/services/axios";
import { usePermissions } from "../../composables/usePermissions";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" }, // add | change | view
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("proprietairefoncier");

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
  nom_propr: "",
  prenom_propr: "",
  tel_propr: "",
  mail_propr: "",
  adresse_propr: "",
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

// Submit
const submitForm = () => {
  if (props.onSubmit) {
    props.onSubmit(form);
  }
};

// Close
const closeModal = () => {
  props.onClose?.();
};
</script>
<style scoped>
.layout-card {
  background: #ffffff;
  border: 1px solid #d7dde6;
  border-left: 3px solid #64748b;
  border-radius: 8px;
  padding: 0.75rem;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
  transition:
    border-color 140ms ease,
    box-shadow 140ms ease;
}
.layout-card:hover {
  border-color: #c8d0db;
  box-shadow: 0 2px 5px rgba(15, 23, 42, 0.08);
}
.proprietaire-form :deep(.v-input--density-compact .v-field__input) {
  min-height: 38px;
  padding-top: 6px;
  padding-bottom: 6px;
}
.proprietaire-form :deep(.v-label.v-field-label) {
  font-size: 0.82rem;
}
.proprietaire-form :deep(.v-input) {
  font-size: 0.88rem;
}
.proprietaire-form :deep(.v-field__input),
.proprietaire-form :deep(.v-select__selection-text) {
  font-size: 0.88rem;
}
.form-ligne {
  padding: 4px;
}
.form-cell {
  padding: 4px;
}
.form-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
}
.disable-events {
  pointer-events: none;
}
</style>
