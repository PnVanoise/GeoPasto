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
            hide-details="auto"
            :rules="rulesDateDebut"
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
            hide-details="auto"
            clearable
            :rules="rulesDateFin"
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

      <div v-if="props.mode !== 'view'" class="import-section">
        <button type="button" class="import-toggle" @click="showImport = !showImport">
          <v-icon size="16">{{ showImport ? "mdi-chevron-up" : "mdi-chevron-down" }}</v-icon>
          Importer depuis QGIS
        </button>

        <div v-if="showImport" class="import-panel">
          <div class="import-row">
            <v-select
              v-model="importCrs"
              :items="crsOptions"
              item-value="value"
              item-title="label"
              label="Projection source"
              density="compact"
              variant="underlined"
              hide-details
              class="import-crs-select"
            />
            <span class="import-hint">WKT ou GeoJSON</span>
          </div>
          <v-textarea
            v-model="importText"
            label="Coller la géométrie copiée depuis QGIS"
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
            <v-btn color="primary" size="small" prepend-icon="mdi-import" @click="importerGeometrie"
              >Importer</v-btn
            >
          </div>
        </div>
      </div>
    </section>

    <div class="form-actions">
      <v-btn color="info" @click="emit('close')" prepend-icon="mdi-arrow-left-circle">Retour</v-btn>
      <v-btn
        v-if="props.mode !== 'view'"
        color="success"
        type="submit"
        prepend-icon="mdi-content-save"
        :disabled="!isFormValid"
        >{{ props.mode === "add" ? "Ajouter" : "Enregistrer" }}</v-btn
      >
    </div>
  </form>
</template>

<script setup>
import { reactive, ref, computed, watch } from "vue";
import proj4 from "proj4";
import { register } from "ol/proj/proj4";
import WKT from "ol/format/WKT";
import GeoJSON from "ol/format/GeoJSON";
import QuartierGeometryEditorOl from "@/components/map/QuartierGeometryEditorOl.vue";

proj4.defs(
  "EPSG:2154",
  "+proj=lcc +lat_0=46.5 +lon_0=3 +lat_1=49 +lat_2=44 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
);
register(proj4);

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

const rulesDateDebut = [(v) => !!v || "La date de début est obligatoire."];

const rulesDateFin = computed(() => [
  (v) =>
    !v ||
    !form.properties.date_debut_validite ||
    v >= form.properties.date_debut_validite ||
    "La date de fin doit être postérieure à la date de début.",
]);

const isFormValid = computed(() => {
  const debut = form.properties.date_debut_validite;
  const fin = form.properties.date_fin_validite;
  return !!debut && (!fin || fin >= debut);
});

const showImport = ref(false);
const importText = ref("");
const importCrs = ref("EPSG:2154");
const importError = ref("");
const importInfo = ref("");

const detectImportCrs = (text) => {
  const trimmed = text?.trim();
  if (!trimmed || trimmed.startsWith("{")) return "";
  const coordMatch = trimmed.match(/\(\s*([-\d.]+)\s+([-\d.]+)/);
  const firstX = coordMatch ? parseFloat(coordMatch[1]) : null;
  return firstX !== null && Math.abs(firstX) < 360 && importCrs.value !== "EPSG:4326"
    ? "Coordonnées WGS84 détectées — projection source ignorée."
    : "";
};

watch(importText, (text) => {
  importInfo.value = detectImportCrs(text);
});

const crsOptions = [
  { value: "EPSG:2154", label: "Lambert 93 (EPSG:2154)" },
  { value: "EPSG:4326", label: "WGS84 (EPSG:4326)" },
];

const importerGeometrie = () => {
  importError.value = "";
  importInfo.value = "";
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
      const coordMatch = text.match(/\(\s*([-\d.]+)\s+([-\d.]+)/);
      const firstX = coordMatch ? parseFloat(coordMatch[1]) : null;
      const effectiveCrs =
        firstX !== null && Math.abs(firstX) < 360 ? "EPSG:4326" : importCrs.value;
      const olFeature = new WKT().readFeature(text, {
        dataProjection: effectiveCrs,
        featureProjection: "EPSG:4326",
      });
      if (!olFeature) throw new Error("WKT invalide.");
      geometry = new GeoJSON().writeGeometryObject(olFeature.getGeometry());
    }

    form.geometry = geometry;
    if (!importInfo.value) showImport.value = false;
    importText.value = "";
  } catch (e) {
    importError.value = e.message || "Format non reconnu (WKT ou GeoJSON attendu).";
  }
};

const submitForm = () => {
  const payload = JSON.parse(JSON.stringify(form));
  if (props.mode === "add") delete payload.id;
  if (payload.properties.date_fin_validite === "") payload.properties.date_fin_validite = null;
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
