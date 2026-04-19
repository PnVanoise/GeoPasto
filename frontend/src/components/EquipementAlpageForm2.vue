<template>
  <h3 class="w3-center w3-margin">{{ formTitle }}</h3>

  <form class="eqpt-form" @submit.prevent="submitForm">
    <div class="eqpt-layout">
      <section class="layout-card">
        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-text-field
              v-model.number="form.id_equipement_alpage"
              type="number"
              label="ID"
              :disabled="props.mode === 'view' || autoId"
              :readonly="autoId"
              density="compact"
              variant="outlined"
              hide-details
            />
          </div>
          <div class="w3-half form-cell">
            <v-switch
              v-model="autoId"
              label="ID auto"
              color="primary"
              :disabled="props.mode === 'view'"
              density="compact"
              hide-details
            />
          </div>
        </div>

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
        <div class="geometry-status" :class="hasGeometry ? 'is-set' : 'is-missing'">
          {{ hasGeometry ? "Position définie" : "Position non définie" }}
        </div>
        <QuartierGeometryEditorOl
          v-model="form.geometry"
          geometryType="Point"
          :contextGeoData="upContextGeoData"
          :disabled="props.mode === 'view'"
        />
      </section>
    </div>

    <div class="form-actions">
      <v-btn color="info" @click="closeModal" prepend-icon="mdi-arrow-left-circle">Retour</v-btn>
      <v-btn v-if="props.mode !== 'view'" color="success" type="submit" prepend-icon="mdi-content-save">{{ btTitle }}</v-btn>
    </div>
  </form>
</template>

<script setup>
import { computed, reactive, ref, watch, onMounted } from "vue";
import config from "../../config";
import auth from "../../auth";
import QuartierGeometryEditorOl from "./QuartierGeometryEditorOl.vue";
import { selectMenuProps } from "../composables/useSelectMenuProps";

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
  if (geom.type !== "Point") return false;
  return Array.isArray(geom.coordinates) && geom.coordinates.length >= 2;
});

const autoId = ref(true);
const typesEquipement = ref([]);
const ups = ref([]);
const upContextGeoData = ref(null);

const form = reactive({
  id_equipement_alpage: null,
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
      features: [{ type: "Feature", geometry: payload.geometry, properties: payload.properties || {} }],
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
    console.error("Erreur chargement géométrie UP", err);
    upContextGeoData.value = null;
  }
};

const fetchNextId = async () => {
  if (props.mode !== "add" || !autoId.value) return;
  try {
    const res = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/equipementAlpage/getNextId/`);
    form.id_equipement_alpage = res.data?.next_id ?? form.id_equipement_alpage;
  } catch (err) {
    console.error("Erreur next id equipement alpage", err);
  }
};

watch(autoId, (enabled) => {
  if (enabled) fetchNextId();
});

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
    const src = base?.properties
      ? { ...base.properties, id_equipement_alpage: base.id ?? base.properties.id_equipement_alpage }
      : base;

    form.id_equipement_alpage = src.id_equipement_alpage ?? src.id ?? null;
    form.description = src.description ?? "";
    form.etat = src.etat ?? "";
    form.type_equipement = normalizeFkId(
      src.type_equipement ?? src.type_equipement_detail,
      ["id_type_equipement", "id"]
    );
    form.unite_pastorale = normalizeFkId(
      src.unite_pastorale ?? src.unite_pastorale_detail,
      ["id_unite_pastorale", "id"]
    );
    form.geometry = base.geometry ?? src.geometry ?? null;
    if (props.mode !== "add") autoId.value = false;
  },
  { deep: true, immediate: true }
);

const submitForm = async () => {
  const payload = {
    id_equipement_alpage: form.id_equipement_alpage,
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
  } catch (err) {
    console.error("Erreur chargement refs equipement alpage", err);
  }

  if (form.unite_pastorale) {
    await fetchUnitePastoraleContext(form.unite_pastorale);
  }
  await fetchNextId();
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
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px;
  background: #ffffff;
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

.form-ligne { padding: 4px; }
.form-cell { padding: 4px; }
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
