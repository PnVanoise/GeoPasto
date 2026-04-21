<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <!-- <div class="style-switch">
    <v-btn-toggle v-model="visualStyle" density="compact" mandatory variant="outlined" divided>
      <v-btn value="premium" size="small">Premium</v-btn>
      <v-btn value="admin" size="small">Sobre</v-btn>
    </v-btn-toggle>
  </div> -->

  <form :class="['event-form', `theme-${visualStyle}`]" @submit.prevent="submitForm">
    <div class="event-layout">
      <section class="layout-card event-fields-card">
        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-text-field
              id="id_evenement"
              v-model.number="form.id_evenement"
              type="number"
              label="ID"
              :disabled="props.mode === 'view' || autoId"
              :readonly="autoId"
              density="compact"
              variant="underlined"
              hide-details
            />
          </div>
          <div class="w3-half form-cell">
            <v-switch
              v-model="autoId"
              label="ID auto"
              color="primary"
              :disabled="props.mode === 'view' || !canEdit"
              density="compact"
              hide-details
            />
          </div>
        </div>

        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-text-field
              v-model="form.date_evenement"
              type="date"
              label="Date de l'événement"
              :class="{ 'disable-events': props.mode === 'view' || !canEdit }"
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
              :class="{ 'disable-events': props.mode === 'view' || !canEdit }"
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
              :class="{ 'disable-events': props.mode === 'view' || !canEdit }"
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
              :class="{ 'disable-events': props.mode === 'view' || !canEdit }"
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
              :class="{ 'disable-events': props.mode === 'view' || !canEdit }"
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
              :class="{ 'disable-events': props.mode === 'view' || !canEdit }"
              density="compact"
              variant="underlined"
              hide-details
            />
          </div>
        </div>

        <div class="w3-row form-ligne" v-if="showUpSelect">
          <div class="form-cell">
            <v-select
              v-model="form.unite_pastorale"
              :items="ups"
              item-title="nom_up"
              item-value="id_unite_pastorale"
              label="Unité pastorale"
              :menu-props="selectMenuProps"
              :class="{ 'disable-events': props.mode === 'view' || !canEdit }"
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
                <strong>Contexte {{ contextLabel }}</strong>
                <span v-if="contextSituationId">Situation #{{ contextSituationId }}</span>
                <span v-if="effectiveUpId">UP #{{ effectiveUpId }} - {{ getUpName(effectiveUpId) }}</span>
                <span>L'UP finale est calculée automatiquement par le backend selon la géométrie.</span>
              </div>
            </v-alert>
          </div>
        </div>

        <div class="w3-row form-ligne">
          <div class="form-cell">
            <v-textarea
              v-model="form.description"
              label="Description"
              :class="{ 'disable-events': props.mode === 'view' || !canEdit }"
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
            <v-alert type="warning" variant="tonal" density="compact" border="start" icon="mdi-alert-circle-outline">
              Dessinez une géométrie valide ({{ geometryTypeLabel.toLowerCase() }}) avant d'enregistrer.
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
          <label class="map-layer-toggle" v-if="contextSituationId">
            <input type="checkbox" v-model="showQuartiersLayer" />
            Quartiers
          </label>
          <label class="map-layer-toggle" v-if="effectiveUpId">
            <input type="checkbox" v-model="showEvenementsLayer" />
            Événements existants
          </label>
        </div>

        <div class="geometry-status" :class="geometryValidity.isValid ? 'is-set' : 'is-missing'">
          {{ geometryValidity.isValid ? 'Géométrie valide' : 'Géométrie à dessiner' }}
        </div>

        <QuartierGeometryEditorOl
          v-model="form.geometry"
          :geometryType="geometryType"
          :contextLayers="mapContextLayers"
          :disabled="props.mode === 'view' || !canEdit"
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
import auth from "../../auth";
import config from "../../config";
import QuartierGeometryEditorOl from "./QuartierGeometryEditorOl.vue";
import { usePermissions } from "../composables/usePermissions";
import { selectMenuProps } from "../composables/useSelectMenuProps";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" },
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
  contextType: { type: String, default: null },
  contextIds: {
    type: Object,
    default: () => ({ idSituation: null, idUp: null }),
  },
});

const { can } = usePermissions("evenement");

const canEdit = computed(() => {
  if (props.mode === "add") return can("add");
  if (props.mode === "change") return can("change");
  return false;
});

const formTitle = computed(() => {
  if (props.mode === "add") return `Ajouter ${props.itemLabel}`;
  if (props.mode === "change") return `Modifier ${props.itemLabel}`;
  return `Voir les détails d'${props.itemLabel}`;
});

const btTitle = computed(() => (props.mode === "add" ? "Ajouter" : "Enregistrer"));

const form = reactive({
  id_evenement: null,
  date_evenement: "",
  observateur: "",
  date_observation: "",
  source: "",
  description: "",
  geometry: null,
  unite_pastorale: null,
  type_evenement: null,
});

const geometryType = ref("Point");
const geometryTypeOptions = [
  { label: "Point", value: "Point" },
  { label: "Polyligne", value: "LineString" },
  { label: "Polygone", value: "Polygon" },
];

const geometryTypeLabel = computed(() => {
  return geometryTypeOptions.find((item) => item.value === geometryType.value)?.label || "Géométrie";
});

const visualStyle = ref("admin");
const autoId = ref(true);
const submitted = ref(false);
const geometryValidity = ref({ isValid: false, reason: "geometry_required" });

const types = ref([]);
const ups = ref([]);
const quartiersContextGeoData = ref(null);
const evenementsContextGeoData = ref(null);
const upContextGeoData = ref(null);

const showUpLayer = ref(true);
const showQuartiersLayer = ref(true);
const showEvenementsLayer = ref(true);

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
      features: [{ type: "Feature", geometry: payload.geometry, properties: payload.properties || payload }],
    };
  }
  return null;
};

const normalizeContextType = (value) => {
  if (!value) return null;
  const normalized = String(value).toLowerCase();
  if (["situation", "up", "global"].includes(normalized)) return normalized;
  return null;
};

const rawContextType = computed(() => {
  return (
    normalizeContextType(props.contextType)
    || normalizeContextType(props.initialForm?.context_type)
    || normalizeContextType(props.initialForm?.contextType)
    || null
  );
});

const contextSituationId = computed(() => {
  return normalizeFkId(
    props.contextIds?.idSituation
      ?? props.initialForm?.context_id_situation
      ?? props.initialForm?.id_situation
      ?? props.initialForm?.situation_exploitation
      ?? props.initialForm?.contextIds?.idSituation,
    ["id_situation", "id"]
  );
});

const contextUpId = computed(() => {
  return normalizeFkId(
    props.contextIds?.idUp
      ?? props.initialForm?.context_id_up
      ?? props.initialForm?.contextIds?.idUp,
    ["id_unite_pastorale", "id"]
  );
});

const resolvedContextType = computed(() => {
  if (rawContextType.value) return rawContextType.value;
  if (contextSituationId.value) return "situation";
  if (contextUpId.value) return "up";
  return "global";
});

const effectiveUpId = computed(() => {
  return normalizeFkId(form.unite_pastorale, ["id_unite_pastorale", "id"])
    || contextUpId.value
    || null;
});

const contextLabel = computed(() => {
  if (resolvedContextType.value === "situation") return "situation";
  if (resolvedContextType.value === "up") return "UP";
  return "global";
});

const showUpSelect = computed(() => {
  return resolvedContextType.value === "global";
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

const getUpName = (upId) => {
  const up = (ups.value || []).find((item) => Number(item.id_unite_pastorale) === Number(upId));
  return up?.nom_up || "";
};

const onGeometryValidityChange = (payload) => {
  geometryValidity.value = payload || { isValid: false, reason: "geometry_required" };
};

const fetchTypes = async () => {
  try {
    const res = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/typeEvenement/`);
    types.value = res.data || [];
  } catch (err) {
    console.error("Erreur chargement types d'événements", err);
  }
};

const fetchUps = async () => {
  try {
    const res = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/unitePastorale/light/`);
    ups.value = res.data || [];
  } catch (err) {
    console.error("Erreur chargement UP", err);
  }
};

const fetchNextId = async () => {
  if (props.mode !== "add" || !autoId.value) return;
  try {
    const res = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/evenement/getNextId/`);
    form.id_evenement = res.data?.next_id ?? form.id_evenement;
  } catch (err) {
    console.error("Erreur next id événement", err);
  }
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
    console.error("Erreur chargement géométrie UP", err);
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
    console.error("Erreur chargement quartiers de la situation", err);
    quartiersContextGeoData.value = null;
  }
};

const fetchEvenementsContext = async (upId) => {
  if (!upId) {
    evenementsContextGeoData.value = null;
    return;
  }

  try {
    const res = await auth.axiosInstance.get(
      `${config.API_BASE_URL}/api/evenement/?unite_pastorale=${upId}`
    );
    evenementsContextGeoData.value = toFeatureCollection(res.data);
  } catch (err) {
    console.error("Erreur chargement événements de contexte", err);
    evenementsContextGeoData.value = null;
  }
};

watch(
  () => props.initialForm,
  (newVal) => {
    const base = newVal || {};
    const src = base?.properties
      ? { ...base.properties, id_evenement: base.id ?? base.properties.id_evenement }
      : base;

    form.id_evenement = src.id_evenement ?? src.id ?? null;
    form.date_evenement = src.date_evenement ?? "";
    form.observateur = src.observateur ?? "";
    form.date_observation = src.date_observation ?? "";
    form.source = src.source ?? "";
    form.description = src.description ?? "";
    form.type_evenement = normalizeFkId(src.type_evenement, ["id_type_evenement", "id"]);

    const incomingUpId = normalizeFkId(src.unite_pastorale, ["id_unite_pastorale", "id"]);
    form.unite_pastorale = incomingUpId;

    form.geometry = base.geometry ?? src.geometry ?? null;
    geometryType.value = form.geometry?.type || geometryType.value;

    if (props.mode !== "add") autoId.value = false;
  },
  { deep: true, immediate: true }
);

watch(autoId, (enabled) => {
  if (enabled) fetchNextId();
});

watch(
  () => effectiveUpId.value,
  (newUpId) => {
    fetchUnitePastoraleContext(newUpId);
    fetchEvenementsContext(newUpId);
  },
  { immediate: true }
);

watch(
  () => contextSituationId.value,
  (newSituationId) => {
    fetchQuartiersContext(newSituationId);
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

watch(
  [() => resolvedContextType.value, () => contextUpId.value],
  () => {
    if ((resolvedContextType.value === "up" || resolvedContextType.value === "situation") && contextUpId.value) {
      form.unite_pastorale = contextUpId.value;
    }
  },
  { immediate: true }
);

const submitForm = async () => {
  submitted.value = true;

  if (!geometryValidity.value?.isValid) {
    return;
  }

  const payload = {
    id_evenement: form.id_evenement,
    date_evenement: form.date_evenement || null,
    observateur: form.observateur || "",
    date_observation: form.date_observation || null,
    source: form.source || "",
    description: form.description || "",
    geometry: form.geometry ?? null,
    unite_pastorale: effectiveUpId.value || form.unite_pastorale || null,
    type_evenement: form.type_evenement || null,
  };

  return props.onSubmit?.(payload);
};

const closeModal = () => {
  props.onClose?.();
};

onMounted(async () => {
  await Promise.all([fetchTypes(), fetchUps()]);
  await fetchNextId();
});
</script>

<style scoped>
.style-switch {
  display: flex;
  justify-content: flex-end;
  margin: 0 0 0.45rem 0;
}

.form-ligne {
  padding: 4px;
}

.form-cell {
  padding: 4px;
}

.disable-events {
  pointer-events: none;
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
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 0.75rem;
  background: #ffffff;
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

.event-form.theme-premium .layout-card {
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
  border: 1px solid #dbe3ee;
  border-radius: 12px;
  box-shadow:
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 8px 22px rgba(15, 23, 42, 0.06);
  transition: box-shadow 180ms ease, transform 180ms ease, border-color 180ms ease;
}

.event-form.theme-premium .layout-card:hover {
  border-color: #c8d7ea;
  box-shadow:
    0 2px 6px rgba(15, 23, 42, 0.08),
    0 14px 30px rgba(15, 23, 42, 0.08);
  transform: translateY(-1px);
}

.event-form.theme-premium .event-fields-card {
  border-left: 4px solid #0ea5e9;
}

.event-form.theme-premium .event-map-card {
  border-left: 4px solid #22c55e;
}

.event-form.theme-admin .layout-card {
  background: #ffffff;
  border: 1px solid #d7dde6;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
  transition: border-color 140ms ease, box-shadow 140ms ease;
}

.event-form.theme-admin .layout-card:hover {
  border-color: #c8d0db;
  box-shadow: 0 2px 5px rgba(15, 23, 42, 0.08);
}

.event-form.theme-admin .event-fields-card,
.event-form.theme-admin .event-map-card {
  border-left: 3px solid #64748b;
}
</style>
