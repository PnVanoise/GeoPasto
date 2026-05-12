<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>

  <form class="event-form" @submit.prevent="submitForm">
    <div class="event-layout">
      <section class="layout-card event-fields-card">
        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-text-field
              v-model="form.date_evenement"
              type="date"
              label="Date de l'événement"
              :disabled="props.mode === 'view'"
              density="compact"
              variant="underlined"
              hide-details
              required
            />
          </div>
          <div class="w3-half form-cell">
            <v-text-field
              v-model="form.date_observation"
              type="date"
              label="Date d'observation"
              :disabled="props.mode === 'view'"
              density="compact"
              variant="underlined"
              hide-details
              required
            />
          </div>
        </div>

        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-text-field
              v-model="form.observateur"
              label="Observateur"
              :disabled="props.mode === 'view'"
              density="compact"
              variant="underlined"
              hide-details
              required
            />
          </div>
          <div class="w3-half form-cell">
            <v-text-field
              v-model="form.source"
              label="Source"
              :disabled="props.mode === 'view'"
              density="compact"
              variant="underlined"
              hide-details
              clearable
            />
          </div>
        </div>

        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-select
              v-model="form.type_evenement"
              :items="types"
              item-title="description"
              item-value="id_type_evenement"
              label="Type d'événement"
              :menu-props="selectMenuProps"
              :disabled="props.mode === 'view'"
              density="compact"
              variant="underlined"
              hide-details
              clearable
            />
          </div>
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

        <div class="w3-row form-ligne" v-if="!contextSituationId">
          <div class="form-cell">
            <v-select
              v-model="form.situation"
              :items="situations"
              :item-title="situationLabel"
              item-value="id_situation"
              label="Situation d'exploitation"
              :menu-props="selectMenuProps"
              :disabled="props.mode === 'view'"
              density="compact"
              variant="underlined"
              hide-details
              clearable
            />
          </div>
        </div>

        <div class="w3-row form-ligne" v-else>
          <div class="form-cell">
            <v-alert
              type="info"
              variant="tonal"
              density="comfortable"
              border="start"
              icon="mdi-information-outline"
            >
              <div class="context-alert-content">
                <strong>Situation #{{ contextSituationId }}</strong>
              </div>
            </v-alert>
          </div>
        </div>

        <div class="w3-row form-ligne">
          <div class="form-cell">
            <v-textarea
              v-model="form.description"
              label="Description"
              :disabled="props.mode === 'view'"
              density="compact"
              variant="underlined"
              rows="2"
              hide-details
              auto-grow
            />
          </div>
        </div>

        <div class="w3-row form-ligne" v-if="submitted && !geometryValidity.isValid">
          <div class="form-cell">
            <v-alert
              type="warning"
              variant="tonal"
              density="compact"
              border="start"
              icon="mdi-alert-circle-outline"
            >
              Dessinez une géométrie valide ({{ geometryTypeLabel.toLowerCase() }}) avant
              d'enregistrer.
            </v-alert>
          </div>
        </div>
      </section>

      <section class="layout-card event-map-card">
        <div class="map-layer-controls">
          <label class="map-layer-toggle">
            <input type="checkbox" v-model="showUpLayer" />
            UP
          </label>
          <label class="map-layer-toggle" v-if="effectiveSituationId">
            <input type="checkbox" v-model="showQuartiersLayer" />
            Quartiers
          </label>
          <label class="map-layer-toggle" v-if="effectiveSituationId">
            <input type="checkbox" v-model="showEvenementsLayer" />
            Événements existants
          </label>
        </div>

        <div class="geometry-status" :class="geometryValidity.isValid ? 'is-set' : 'is-missing'">
          {{ geometryValidity.isValid ? "Géométrie valide" : "Géométrie à dessiner" }}
        </div>

        <QuartierGeometryEditorOl
          v-model="form.geometry"
          :geometryType="geometryType"
          :contextLayers="mapContextLayers"
          :disabled="props.mode === 'view'"
          @geometry-validity-change="onGeometryValidityChange"
        />

        <div class="map-legend" aria-label="Légende de la carte">
          <div class="map-legend-item" v-if="showUpLayer && mapUpCount > 0">
            <span class="map-legend-swatch map-legend-swatch--up" aria-hidden="true"></span>
            Unité pastorale
          </div>
          <div class="map-legend-item" v-if="showQuartiersLayer && mapQuartierCount > 0">
            <span class="map-legend-swatch map-legend-swatch--quartier" aria-hidden="true"></span>
            Quartiers ({{ mapQuartierCount }})
          </div>
          <div class="map-legend-item" v-if="showEvenementsLayer && mapEventCount > 0">
            <span class="map-legend-swatch map-legend-swatch--evenement" aria-hidden="true"></span>
            Événements ({{ mapEventCount }})
          </div>
        </div>
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
import { computed, onMounted, reactive, ref, watch } from "vue";
import auth from "@/services/axios";
import config from "../../../config";
import QuartierGeometryEditorOl from "../../components/map/QuartierGeometryEditorOl.vue";
import { usePermissions } from "../../composables/usePermissions";
import { selectMenuProps } from "../../composables/useSelectMenuProps";
import { useMainStore } from "../../store/index";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" },
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
  contextIds: {
    type: Object,
    default: () => ({ idSituation: null }),
  },
});

const mainStore = useMainStore();
const { can } = usePermissions("evenement");

const formTitle = computed(() => {
  if (props.mode === "add") return `Ajouter ${props.itemLabel}`;
  if (props.mode === "change") return `Modifier ${props.itemLabel}`;
  return `Voir les détails d'${props.itemLabel}`;
});

const btTitle = computed(() => (props.mode === "add" ? "Ajouter" : "Enregistrer"));

const form = reactive({
  date_evenement: "",
  observateur: "",
  date_observation: "",
  source: "",
  description: "",
  geometry: null,
  situation: null,
  type_evenement: null,
});

const geometryType = ref("Point");
const geometryTypeOptions = [
  { label: "Point", value: "Point" },
  { label: "Polyligne", value: "LineString" },
  { label: "Polygone", value: "Polygon" },
];

const geometryTypeLabel = computed(() => {
  return (
    geometryTypeOptions.find((item) => item.value === geometryType.value)?.label || "Géométrie"
  );
});

const submitted = ref(false);
const geometryValidity = ref({ isValid: false, reason: "geometry_required" });

const types = ref([]);
const situations = ref([]);
const quartiersContextGeoData = ref(null);
const evenementsContextGeoData = ref(null);
const upContextGeoData = ref(null);

const showUpLayer = ref(true);
const showQuartiersLayer = ref(true);
const showEvenementsLayer = ref(true);

const situationLabel = (item) => {
  const parts = [item.annee];
  if (item.exploitant_nom) parts.push(item.exploitant_nom);
  if (item.unite_pastorale_detail?.nom_up) parts.push(item.unite_pastorale_detail.nom_up);
  return parts.join(" — ");
};

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
  if (Array.isArray(payload)) {
    const features = payload
      .map((item) => {
        if (!item) return null;
        if (item.type === "Feature") return item;
        if (!item.geometry) return null;
        return {
          type: "Feature",
          id: item.id ?? item.properties?.id,
          geometry: item.geometry,
          properties: item.properties ?? item,
        };
      })
      .filter(Boolean);
    return { type: "FeatureCollection", features };
  }
  if (payload.geometry) {
    return {
      type: "FeatureCollection",
      features: [
        { type: "Feature", geometry: payload.geometry, properties: payload.properties || payload },
      ],
    };
  }
  return null;
};

const contextSituationId = computed(() => {
  return normalizeFkId(
    props.contextIds?.idSituation ??
      props.initialForm?.context_id_situation ??
      props.initialForm?.id_situation ??
      props.initialForm?.situation_exploitation ??
      props.initialForm?.contextIds?.idSituation,
    ["id_situation", "id"]
  );
});

const effectiveSituationId = computed(() => {
  return normalizeFkId(form.situation, ["id_situation", "id"]) || contextSituationId.value || null;
});

const mapContextLayers = computed(() => {
  const layers = [];

  if (showUpLayer.value && upContextGeoData.value) {
    layers.push({
      id: "up_outline",
      label: "UP",
      data: upContextGeoData.value,
      style: {
        strokeColor: "#b23a2a",
        strokeWidth: 3,
        fillOpacity: 0,
        lineDash: [10, 7],
        pointRadius: 5,
      },
      visible: true,
    });
  }

  if (showQuartiersLayer.value && quartiersContextGeoData.value) {
    layers.push({
      id: "quartiers",
      label: "Quartiers",
      data: quartiersContextGeoData.value,
      style: {
        strokeColor: "#1f6f8b",
        strokeWidth: 2.4,
        fillOpacity: 0.14,
      },
      visible: true,
    });
  }

  if (showEvenementsLayer.value && evenementsContextGeoData.value) {
    layers.push({
      id: "evenements",
      label: "Événements",
      data: evenementsContextGeoData.value,
      style: {
        strokeColor: "#dc2626",
        strokeWidth: 2,
        fillOpacity: 0.12,
        pointShape: "triangle",
        pointRadius: 6.2,
        pointStrokeColor: "#ffffff",
        pointStrokeWidth: 1.1,
      },
      visible: true,
    });
  }

  return layers;
});

const mapQuartierCount = computed(() => {
  const features = quartiersContextGeoData.value?.features || [];
  const ids = new Set(
    features
      .map((f) => f?.properties?.id_quartier ?? f?.id)
      .filter((id) => id != null)
      .map((id) => String(id))
  );
  return ids.size;
});

const mapEventCount = computed(() => {
  const features = evenementsContextGeoData.value?.features || [];
  const ids = new Set(
    features
      .map((f) => f?.properties?.id_evenement ?? f?.id)
      .filter((id) => id != null)
      .map((id) => String(id))
  );
  return ids.size;
});

const mapUpCount = computed(() => {
  const features = upContextGeoData.value?.features || [];
  return Array.isArray(features) ? features.length : 0;
});

const onGeometryValidityChange = (payload) => {
  geometryValidity.value = payload || { isValid: false, reason: "geometry_required" };
};

const fetchTypes = async () => {
  try {
    const res = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/typeEvenement/`);
    types.value = res.data || [];
  } catch (err) {}
};

const fetchSituations = async () => {
  try {
    const res = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/situationExploitation/`);
    situations.value = res.data || [];
  } catch (err) {}
};

const fetchContextFromSituation = async (situationId) => {
  if (!situationId) {
    upContextGeoData.value = null;
    return;
  }
  try {
    const res = await auth.axiosInstance.get(
      `${config.API_BASE_URL}/api/situationExploitation/${situationId}/`
    );
    const upId = res.data?.unite_pastorale;
    if (upId) {
      const upRes = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/unitePastorale/${upId}/`
      );
      upContextGeoData.value = toFeatureCollection(upRes.data);
    } else {
      upContextGeoData.value = null;
    }
  } catch (err) {
    upContextGeoData.value = null;
  }
};

const fetchQuartiersContext = async (situationId) => {
  if (!situationId) {
    quartiersContextGeoData.value = null;
    return;
  }
  try {
    const res = await auth.axiosInstance.get(
      `${config.API_BASE_URL}/api/quartierPasto/?id_situation=${situationId}`
    );
    quartiersContextGeoData.value = toFeatureCollection(res.data);
  } catch (err) {
    quartiersContextGeoData.value = null;
  }
};

const fetchEvenementsContext = async (situationId) => {
  if (!situationId) {
    evenementsContextGeoData.value = null;
    return;
  }
  try {
    const res = await auth.axiosInstance.get(
      `${config.API_BASE_URL}/api/evenement/?situation=${situationId}`
    );
    evenementsContextGeoData.value = toFeatureCollection(res.data);
  } catch (err) {
    evenementsContextGeoData.value = null;
  }
};

watch(
  () => props.initialForm,
  (newVal) => {
    const base = newVal || {};
    const src = base?.properties ? { ...base.properties } : base;

    form.date_evenement = src.date_evenement ?? "";
    const fullName = [mainStore.firstName, mainStore.lastName].filter(Boolean).join(" ");
    form.observateur =
      src.observateur || (props.mode === "add" ? fullName || mainStore.username || "" : "");
    form.date_observation = src.date_observation ?? "";
    form.source = src.source ?? "";
    form.description = src.description ?? "";
    form.type_evenement = normalizeFkId(src.type_evenement, ["id_type_evenement", "id"]);
    form.situation =
      normalizeFkId(src.situation, ["id_situation", "id"]) || contextSituationId.value || null;
    form.geometry = base.geometry ?? src.geometry ?? null;
    geometryType.value = form.geometry?.type || geometryType.value;
  },
  { deep: true, immediate: true }
);

watch(
  () => effectiveSituationId.value,
  (newSituationId) => {
    fetchContextFromSituation(newSituationId);
    fetchQuartiersContext(newSituationId);
    fetchEvenementsContext(newSituationId);
  },
  { immediate: true }
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
  submitted.value = true;

  if (!geometryValidity.value?.isValid) {
    return;
  }

  const payload = {
    date_evenement: form.date_evenement || null,
    observateur: form.observateur || "",
    date_observation: form.date_observation || null,
    source: form.source || "",
    description: form.description || "",
    geometry: form.geometry ?? null,
    situation: effectiveSituationId.value || null,
    type_evenement: form.type_evenement || null,
  };

  return props.onSubmit?.(payload);
};

const closeModal = () => {
  props.onClose?.();
};

onMounted(async () => {
  await Promise.all([fetchTypes(), fetchSituations()]);
});
</script>

<style scoped>
.form-ligne {
  padding: 4px;
}

.form-cell {
  padding: 4px;
}

.event-layout {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.05fr);
  grid-template-areas: "fields map";
  gap: 1rem;
  align-items: start;
  margin-top: 1rem;
}

.event-fields-card {
  grid-area: fields;
  min-width: 0;
}

.event-map-card {
  grid-area: map;
  min-width: 0;
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

.context-alert-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
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

.map-layer-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin: 0 0 0.45rem 0;
}

.map-layer-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  color: #334155;
}

.map-legend {
  margin-top: 0.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
  font-size: 0.8rem;
  color: #334155;
}

.map-legend-item {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.map-legend-swatch {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 3px;
  border: 2px solid transparent;
}

.map-legend-swatch--quartier {
  border-color: #1f6f8b;
  background: rgba(31, 111, 139, 0.16);
}

.map-legend-swatch--up {
  border-color: #b23a2a;
  border-style: dashed;
  background: transparent;
}

.map-legend-swatch--evenement {
  border-radius: 0;
  border-color: #ffffff;
  border-width: 1px;
  background: rgba(220, 38, 38, 0.9);
  clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
}

.event-form :deep(.v-input--density-compact .v-field__input) {
  min-height: 38px;
  padding-top: 6px;
  padding-bottom: 6px;
}

.event-form :deep(.v-label.v-field-label) {
  font-size: 0.82rem;
}

.event-form :deep(.v-input) {
  font-size: 0.88rem;
}

.event-form :deep(.v-field__input),
.event-form :deep(.v-select__selection-text) {
  font-size: 0.88rem;
}

.form-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

@media (max-width: 1100px) {
  .event-layout {
    grid-template-columns: 1fr;
    grid-template-areas:
      "fields"
      "map";
  }
}
</style>
