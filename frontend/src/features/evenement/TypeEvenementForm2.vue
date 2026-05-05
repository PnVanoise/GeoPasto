<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <form class="type-evenement-form" @submit.prevent="submitForm">
    <section class="layout-card">
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-text-field
            id="description"
            v-model="form.description"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Description"
            dense
            variant="underlined"
            hide-details
            clearable
          />
        </div>
      </div>
    </section>

    <div class="form-actions">
      <v-btn density="comfortable" color="info" @click="closeModal" prepend-icon="mdi-arrow-left-circle">Retour</v-btn>
      <v-btn density="comfortable" v-if="props.mode !== 'view'" color="success" type="submit" prepend-icon="mdi-content-save">{{ btTitle }}</v-btn>
    </div>
  </form>
</template>

<script setup>
import { reactive, watch, ref, computed, onMounted } from "vue";
import config from "../../../config";
import auth from '@/services/axios';
import { usePermissions } from "../../composables/usePermissions";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" }, // add | change | view
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("typeevenement");

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
  id_type_evenement: null,
  description: "",
});

watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) {
      Object.assign(form, newVal);
      // assurer l'ID pour le mode "change" (compatibilité id / id_type_evenement)
      if (newVal.id_type_evenement !== undefined && newVal.id_type_evenement !== null) {
        form.id_type_evenement = newVal.id_type_evenement;
      } else if (newVal.id !== undefined && newVal.id !== null) {
        form.id_type_evenement = newVal.id;
      }
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
  if (props.mode === 'add') delete payload.id_type_evenement;
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
.layout-card {
  background: #ffffff;
  border: 1px solid #d7dde6;
  border-left: 3px solid #64748b;
  border-radius: 8px;
  padding: 0.75rem;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
  transition: border-color 140ms ease, box-shadow 140ms ease;
}
.layout-card:hover {
  border-color: #c8d0db;
  box-shadow: 0 2px 5px rgba(15, 23, 42, 0.08);
}
.type-evenement-form :deep(.v-input--density-compact .v-field__input) { min-height: 38px; padding-top: 6px; padding-bottom: 6px; }
.type-evenement-form :deep(.v-label.v-field-label) { font-size: 0.82rem; }
.type-evenement-form :deep(.v-input) { font-size: 0.88rem; }
.type-evenement-form :deep(.v-field__input),
.type-evenement-form :deep(.v-select__selection-text) { font-size: 0.88rem; }
.form-ligne { padding: 4px; }
.form-cell { padding: 4px; }
.form-actions { display: flex; justify-content: center; align-items: center; gap: 0.5rem; margin-top: 1.5rem; }
.disable-events { pointer-events: none; }
</style>


