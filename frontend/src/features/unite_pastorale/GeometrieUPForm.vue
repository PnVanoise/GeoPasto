<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <form class="geometrie-up-form" @submit.prevent="submitForm">
    <section class="layout-card">
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-text-field
            v-model="form.properties.date_debut_validite"
            :disabled="props.mode === 'view'"
            label="Début de validité"
            type="date"
            density="compact"
            variant="underlined"
            hide-details
          />
        </div>
        <div class="w3-half form-cell">
          <v-text-field
            v-model="form.properties.date_fin_validite"
            :disabled="props.mode === 'view'"
            label="Fin de validité (vide = en cours)"
            type="date"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
      </div>

      <div class="form-cell map-cell">
        <QuartierGeometryEditorOl
          :key="`geom-up-${form.id ?? 'new'}`"
          v-model="form.geometry"
          geometryType="MultiPolygon"
          :disabled="props.mode === 'view'"
          :drawOnly="props.mode === 'add'"
          :editOnly="props.mode === 'change'"
        />
      </div>
    </section>

    <div class="form-actions">
      <v-btn color="info" @click="emit('close')" prepend-icon="mdi-arrow-left-circle">Retour</v-btn>
      <v-btn
        v-if="props.mode !== 'view'"
        color="success"
        type="submit"
        prepend-icon="mdi-content-save"
        >{{ props.mode === "add" ? "Ajouter" : "Enregistrer" }}</v-btn
      >
    </div>
  </form>
</template>

<script setup>
import { reactive, computed } from "vue";
import QuartierGeometryEditorOl from "@/components/map/QuartierGeometryEditorOl.vue";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" },
  itemLabel: { type: String, required: true },
});

const emit = defineEmits(["close", "submit"]);

const formTitle = computed(() => {
  if (props.mode === "add") return `Ajouter ${props.itemLabel}`;
  if (props.mode === "change") return `Modifier ${props.itemLabel}`;
  return `Détail ${props.itemLabel}`;
});

const form = reactive({
  ...props.initialForm,
  properties: {
    ...(props.initialForm?.properties || {}),
    date_debut_validite: props.initialForm?.properties?.date_debut_validite || "",
    date_fin_validite: props.initialForm?.properties?.date_fin_validite || "",
    unite_pastorale: props.initialForm?.properties?.unite_pastorale || null,
  },
  geometry: props.initialForm?.geometry || null,
});

const submitForm = () => {
  const payload = JSON.parse(JSON.stringify(form));
  if (props.mode === "add") delete payload.id;
  emit("submit", payload);
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
}
.geometrie-up-form :deep(.v-input--density-compact .v-field__input) {
  min-height: 38px;
  padding-top: 6px;
  padding-bottom: 6px;
}
.geometrie-up-form :deep(.v-label.v-field-label) {
  font-size: 0.82rem;
}
.geometrie-up-form :deep(.v-input) {
  font-size: 0.88rem;
}
.geometrie-up-form :deep(.v-field__input) {
  font-size: 0.88rem;
}
.form-ligne {
  padding: 4px;
}
.form-cell {
  padding: 4px;
}
.map-cell {
  min-height: 300px;
  margin-top: 0.5rem;
}
.form-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
}
</style>
