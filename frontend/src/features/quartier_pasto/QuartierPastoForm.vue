<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>

  <v-form class="quartier-form" @submit.prevent="submitForm">
    <div class="quartier-layout">
      <section class="layout-card fields-card">
        <v-text-field
          v-model="form.properties.code_quartier"
          label="Code quartier"
          variant="underlined"
          density="comfortable"
          required
        />

        <v-text-field
          v-model="form.properties.nom_quartier"
          label="Nom quartier"
          variant="underlined"
          density="comfortable"
          required
        />

        <v-select
          v-model="form.properties.situation_exploitation"
          :items="situations"
          item-title="nom_situation"
          item-value="id_situation"
          label="Situation d'exploitation"
          variant="underlined"
          density="comfortable"
          clearable
        />
      </section>

      <section class="layout-card map-card">
        <h4 class="map-title">Géométrie du quartier</h4>
        <v-alert
          v-if="geometryError"
          type="error"
          variant="tonal"
          density="compact"
          class="geometry-alert"
        >
          Dessinez d'abord la géométrie du quartier (double-clic pour terminer le polygone), puis
          enregistrez.
        </v-alert>
        <v-alert
          v-if="splitError"
          type="error"
          variant="tonal"
          density="compact"
          class="geometry-alert"
        >
          {{ splitError }}
        </v-alert>
        <v-alert
          v-if="splitSuccess"
          type="success"
          variant="tonal"
          density="compact"
          class="geometry-alert"
        >
          Quartier découpé avec succès. Redirection en cours…
        </v-alert>
        <QuartierGeometryEditorOl
          ref="geometryEditorRef"
          v-model="form.geometry"
          :geometryType="'MultiPolygon'"
          :contextLayers="contextLayers"
          :drawOnly="!props.isEdit"
          :editOnly="props.isEdit"
          :allowSplit="props.isEdit"
          @split-line="handleSplitLine"
        />

        <div v-if="resolvedMode !== 'view'" class="import-section">
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
      </section>
    </div>

    <div class="actions-row">
      <v-btn
        density="comfortable"
        color="info"
        prepend-icon="mdi-arrow-left-circle"
        @click="closeForm"
        >Retour</v-btn
      >
      <v-btn density="comfortable" color="success" type="submit" prepend-icon="mdi-content-save"
        >Enregistrer</v-btn
      >
    </div>
  </v-form>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
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

const resolvedMode = computed(() => {
  if (props.mode === "add" || props.mode === "change" || props.mode === "view") {
    return props.mode;
  }
  return props.isEdit ? "change" : "add";
});

const props = defineProps({
  initialForm: Object,
  mode: { type: String, default: null },
  isEdit: Boolean,
  onSubmit: Function,
  onClose: Function,
  onSplitSuccess: Function,
  itemLabel: { type: String, default: "un quartier pastoral" },
});

const formTitle = computed(() => {
  if (resolvedMode.value === "add") return `Ajouter ${props.itemLabel}`;
  if (resolvedMode.value === "change") return `Modifier ${props.itemLabel}`;
  return `Voir les détails de ${props.itemLabel}`;
});

const closeForm = () => props.onClose?.();

const ups = ref([]);
const situations = ref([]);
const contextQuartiersGeoData = ref(null);
const upGeoData = ref(null);

const contextLayers = computed(() => {
  const layers = [];
  if (contextQuartiersGeoData.value) {
    layers.push({
      id: "quartiers",
      data: contextQuartiersGeoData.value,
      visible: true,
      style: { strokeColor: "#1565C0", strokeWidth: 1.4, lineDash: [10, 6], fillOpacity: 0.15 },
    });
  }
  if (upGeoData.value) {
    layers.push({
      id: "up",
      data: upGeoData.value,
      visible: true,
      style: { strokeColor: "#2E7D32", strokeWidth: 2, fillOpacity: 0.07 },
    });
  }
  return layers;
});

const fetchUpGeometry = async (upId) => {
  if (!upId) {
    upGeoData.value = null;
    return;
  }
  try {
    const response = await auth.axiosInstance.get(
      `${config.API_BASE_URL}/api/unitePastorale/${upId}/`
    );
    const feature = response.data;
    if (feature?.geometry) {
      upGeoData.value = {
        type: "FeatureCollection",
        features: [
          { type: "Feature", geometry: feature.geometry, properties: feature.properties || {} },
        ],
      };
    } else {
      upGeoData.value = null;
    }
  } catch (e) {
    upGeoData.value = null;
  }
};

const normalizeForm = (src) => {
  const base = src || {};
  const propsData = base.properties || {};
  const quartierId = base.id ?? base.id_quartier ?? propsData.id_quartier ?? propsData.id ?? null;

  return {
    ...base,
    id: quartierId,
    id_quartier: quartierId,
    properties: {
      ...propsData,
      id_quartier: quartierId,
      code_quartier: propsData.code_quartier ?? base.code_quartier ?? "",
      nom_quartier: propsData.nom_quartier ?? base.nom_quartier ?? "",
      unite_pastorale: propsData.unite_pastorale ?? base.unite_pastorale ?? null,
      situation_exploitation:
        propsData.situation_exploitation ?? base.situation_exploitation ?? null,
    },
    geometry: base.geometry || null,
  };
};

const normalizeContextQuartiers = (payload) => {
  if (!payload) return null;

  if (payload.type === "FeatureCollection" && Array.isArray(payload.features)) {
    return payload;
  }

  if (payload.type === "Feature") {
    return { type: "FeatureCollection", features: [payload] };
  }

  if (Array.isArray(payload)) {
    return { type: "FeatureCollection", features: payload.filter(Boolean) };
  }

  if (payload?.results && Array.isArray(payload.results)) {
    return normalizeContextQuartiers(payload.results);
  }

  return null;
};

const form = ref(normalizeForm(props.initialForm));
const geometryEditorRef = ref(null);
const geometryError = ref(false);
const splitError = ref(null);
const splitSuccess = ref(false);

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
    form.value.geometry = geometry;
    showImport.value = false;
    importText.value = "";
  } catch (e) {
    importError.value = e.message || "Format non reconnu (WKT ou GeoJSON attendu).";
  }
};

const normalizeQuartiersGeoData = (payload) => {
  if (!payload) return null;

  if (payload?.results && Array.isArray(payload.results)) {
    return normalizeQuartiersGeoData(payload.results);
  }

  if (payload.type === "FeatureCollection" && Array.isArray(payload.features)) {
    return payload;
  }

  if (payload.type === "Feature") {
    return { type: "FeatureCollection", features: [payload] };
  }

  if (Array.isArray(payload)) {
    const features = payload
      .map((item) => {
        if (!item) return null;
        if (item.type === "Feature") return item;
        if (!item.geometry) return null;

        return {
          type: "Feature",
          id: item.id_quartier ?? item.id ?? item.properties?.id_quartier,
          geometry: item.geometry,
          properties: item.properties ?? item,
        };
      })
      .filter(Boolean);

    return { type: "FeatureCollection", features };
  }

  return null;
};

const normalizeComparableId = (rawId) => {
  if (rawId == null) return null;
  const str = String(rawId);
  if (str.includes(":")) return str.split(":").pop();
  return str;
};

const getCurrentQuartierId = () => {
  return (
    form.value?.id ??
    form.value?.id_quartier ??
    form.value?.properties?.id_quartier ??
    props.initialForm?.id ??
    props.initialForm?.id_quartier ??
    props.initialForm?.properties?.id_quartier ??
    null
  );
};

const fetchContextQuartiersForSituation = async (situationId) => {
  const fromProps = normalizeContextQuartiers(props.initialForm?.context_quartiers_geojson);
  if (fromProps && Array.isArray(fromProps.features)) {
    const currentId = getCurrentQuartierId();
    contextQuartiersGeoData.value = {
      type: "FeatureCollection",
      features: fromProps.features
        .filter((feature) => {
          const rawId = feature?.id ?? feature?.properties?.id_quartier ?? feature?.properties?.id;
          if (currentId == null || rawId == null) return true;
          return normalizeComparableId(rawId) !== normalizeComparableId(currentId);
        })
        .filter((feature) => feature?.geometry)
        .map((feature) => {
          const rawId = feature?.id ?? feature?.properties?.id_quartier ?? feature?.properties?.id;
          return {
            ...feature,
            id: rawId != null ? `quartier_context:${normalizeComparableId(rawId)}` : undefined,
            properties: {
              ...(feature?.properties || {}),
              id_quartier: normalizeComparableId(rawId) ?? feature?.properties?.id_quartier,
            },
          };
        }),
    };
    return;
  }

  if (!situationId) {
    contextQuartiersGeoData.value = null;
    return;
  }

  try {
    const response = await auth.axiosInstance.get(
      `${config.API_BASE_URL}/api/quartierPasto/?id_situation=${situationId}`
    );

    const normalized = normalizeQuartiersGeoData(response.data);
    const currentId = getCurrentQuartierId();

    const features = (normalized?.features || [])
      .filter((feature) => {
        const rawId = feature?.id ?? feature?.properties?.id_quartier ?? feature?.properties?.id;
        if (currentId == null || rawId == null) return true;
        return normalizeComparableId(rawId) !== normalizeComparableId(currentId);
      })
      .filter((feature) => feature?.geometry)
      .map((feature) => {
        const rawId = feature?.id ?? feature?.properties?.id_quartier ?? feature?.properties?.id;
        return {
          ...feature,
          id: rawId != null ? `quartier_context:${normalizeComparableId(rawId)}` : undefined,
          properties: {
            ...(feature?.properties || {}),
            id_quartier: normalizeComparableId(rawId) ?? feature?.properties?.id_quartier,
          },
        };
      });

    contextQuartiersGeoData.value = {
      type: "FeatureCollection",
      features,
    };
  } catch (error) {
    contextQuartiersGeoData.value = null;
  }
};

const handleSplitLine = async (lineGeojson) => {
  const quartierId =
    form.value?.id ?? form.value?.id_quartier ?? form.value?.properties?.id_quartier ?? null;

  if (!quartierId) return;

  splitError.value = null;
  splitSuccess.value = false;

  try {
    const { data } = await auth.axiosInstance.post(
      `${config.API_BASE_URL}/api/quartierPasto/${quartierId}/split/`,
      { line: lineGeojson }
    );
    splitSuccess.value = true;
    const newQuartierId = data?.quartier2?.id ?? data?.quartier2?.properties?.id_quartier;
    props.onSplitSuccess?.(newQuartierId ?? null);
  } catch (err) {
    splitError.value = err?.response?.data?.detail || "Erreur lors du découpage du quartier.";
  }
};

const submitForm = () => {
  if (props.isEdit) {
    const existingId =
      form.value.id ??
      form.value.id_quartier ??
      form.value.properties?.id_quartier ??
      props.initialForm?.id ??
      props.initialForm?.id_quartier ??
      props.initialForm?.properties?.id_quartier ??
      null;
    form.value.id = existingId;
    form.value.id_quartier = existingId;
    if (!form.value.properties) form.value.properties = {};
    form.value.properties.id_quartier = existingId;
  }

  form.value.situation_exploitation = form.value.properties.situation_exploitation ?? null;

  const geometryFromEditor = geometryEditorRef.value?.getGeometry?.() ?? null;
  if (geometryFromEditor) {
    form.value.geometry = geometryFromEditor;
  }

  if (!form.value.geometry) {
    geometryError.value = true;
    return;
  }

  geometryError.value = false;

  props
    .onSubmit(form.value)
    .then(() => {})
    .catch((error) => {});
};

onMounted(() => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/unitePastorale/`)
    .then((response) => {
      ups.value = response.data;
    })
    .catch((error) => {});

  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/situationExploitation/`)
    .then((response) => {
      situations.value = response.data || [];
      fetchUpGeometry(getUpIdForSituation(form.value?.properties?.situation_exploitation));
    })
    .catch((error) => {});

  fetchContextQuartiersForSituation(form.value?.properties?.situation_exploitation);
});

const getUpIdForSituation = (situationId) => {
  if (!situationId || !situations.value.length) return null;
  const situation = situations.value.find((s) => s.id_situation === situationId);
  return situation?.unite_pastorale ?? null;
};

watch(
  () => form.value?.properties?.situation_exploitation,
  (newSituationId) => {
    fetchContextQuartiersForSituation(newSituationId);
    fetchUpGeometry(getUpIdForSituation(newSituationId));
  }
);

watch(
  () => form.value?.geometry,
  (geometry) => {
    if (geometry) {
      geometryError.value = false;
    }
  }
);

watch(
  () => props.initialForm,
  (newForm) => {
    const normalized = normalizeForm(newForm);

    const incomingId =
      normalized?.id ?? normalized?.id_quartier ?? normalized?.properties?.id_quartier ?? null;
    const currentId =
      form.value?.id ?? form.value?.id_quartier ?? form.value?.properties?.id_quartier ?? null;
    const sameQuartier = normalizeComparableId(incomingId) === normalizeComparableId(currentId);

    // When parent context data refreshes, keep in-progress geometry instead of resetting to null.
    const incomingGeometry = normalized?.geometry;
    const hasIncomingGeometry = !!(
      incomingGeometry &&
      Array.isArray(incomingGeometry.coordinates) &&
      incomingGeometry.coordinates.length
    );
    if (sameQuartier && !hasIncomingGeometry && form.value?.geometry) {
      normalized.geometry = form.value.geometry;
    }

    form.value = normalized;
    fetchContextQuartiersForSituation(normalized?.properties?.situation_exploitation);
  },
  { immediate: true }
);
</script>

<style scoped>
.quartier-layout {
  display: grid;
  grid-template-columns: minmax(280px, 420px) 1fr;
  gap: 20px;
  align-items: start;
}

.fields-card {
  display: flex;
  flex-direction: column;
}

.map-title {
  margin: 0 0 10px;
  font-size: 1rem;
  font-weight: 600;
}

.geometry-alert {
  margin-bottom: 10px;
}

.actions-row {
  margin-top: 14px;
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

@media (max-width: 980px) {
  .quartier-layout {
    grid-template-columns: 1fr;
  }
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
.import-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.import-crs-select {
  max-width: 220px;
}
.import-hint {
  font-size: 0.76rem;
  color: #94a3b8;
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
</style>
