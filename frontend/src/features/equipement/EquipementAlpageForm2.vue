<template>
  <h3 class="w3-center w3-margin">{{ formTitle }}</h3>

  <form class="eqpt-form" @submit.prevent="submitForm">
    <div class="eqpt-layout">
      <section class="layout-card">
        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
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
          <div class="w3-half form-cell">
            <v-text-field
              v-model="form.etat"
              label="État"
              :disabled="props.mode === 'view'"
              density="compact"
              variant="outlined"
              hide-details
              required
            />
          </div>
        </div>

        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-select
              v-model="form.type_equipement"
              :items="typesEquipement"
              item-title="description"
              item-value="id_type_equipement"
              label="Type équipement"
              :menu-props="selectMenuProps"
              :disabled="props.mode === 'view'"
              density="compact"
              variant="outlined"
              hide-details
              clearable
            />
          </div>
          <div class="w3-half form-cell">
            <v-select
              v-model="form.unite_pastorale"
              :items="ups"
              item-title="nom_up"
              item-value="id_unite_pastorale"
              label="Unité pastorale"
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
        <h4 class="map-title">Position de l'équipement</h4>
        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-select
              v-model="geometryType"
              :items="geometryTypeOptions"
              item-title="label"
              item-value="value"
              label="Type géométrie"
              :menu-props="selectMenuProps"
              :disabled="props.mode === 'view'"
              density="compact"
              variant="underlined"
              hide-details
            />
          </div>
        </div>
        <div class="geometry-status" :class="hasGeometry ? 'is-set' : 'is-missing'">
          {{ hasGeometry ? "Géométrie définie" : "Géométrie à dessiner" }}
        </div>
        <QuartierGeometryEditorOl
          v-model="form.geometry"
          :geometryType="geometryType"
          :contextGeoData="upContextGeoData"
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
        >{{ btTitle }}</v-btn
      >
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
  return `Voir les details d'${props.itemLabel}`;
});

const btTitle = computed(() => (props.mode === "add" ? "Ajouter" : "Enregistrer"));
const hasGeometry = computed(() => {
  const geom = form.geometry;
  if (!geom || !geom.type) return false;
  return Array.isArray(geom.coordinates) && geom.coordinates.length > 0;
});

const geometryType = ref("Point");
const geometryTypeOptions = [
  { label: "Point", value: "Point" },
  { label: "Polyligne", value: "LineString" },
  { label: "Polygone", value: "Polygon" },
];

const typesEquipement = ref([]);
const ups = ref([]);
const upContextGeoData = ref(null);

const form = reactive({
  description: "",
  etat: "",
  type_equipement: null,
  unite_pastorale: null,
  geometry: null,
});

const closeModal = () => props.onClose?.();

const normalizeFkId = (value, candidateKeys = []) => {
  if (value == null || value === "") return null;

  if (typeof value === "object") {
    for (const key of candidateKeys) {
      if (value[key] != null && value[key] !== "") {
        const nested = Number(value[key]);
        return Number.isFinite(nested) && nested > 0 ? nested : null;
      }
    }
    return null;
  }

  const numeric = Number(value);
  if (!Number.isFinite(numeric) || numeric <= 0) return null;
  return numeric;
};

const toFeatureCollection = (payload) => {
  if (!payload) return null;
  if (payload.type === "FeatureCollection" && Array.isArray(payload.features)) return payload;
  if (payload.type === "Feature") return { type: "FeatureCollection", features: [payload] };
  if (payload.geometry) {
    return {
      type: "FeatureCollection",
      features: [
        { type: "Feature", geometry: payload.geometry, properties: payload.properties || {} },
      ],
    };
  }
  return null;
};

const fetchUnitePastoraleContext = async (upId) => {
  if (!upId) {
    upContextGeoData.value = null;
    return;
  }

  try {
    const res = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/unitePastorale/${upId}/`);
    upContextGeoData.value = toFeatureCollection(res.data);
  } catch (err) {
    upContextGeoData.value = null;
  }
};

watch(
  () => form.unite_pastorale,
  (newUpId) => {
    fetchUnitePastoraleContext(newUpId);
  }
);

watch(
  () => props.initialForm,
  (newVal) => {
    const base = newVal || {};
    const src = base?.properties ? { ...base.properties } : base;

    form.description = src.description ?? "";
    form.etat = src.etat ?? "";
    form.type_equipement = normalizeFkId(src.type_equipement ?? src.type_equipement_detail, [
      "id_type_equipement",
      "id",
    ]);
    form.unite_pastorale = normalizeFkId(src.unite_pastorale ?? src.unite_pastorale_detail, [
      "id_unite_pastorale",
      "id",
    ]);
    form.geometry = base.geometry ?? src.geometry ?? null;
    geometryType.value = form.geometry?.type || "Point";
  },
  { deep: true, immediate: true }
);

watch(
  () => geometryType.value,
  (newType) => {
    if (!newType) return;
    if (form.geometry?.type && form.geometry.type !== newType) {
      form.geometry = null;
    }
  }
);

const submitForm = async () => {
  const payload = {
    description: form.description,
    etat: form.etat,
    type_equipement: form.type_equipement,
    unite_pastorale: form.unite_pastorale,
    geometry: form.geometry ?? null,
  };
  return props.onSubmit?.(payload);
};

onMounted(async () => {
  try {
    const [typeRes, upRes] = await Promise.all([
      auth.axiosInstance.get(`${config.API_BASE_URL}/api/typeEquipement/?categorie=Alpage`),
      auth.axiosInstance.get(`${config.API_BASE_URL}/api/unitePastorale/light/`),
    ]);
    typesEquipement.value = typeRes.data || [];
    ups.value = upRes.data || [];
  } catch (err) {}

  if (form.unite_pastorale) {
    await fetchUnitePastoraleContext(form.unite_pastorale);
  }
});
</script>

<style scoped>
.eqpt-layout {
  display: grid;
  grid-template-columns: minmax(280px, 420px) 1fr;
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
  transition:
    border-color 140ms ease,
    box-shadow 140ms ease;
}

.layout-card:hover {
  border-color: #c8d0db;
  box-shadow: 0 2px 5px rgba(15, 23, 42, 0.08);
}

.eqpt-form :deep(.v-input--density-compact .v-field__input) {
  min-height: 38px;
  padding-top: 6px;
  padding-bottom: 6px;
}

.eqpt-form :deep(.v-label.v-field-label) {
  font-size: 0.82rem;
}

.eqpt-form :deep(.v-input) {
  font-size: 0.88rem;
}

.eqpt-form :deep(.v-field__input),
.eqpt-form :deep(.v-select__selection-text) {
  font-size: 0.88rem;
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
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.2rem;
}

@media (max-width: 1000px) {
  .eqpt-layout {
    grid-template-columns: 1fr;
  }
}
</style>
