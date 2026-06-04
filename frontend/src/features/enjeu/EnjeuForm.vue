<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <form class="enjeu-form" @submit.prevent="submitForm">
    <section class="layout-card">
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-text-field
            v-model="form.description"
            :disabled="props.mode === 'view'"
            label="Description"
            density="compact"
            variant="underlined"
            hide-details="auto"
            :rules="[maxLen(150)]"
            :counter="150"
            clearable
          />
        </div>
      </div>
    </section>

    <div class="form-actions">
      <v-btn color="info" @click="closeModal" prepend-icon="mdi-arrow-left-circle">Retour</v-btn>
      <v-btn
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
import { reactive, watch, computed } from "vue";
import { usePermissions } from "../../composables/usePermissions";
import { maxLen } from "@/utils/validators";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" },
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("enjeu");

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
  id_enjeu: null,
  description: "",
});

watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) {
      form.id_enjeu = newVal.id_enjeu ?? null;
      form.description = newVal.description ?? "";
    }
  },
  { immediate: true }
);

const isFormValid = computed(() => !!form.description?.trim());

const submitForm = () => {
  if (!props.onSubmit) return;
  const payload = { description: form.description };
  if (props.mode === "change") payload.id_enjeu = form.id_enjeu;
  props.onSubmit(payload);
};

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
.enjeu-form :deep(.v-input--density-compact .v-field__input) {
  min-height: 38px;
  padding-top: 6px;
  padding-bottom: 6px;
}
.enjeu-form :deep(.v-label.v-field-label) {
  font-size: 0.82rem;
}
.enjeu-form :deep(.v-input) {
  font-size: 0.88rem;
}
.enjeu-form :deep(.v-field__input),
.enjeu-form :deep(.v-select__selection-text) {
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
</style>
