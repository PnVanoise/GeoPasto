<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <form class="type-equipement-form" @submit.prevent="submitForm">
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
          <v-text-field
            id="categorie"
            v-model="form.categorie"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Catégorie"
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

const { can } = usePermissions("typeequipement");

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
  id_type_equipement: null,
  description: "",
  categorie: "",
});

watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) {
      Object.assign(form, newVal);
      // assurer l'ID pour le mode "change" (compatibilité id / id_type_equipement)
      if (newVal.id_type_equipement !== undefined && newVal.id_type_equipement !== null) {
        form.id_type_equipement = newVal.id_type_equipement;
      } else if (newVal.id !== undefined && newVal.id !== null) {
        form.id_type_equipement = newVal.id;
      }
    }
  },
  { immediate: true }
);

onMounted(() => {});

const isFormValid = computed(() => !!form.description?.trim());

// Submit
const submitForm = () => {
  if (!props.onSubmit) return;
  // payload propre (deep copy) : enlever champs read-only et n'envoyer l'id que pour update
  const payload = JSON.parse(JSON.stringify(form));
  if (props.mode === "add") delete payload.id_type_equipement;
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
