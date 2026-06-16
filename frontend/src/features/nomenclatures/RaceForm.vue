<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <form class="race-form" @submit.prevent="submitForm">
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
            hide-details="auto"
            :rules="[maxLen(150)]"
            :counter="150"
            clearable
          />
        </div>
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

const { can } = usePermissions("race");

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
  espece: "",
});

const especes = ref([]);

watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) {
      Object.assign(form, newVal);
      // assurer l'ID pour le mode "change" (compatibilité id / id_race)
      if (newVal.id_race !== undefined && newVal.id_race !== null) {
        form.id_race = newVal.id_race;
      } else if (newVal.id !== undefined && newVal.id !== null) {
        form.id_race = newVal.id;
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
  if (props.mode === "add") delete payload.id_race;
  props.onSubmit(payload);
};

// Close
const closeModal = () => {
  props.onClose?.();
};
</script>

<style scoped>
.disable-events {
  pointer-events: none;
}
</style>
