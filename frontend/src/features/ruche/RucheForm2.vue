<template>
  <h3 class="w3-center w3-margin">{{ formTitle }}</h3>
  <form class="ruche-form" @submit.prevent="submitForm">
    <div class="ruche-layout">
      <section class="layout-card">
        <div class="w3-row form-ligne">
          <div class="w3-col s12 form-cell">
            <v-text-field
              v-model="form.description"
              label="Description"
              :disabled="props.mode === 'view'"
              density="compact"
              variant="outlined"
              hide-details
              required
            />
          </div>
        </div>
        <div class="w3-row form-ligne">
          <div class="w3-col s12 form-cell">
            <v-select
              v-model="form.situation_exploitation"
              :items="situations"
              item-title="nom_situation"
              item-value="id_situation"
              label="Situation d'exploitation"
              :menu-props="selectMenuProps"
              :disabled="props.mode === 'view'"
              density="compact"
              variant="outlined"
              hide-details
              clearable
            />
          </div>
        </div>
      </section>

      <section class="layout-card">
        <h4 class="map-title">Position de la ruche</h4>
        <div class="geometry-status" :class="hasGeometry ? 'is-set' : 'is-missing'">
          {{ hasGeometry ? "Position définie" : "Position non définie" }}
        </div>
        <QuartierGeometryEditorOl
          v-model="form.geometry"
          geometryType="Point"
          :disabled="props.mode === 'view'"
        />
      </section>
    </div>

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
import { computed, reactive, ref, watch, onMounted } from "vue";
import config from "../../../config";
import auth from "@/services/axios";
import QuartierGeometryEditorOl from "../../components/map/QuartierGeometryEditorOl.vue";
import { selectMenuProps } from "../../composables/useSelectMenuProps";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" },
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const formTitle = computed(() => {
  if (props.mode === "add") return `Ajouter ${props.itemLabel}`;
  if (props.mode === "change") return `Modifier ${props.itemLabel}`;
  return `Voir les détails d'${props.itemLabel}`;
});
const btTitle = computed(() => (props.mode === "add" ? "Ajouter" : "Enregistrer"));
const hasGeometry = computed(() => {
  const g = form.geometry;
  return g?.type === "Point" && Array.isArray(g.coordinates) && g.coordinates.length >= 2;
});

const situations = ref([]);

const form = reactive({
  id: null,
  description: "",
  situation_exploitation: null,
  geometry: null,
});

watch(
  () => props.initialForm,
  (newVal) => {
    const base = newVal || {};
    const src = base.properties ? { ...base.properties } : base;
    form.id = base.id ?? src.id ?? null;
    form.description = src.description ?? "";
    form.situation_exploitation = src.situation_exploitation ?? null;
    form.geometry = base.geometry ?? src.geometry ?? null;
  },
  { deep: true, immediate: true }
);

const submitForm = () => {
  props.onSubmit?.({ ...form }).catch((err) => console.error("Erreur soumission ruche", err));
};

const closeModal = () => props.onClose?.();

onMounted(async () => {
  try {
    const res = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/situationExploitation/`);
    situations.value = res.data || [];
  } catch (err) {
    console.error("Erreur chargement situations", err);
  }
});
</script>

<style scoped>
.ruche-layout {
  display: grid;
  grid-template-columns: minmax(260px, 380px) 1fr;
  gap: 16px;
  align-items: start;
}

.layout-card {
  background: #ffffff;
  border: 1px solid #d7dde6;
  border-left: 3px solid #64748b;
  border-radius: 8px;
  padding: 0.75rem;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}

.map-title {
  margin: 0 0 10px;
  font-size: 1rem;
  font-weight: 600;
}

.geometry-status {
  display: inline-block;
  margin: 0 0 10px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
}
.geometry-status.is-set {
  color: #166534;
  background: #dcfce7;
  border: 1px solid #86efac;
}
.geometry-status.is-missing {
  color: #92400e;
  background: #fef3c7;
  border: 1px solid #fcd34d;
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
  gap: 0.5rem;
  margin-top: 1.2rem;
}

@media (max-width: 900px) {
  .ruche-layout {
    grid-template-columns: 1fr;
  }
}
</style>
