<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <form class="categorie-animaux-form" @submit.prevent="submitForm">
    <section class="layout-card">
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-text-field
            id="description"
            v-model="form.description"
            :disabled="props.mode === 'view' || !can('change')"
            label="Description"
            density="compact"
            variant="underlined"
            hide-details="auto"
            :rules="[maxLen(150)]"
            :counter="150"
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
            :disabled="props.mode === 'view' || !can('change')"
            label="Espèce"
            density="compact"
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
        :disabled="!isFormValid"
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
import { maxLen } from "@/utils/validators";

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
const isFormValid = computed(() => !!form.description?.trim());

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
