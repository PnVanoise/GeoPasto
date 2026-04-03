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
    </div>
    
    <div class="form-actions">
      <v-btn density="comfortable" color="info" @click="closeModal" prepend-icon="mdi-arrow-left-circle">Retour</v-btn>
      <v-btn density="comfortable" v-if="props.mode !== 'view'" color="success" type="submit" prepend-icon="mdi-content-save">{{ btTitle }}</v-btn>
    </div>
  </form>
</template>

<script setup>
import { reactive, watch, computed, onMounted } from "vue";
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

const { can } = usePermissions("categorie_pension");

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
 });

watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) {
      Object.assign(form, newVal);
      // assurer l'ID pour le mode "change" (compatibilité id / id_categorie_pension)
      if (newVal.id_categorie_pension) form.id_categorie_pension = newVal.id_categorie_pension;
      else if (newVal.id) form.id_categorie_pension = newVal.id;
    }
  },
  { immediate: true }
);

onMounted(() => {
});


// Submits
const submitForm = () => {
  if (!props.onSubmit) return;
  // payload propre (deep copy) : enlever champs read-only et n'envoyer l'id que pour update
  const payload = JSON.parse(JSON.stringify(form));
  if (props.mode === 'add') delete payload.id_categorie_pension;
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


