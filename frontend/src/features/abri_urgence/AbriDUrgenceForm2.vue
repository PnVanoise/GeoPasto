<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <form class="abri-urgence-form" @submit.prevent="submitForm">
    <section class="layout-card">
      <div class="w3-row form-ligne">
        <div class="form-cell">
          <v-text-field
            v-model="form.description"
            label="Description"
            :disabled="props.mode === 'view'"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
      </div>
      <div class="w3-row form-ligne">
        <div class="form-cell">
          <v-text-field
            v-model="form.etat"
            label="État de l'abri"
            :disabled="props.mode === 'view'"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
      </div>
    </section>

    <section class="layout-card" style="margin-top: 1rem">
      <h4 class="section-title">Commodités associées</h4>
      <template v-if="props.mode === 'add'">
        <div class="w3-panel w3-pale-yellow info-panel">
          Enregistrez l'abri d'urgence pour pouvoir ajouter des commodités.
        </div>
      </template>
      <template v-else>
        <CrudList2
          title="Commodités"
          modelName="abridurgencecommodite"
          apiRouteName="abriDUrgenceCommodite"
          itemLabel="une commodité d'abri"
          idField="id_abri_urgence_commodite"
          :columns="commGridColumns"
          :formComponent="AbriDUrgenceCommoditeForm"
          :bgColor="'#154889'"
          :filters="commFilters"
          :showTitle="false"
          :showHeader="true"
          :showSearch="true"
          :showFilters="false"
          :forceAdd="false"
          :viewOnly="props.mode === 'view'"
          :initialNewItem="{ abri_urgence: form.id_abri_urgence }"
        />
      </template>
    </section>

    <div class="form-actions">
      <v-btn color="info" @click="closeModal" prepend-icon="mdi-arrow-left-circle">Retour</v-btn>
      <v-btn
        v-if="props.mode !== 'view'"
        color="success"
        type="submit"
        prepend-icon="mdi-content-save"
      >
        {{ btTitle }}
      </v-btn>
    </div>
  </form>
</template>

<script setup>
import { reactive, watch, ref, computed } from "vue";
import { usePermissions } from "../../composables/usePermissions";
import CrudList2 from "../../components/crud/CrudList2.vue";
import AbriDUrgenceCommoditeForm from "./AbriDUrgenceCommoditeForm.vue";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" },
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("abridurgence");

const formTitle = computed(() => {
  if (props.mode === "add") return `Ajouter ${props.itemLabel}`;
  if (props.mode === "change") return `Modifier ${props.itemLabel}`;
  return `Voir les détails d'${props.itemLabel}`;
});

const btTitle = computed(() => (props.mode === "add" ? "Ajouter" : "Enregistrer"));

const form = reactive({
  description: "",
  etat: "",
});

const commGridColumns = ref([
  { field: "commodite_desc", label: "Commodité", sortable: true },
  { field: "etat", label: "État", sortable: true },
  { field: "quantite", label: "Quantité", sortable: true },
]);

const commFilters = ref([
  {
    key: "abriFilter",
    type: "hidden",
    default: "",
    apply: (items, _value) => {
      if (!form.id_abri_urgence) return [];
      return (items || []).filter((i) => i.abri_urgence === form.id_abri_urgence);
    },
  },
]);

watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) Object.assign(form, newVal);
  },
  { immediate: true }
);

const submitForm = () => {
  props.onSubmit?.(form).catch((err) => console.error(err));
};

const closeModal = () => props.onClose?.();
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
.abri-urgence-form :deep(.v-input--density-compact .v-field__input) {
  min-height: 38px;
  padding-top: 6px;
  padding-bottom: 6px;
}
.abri-urgence-form :deep(.v-label.v-field-label) {
  font-size: 0.82rem;
}
.abri-urgence-form :deep(.v-input) {
  font-size: 0.88rem;
}
.abri-urgence-form :deep(.v-field__input),
.abri-urgence-form :deep(.v-select__selection-text) {
  font-size: 0.88rem;
}
.form-ligne {
  padding: 4px;
}
.form-cell {
  padding: 4px;
}
.section-title {
  margin: 0 0 0.5rem;
  font-size: 0.95rem;
  font-weight: 600;
}
.info-panel {
  padding: 12px;
  border: 1px solid #ddd;
}
.form-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
}
</style>
