<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>

  <v-form ref="formRef" class="event-form" @submit.prevent="submitForm">
    <div class="event-layout">
      <section class="layout-card event-fields-card">
        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-text-field
              v-model="form.date_evenement"
              type="date"
              label="Date de l'événement"
              :disabled="props.mode === 'view'"
              class="required"
              density="compact"
              variant="underlined"
              hide-details="auto"
              :rules="[required]"
            />
          </div>
          <div class="w3-half form-cell">
            <v-text-field
              v-model="form.date_observation"
              type="date"
              label="Date d'observation"
              :disabled="props.mode === 'view'"
              class="required"
              density="compact"
              variant="underlined"
              hide-details="auto"
              :rules="[required]"
            />
          </div>
        </div>

        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-text-field
              v-model="form.observateur"
              label="Observateur"
              :disabled="props.mode === 'view'"
              class="required"
              density="compact"
              variant="underlined"
              hide-details="auto"
              :rules="[required]"
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
              class="required"
              density="compact"
              variant="underlined"
              rows="2"
              hide-details="auto"
              :rules="[required, maxLen(150)]"
              :counter="150"
              auto-grow
            />
          </div>
        </div>
        <div class="w3-row form-ligne">
          <div class="form-cell">
            <v-textarea
              v-model="form.commentaire"
              label="Commentaire"
              :disabled="props.mode === 'view'"
              density="compact"
              variant="underlined"
              rows="2"
              hide-details
              auto-grow
              clearable
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

        <div v-if="props.mode !== 'view'" class="import-section">
          <button type="button" class="import-toggle" @click="showImport = !showImport">
            <v-icon size="16">{{ showImport ? "mdi-chevron-up" : "mdi-chevron-down" }}</v-icon>
            Importer depuis QGIS
          </button>
          <div v-if="showImport" class="import-panel">
            <v-textarea
              v-model="importText"
              label="Coller la géométrie copiée depuis QGIS (WKT ou GeoJSON)"
              density="compact"
              variant="outlined"
              hide-details
              rows="4"
              auto-grow
              class="import-textarea"
            />
            <div class="import-actions">
              <span v-if="importInfo" class="import-info">{{ importInfo }}</span>
              <span v-if="importError" class="import-error">{{ importError }}</span>
              <v-btn
                color="primary"
                size="small"
                prepend-icon="mdi-import"
                @click="importerGeometrie"
                >Importer</v-btn
              >
            </div>
          </div>
        </div>

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
        :disabled="formRef?.isValid === false"
      >
        {{ btTitle }}
      </v-btn>
    </div>
  </v-form>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import proj4 from "proj4";
import { register } from "ol/proj/proj4";
import WKT from "ol/format/WKT";
import GeoJSON from "ol/format/GeoJSON";
import auth from "@/services/axios";
import config from "../../../config";
import QuartierGeometryEditorOl from "../../components/map/QuartierGeometryEditorOl.vue";

proj4.defs(
  "EPSG:2154",
  "+proj=lcc +lat_0=46.5 +lon_0=3 +lat_1=49 +lat_2=44 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
);
register(proj4);
import { usePermissions } from "../../composables/usePermissions";
import { selectMenuProps } from "../../composables/useSelectMenuProps";
import { useMainStore } from "../../store/index";
import { maxLen, required } from "@/utils/validators";

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

const formRef = ref(null);

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
  commentaire: "",
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
  const parts = [];
  if (item.date_debut) parts.push(String(new Date(item.date_debut).getFullYear()));
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
    form.commentaire = src.commentaire ?? "";
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

const showImport = ref(false);
const importText = ref("");
const importError = ref("");
const importInfo = ref("");
const detectedCrs = ref("");

const CRS_LABELS = {
  "EPSG:4326": "WGS84 (EPSG:4326)",
  "EPSG:2154": "Lambert 93 (EPSG:2154)",
  "EPSG:3857": "Web Mercator (EPSG:3857)",
};

const detectCrsFromCoords = (x, y) => {
  if (Math.abs(x) <= 180 && Math.abs(y) <= 90) return "EPSG:4326";
  if (x > 70000 && x < 1300000 && y > 6000000 && y < 7200000) return "EPSG:2154";
  return "EPSG:3857";
};

watch(importText, (text) => {
  importError.value = "";
  const trimmed = text?.trim();
  if (!trimmed || trimmed.startsWith("{")) {
    detectedCrs.value = "";
    importInfo.value = "";
    return;
  }
  const coordMatch = trimmed.match(/\(\s*([-\d.]+)\s+([-\d.]+)/);
  if (!coordMatch) {
    detectedCrs.value = "";
    importInfo.value = "";
    return;
  }
  const crs = detectCrsFromCoords(parseFloat(coordMatch[1]), parseFloat(coordMatch[2]));
  detectedCrs.value = crs;
  importInfo.value = `Projection détectée : ${CRS_LABELS[crs]}`;
});

const importerGeometrie = () => {
  importError.value = "";
  const text = importText.value.trim();
  if (!text) {
    importError.value = "Collez une géométrie WKT ou GeoJSON.";
    return;
  }
  try {
    let geometry;
    if (text.startsWith("{")) {
      const parsed = JSON.parse(text);
      if (parsed.type === "FeatureCollection") {
        geometry = parsed.features?.[0]?.geometry ?? null;
      } else if (parsed.type === "Feature") {
        geometry = parsed.geometry;
      } else {
        geometry = parsed;
      }
      if (!geometry?.type) throw new Error("GeoJSON invalide.");
    } else {
      const effectiveCrs = detectedCrs.value || "EPSG:4326";
      const olFeature = new WKT().readFeature(text, {
        dataProjection: effectiveCrs,
        featureProjection: "EPSG:4326",
      });
      if (!olFeature) throw new Error("WKT invalide.");
      geometry = new GeoJSON().writeGeometryObject(olFeature.getGeometry());
    }
    form.geometry = geometry;
    showImport.value = false;
    importText.value = "";
  } catch (e) {
    importError.value = e.message || "Format non reconnu (WKT ou GeoJSON attendu).";
  }
};

const submitForm = async () => {
  submitted.value = true;
  const { valid } = await formRef.value.validate();
  if (!valid) return;

  if (!geometryValidity.value?.isValid) {
    return;
  }

  const payload = {
    date_evenement: form.date_evenement || null,
    observateur: form.observateur || "",
    date_observation: form.date_observation || null,
    source: form.source || "",
    description: form.description || "",
    commentaire: form.commentaire || null,
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

.import-section {
  margin-top: 0.75rem;
  border-top: 1px solid #e2e8f0;
  padding-top: 0.5rem;
}
.import-toggle {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.82rem;
  color: #475569;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 0;
}
.import-toggle:hover {
  color: #1e40af;
}
.import-panel {
  margin-top: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.import-textarea :deep(.v-field__input) {
  font-size: 0.78rem;
  font-family: monospace;
}
.import-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}
.import-error {
  font-size: 0.78rem;
  color: #dc2626;
}
.import-info {
  font-size: 0.78rem;
  color: #2563eb;
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
