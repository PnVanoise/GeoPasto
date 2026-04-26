<template>
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
          v-model="form.properties.unite_pastorale"
          :items="ups.features || []"
          item-title="properties.nom_up"
          item-value="id"
          label="Unité pastorale"
          variant="underlined"
          density="comfortable"
          clearable
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

        <v-alert
          v-if="!isEdit && nextId"
          type="info"
          variant="tonal"
          density="compact"
        >
          Prochain identifiant: {{ nextId }}
        </v-alert>
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
          Dessinez d'abord la géométrie du quartier (double-clic pour terminer le polygone), puis enregistrez.
        </v-alert>
        <QuartierGeometryEditorOl
          ref="geometryEditorRef"
          v-model="form.geometry"
          :geometryType="'Polygon'"
          :contextLayers="contextLayers"
          :drawOnly="!props.isEdit"
          :editOnly="props.isEdit"
        />
      </section>
    </div>

    <div class="actions-row">
      <v-btn type="submit" color="primary">Enregistrer</v-btn>
    </div>
  </v-form>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";

import auth from "../../auth";
import config from "../../config";
import QuartierGeometryEditorOl from "./QuartierGeometryEditorOl.vue";

const props = defineProps({
  initialForm: Object,
  isEdit: Boolean,
  onSubmit: Function,
});

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
  if (!upId) { upGeoData.value = null; return; }
  try {
    const response = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/unitePastorale/${upId}/`);
    const feature = response.data;
    if (feature?.geometry) {
      upGeoData.value = {
        type: "FeatureCollection",
        features: [{ type: "Feature", geometry: feature.geometry, properties: feature.properties || {} }],
      };
    } else {
      upGeoData.value = null;
    }
  } catch (e) {
    console.error("Erreur lors de la récupération de la géométrie de l'UP", e);
    upGeoData.value = null;
  }
};

const normalizeForm = (src) => {
  const base = src || {};
  const propsData = base.properties || {};
  const quartierId =
    base.id
    ?? base.id_quartier
    ?? propsData.id_quartier
    ?? propsData.id
    ?? null;

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
      situation_exploitation: propsData.situation_exploitation ?? base.situation_exploitation ?? null,
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
const nextId = ref(null);
const geometryEditorRef = ref(null);
const geometryError = ref(false);

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
    form.value?.id
    ?? form.value?.id_quartier
    ?? form.value?.properties?.id_quartier
    ?? props.initialForm?.id
    ?? props.initialForm?.id_quartier
    ?? props.initialForm?.properties?.id_quartier
    ?? null
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
    console.error("Erreur lors de la récupération des quartiers de contexte", error);
    contextQuartiersGeoData.value = null;
  }
};

const submitForm = () => {
  if (!props.isEdit) {
    form.value.id = nextId.value;
    form.value.id_quartier = nextId.value;
    form.value.properties.id_quartier = nextId.value;
  } else {
    const existingId =
      form.value.id
      ?? form.value.id_quartier
      ?? form.value.properties?.id_quartier
      ?? props.initialForm?.id
      ?? props.initialForm?.id_quartier
      ?? props.initialForm?.properties?.id_quartier
      ?? null;
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
    console.warn("QuartierPastoForm submit: geometry is null. Finish drawing (double-click) before saving.");
    return;
  }

  geometryError.value = false;

  props
    .onSubmit(form.value)
    .then(() => {
      console.log("Form submission then block executed");
    })
    .catch((error) => {
      console.error("There was an error in form submission!", error);
    });
};

onMounted(() => {
  if (!props.isEdit) {
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/quartierPasto/getNextId/`)
      .then((response) => {
        nextId.value = response.data.next_id;
        form.value.id = nextId.value;
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération du Next ID", error);
      });
  }

  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/unitePastorale/`)
    .then((response) => {
      ups.value = response.data;
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération de la liste des unites pastorales", error);
    });

  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/situationExploitation/`)
    .then((response) => {
      situations.value = response.data || [];
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération de la liste des situations", error);
    });

  fetchContextQuartiersForSituation(form.value?.properties?.situation_exploitation);
  fetchUpGeometry(form.value?.properties?.unite_pastorale);
});

watch(
  () => form.value?.properties?.situation_exploitation,
  (newSituationId) => {
    fetchContextQuartiersForSituation(newSituationId);
  }
);

watch(
  () => form.value?.properties?.unite_pastorale,
  (newUpId) => {
    fetchUpGeometry(newUpId);
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

    const incomingId = normalized?.id ?? normalized?.id_quartier ?? normalized?.properties?.id_quartier ?? null;
    const currentId = form.value?.id ?? form.value?.id_quartier ?? form.value?.properties?.id_quartier ?? null;
    const sameQuartier = normalizeComparableId(incomingId) === normalizeComparableId(currentId);

    // When parent context data refreshes, keep in-progress geometry instead of resetting to null.
    const incomingGeometry = normalized?.geometry;
    const hasIncomingGeometry = !!(incomingGeometry && Array.isArray(incomingGeometry.coordinates) && incomingGeometry.coordinates.length);
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

.layout-card {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 14px;
  background: #ffffff;
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
  justify-content: flex-end;
}

@media (max-width: 980px) {
  .quartier-layout {
    grid-template-columns: 1fr;
  }
}
</style>
