<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <form class="categorie-animaux-form" @submit.prevent="submitForm">
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
        <div class="w3-half form-cell">
          <v-text-field
            v-model="form.coefficient_UGB"
            :disabled="props.mode === 'view'"
            label="Coefficient UGB"
            type="number"
            min="0"
            max="1"
            step="0.01"
            density="compact"
            variant="underlined"
            hide-details
          />
        </div>
      </div>
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-select
            id="espece"
            v-model="form.espece"
            :items="especes"
            item-title="description"
            item-value="id_espece"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Espèce"
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
import { reactive, watch, ref, computed, onMounted } from "vue";
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

const { can } = usePermissions("categorieanimaux");

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
  coefficient_UGB: 0,
  espece: "",
});

const especes = ref([]);

watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) {
      Object.assign(form, newVal);
      // assurer l'ID pour le mode "change" (compatibilité id / id_categorie_animaux)
      if (newVal.id_categorie_animaux !== undefined && newVal.id_categorie_animaux !== null) {
        form.id_categorie_animaux = newVal.id_categorie_animaux;
      } else if (newVal.id !== undefined && newVal.id !== null) {
        form.id_categorie_animaux = newVal.id;
      }
    }
  },
  { immediate: true }
);

onMounted(() => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/espece/`)
    .then((response) => {
      especes.value = response.data;
    })
    .catch((error) => {});
});

// Submits
const submitForm = () => {
  if (!props.onSubmit) return;
  // payload propre (deep copy) : enlever champs read-only et n'envoyer l'id que pour update
  const payload = JSON.parse(JSON.stringify(form));
  if (props.mode === "add") delete payload.id_categorie_animaux;
  props.onSubmit(payload);
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

.categorie-animaux-form :deep(.v-input--density-compact .v-field__input) {
  min-height: 38px;
  padding-top: 6px;
  padding-bottom: 6px;
}

.categorie-animaux-form :deep(.v-label.v-field-label) {
  font-size: 0.82rem;
}

.categorie-animaux-form :deep(.v-input) {
  font-size: 0.88rem;
}

.categorie-animaux-form :deep(.v-field__input),
.categorie-animaux-form :deep(.v-select__selection-text) {
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
