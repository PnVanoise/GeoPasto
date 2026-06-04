<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <form class="plan-suivi-form" @submit.prevent="submitForm">
    <div class="plan-suivi-layout">
      <div
        class="plan-suivi-left"
        :class="{ 'full-width': props.mode === 'add' || !form.id_plan_suivi }"
      >
        <section class="layout-card">
          <div class="w3-row form-ligne">
            <div class="form-cell">
              <v-text-field
                v-model="form.description"
                :disabled="props.mode === 'view'"
                label="Description"
                density="compact"
                variant="underlined"
                hide-details="auto"
                :rules="[maxLen(150)]"
                :counter="150"
                clearable
              />
            </div>
          </div>
          <div class="w3-row form-ligne">
            <div class="form-cell">
              <v-textarea
                v-model="form.commentaire"
                :disabled="props.mode === 'view'"
                label="Commentaire"
                density="compact"
                variant="underlined"
                hide-details
                rows="2"
                auto-grow
                clearable
              />
            </div>
          </div>
          <div class="w3-row form-ligne">
            <div class="w3-half form-cell">
              <v-text-field
                type="date"
                label="Date de début"
                v-model="form.date_debut"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
            </div>
            <div class="w3-half form-cell">
              <v-text-field
                type="date"
                label="Date de fin"
                v-model="form.date_fin"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details="auto"
                clearable
                :rules="rulesDateFin"
              />
            </div>
          </div>
          <div class="w3-row form-ligne">
            <div class="w3-half form-cell">
              <v-select
                v-model="form.type_suivi"
                :items="typesuivis"
                item-title="description"
                item-value="id_type_suivi"
                :disabled="props.mode === 'view'"
                label="Type de suivi"
                density="compact"
                variant="underlined"
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
                :disabled="props.mode === 'view' || props.lockUnitePastorale"
                label="Unité pastorale"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
            </div>
          </div>
        </section>

        <template v-if="props.mode !== 'add' && form.id_plan_suivi">
          <section class="layout-card mesures-card">
            <v-tabs v-model="activeTab" density="compact" class="plan-tabs">
              <v-tab value="mesures" prepend-icon="mdi-clipboard-list-outline">Mesures</v-tab>
              <v-tab value="avancement" prepend-icon="mdi-chart-bar">Avancement</v-tab>
            </v-tabs>

            <v-window v-model="activeTab" class="tab-content">
              <v-window-item value="mesures">
                <CrudListPage
                  ref="mesuresListRef"
                  title="Mesures de plan"
                  modelName="mesuredeplan"
                  apiRouteName="mesurePlan"
                  itemLabel="une mesure de plan"
                  idField="id_mesure_plan"
                  :columns="mesureColumns"
                  :bgColor="'#64748b'"
                  :geojsonMode="true"
                  :showTitle="false"
                  :showHeader="true"
                  :showSearch="false"
                  :showExportButtons="false"
                  :showFilters="false"
                  :viewOnly="props.mode === 'view'"
                  :requestParams="{ plan_suivi: form.id_plan_suivi }"
                  :addQueryParams="{ plan_suivi: form.id_plan_suivi }"
                  :selectedId="selectedMesureRawId"
                  @row-click="onMesureRowClick"
                />
              </v-window-item>

              <v-window-item value="avancement">
                <PlanAvancementView
                  :plan-id="form.id_plan_suivi"
                  :unite-pastorale-id="form.unite_pastorale"
                  :view-only="props.mode === 'view'"
                />
              </v-window-item>
            </v-window>
          </section>
        </template>
      </div>

      <section v-if="props.mode !== 'add' && form.id_plan_suivi" class="layout-card map-card">
        <OpenLayersGeoJsonMap
          ref="mapRef"
          :layers="mesuresMapLayers"
          :selectedId="selectedFeature?.id ?? null"
          @feature-click="onMapFeatureClick"
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
        :disabled="!isFormValid"
        >{{ btTitle }}</v-btn
      >
    </div>
  </form>
</template>

<script setup>
import { reactive, watch, ref, computed, onMounted, onUnmounted, nextTick } from "vue";
import config from "../../../config";
import auth from "@/services/axios";
import { usePermissions } from "../../composables/usePermissions";
import CrudListPage from "../../components/crud/CrudListPage.vue";
import PlanAvancementView from "./PlanAvancementView.vue";
import OpenLayersGeoJsonMap from "../../components/map/OpenLayersGeoJsonMap.vue";
import { maxLen } from "@/utils/validators";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" },
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
  lockUnitePastorale: { type: Boolean, default: false },
});

const { can } = usePermissions("plandesuivi");

const formTitle = computed(() => {
  if (props.mode === "add") return `Ajouter ${props.itemLabel}`;
  if (props.mode === "change") return `Modifier ${props.itemLabel}`;
  if (props.mode === "view") return `Voir les détails d'${props.itemLabel}`;
  return "";
});

const btTitle = computed(() => {
  if (props.mode === "add") return "Ajouter";
  if (props.mode === "change") return "Enregistrer";
  return "";
});

const form = reactive({
  id_plan_suivi: null,
  description: "",
  commentaire: "",
  date_debut: "",
  date_fin: "",
  type_suivi: null,
  unite_pastorale: null,
});

const activeTab = ref("mesures");

const typesuivis = ref([]);
const ups = ref([]);
const mesuresGeoData = ref(null);
const upGeoData = ref(null);
const selectedFeature = ref(null);
const mapRef = ref(null);
const mesuresListRef = ref(null);

const selectedMesureRawId = computed(() => {
  const id = selectedFeature.value?.id;
  if (!id) return null;
  return typeof id === "string" && id.includes(":") ? Number(id.split(":")[1]) : Number(id);
});

const mesuresMapLayers = computed(() => {
  const layers = [];
  if (upGeoData.value) {
    layers.push({
      id: "up_outline",
      title: "Unité pastorale",
      data: upGeoData.value,
      style: { strokeColor: "#b23a2a", strokeWidth: 3, fillOpacity: 0, lineDash: [10, 7] },
      visible: true,
    });
  }
  if (mesuresGeoData.value?.features) {
    const obligations = mesuresGeoData.value.features.filter(
      (f) => f.geometry && f.properties?.obligation === true
    );
    const preconisations = mesuresGeoData.value.features.filter(
      (f) => f.geometry && f.properties?.obligation !== true
    );
    if (obligations.length) {
      layers.push({
        id: "mesure_plan_obligation",
        title: "Obligations",
        data: { type: "FeatureCollection", features: obligations },
        style: {
          strokeColor: "#7c3aed",
          strokeWidth: 2,
          fillOpacity: 0.18,
          pointRadius: 5.5,
          pointStrokeColor: "#ffffff",
          pointStrokeWidth: 1,
          zIndex: 13,
        },
        popup: {
          typeLabel: "Obligation",
          attribute: "popup_label",
          idAttribute: "id_mesure_plan",
          route: "",
        },
        visible: true,
      });
    }
    if (preconisations.length) {
      layers.push({
        id: "mesure_plan_preconisation",
        title: "Préconisations",
        data: { type: "FeatureCollection", features: preconisations },
        style: {
          strokeColor: "#c4b5fd",
          strokeWidth: 2,
          fillOpacity: 0.1,
          pointRadius: 5.5,
          pointStrokeColor: "#ffffff",
          pointStrokeWidth: 1,
          zIndex: 12,
        },
        popup: {
          typeLabel: "Préconisation",
          attribute: "popup_label",
          idAttribute: "id_mesure_plan",
          route: "",
        },
        visible: true,
      });
    }
  }
  return layers;
});

const mesureColumns = [
  { field: "type_mesure_detail.description", label: "Type", sortable: true },
  { field: "obligation", label: "Oblig.", sortable: true },
  { field: "date_debut_validite", label: "Début validité", sortable: true, format: "date" },
  { field: "date_fin_validite", label: "Fin validité", sortable: true, format: "date" },
];

const fetchMesuresForPlan = async (planId) => {
  if (!planId) {
    mesuresGeoData.value = null;
    return;
  }
  try {
    const { data } = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/mesurePlan/`, {
      params: { plan_suivi: planId },
    });
    const raw = data?.type === "FeatureCollection" ? data : null;
    if (!raw) {
      mesuresGeoData.value = null;
      return;
    }
    const features = raw.features
      .filter((f) => f?.geometry)
      .map((f) => {
        const rawId = f?.id ?? f?.properties?.id_mesure_plan;
        const typeMesure = f?.properties?.type_mesure_detail?.description;
        const desc = f?.properties?.description;
        const popupLabel = [typeMesure, desc].filter(Boolean).join(" – ") || `Mesure ${rawId}`;
        return {
          ...f,
          id: rawId != null ? `mesure_plan:${rawId}` : undefined,
          properties: {
            ...(f?.properties || {}),
            id_mesure_plan: rawId,
            popup_label: popupLabel,
          },
        };
      });
    mesuresGeoData.value = { type: "FeatureCollection", features };
  } catch {
    mesuresGeoData.value = null;
  }
};

const fetchUpGeoData = async (upId) => {
  if (!upId) {
    upGeoData.value = null;
    return;
  }
  try {
    const { data } = await auth.axiosInstance.get(
      `${config.API_BASE_URL}/api/unitePastorale/${upId}/`
    );
    upGeoData.value =
      data?.type === "Feature"
        ? { type: "FeatureCollection", features: [data] }
        : data?.type === "FeatureCollection"
          ? data
          : null;
  } catch {
    upGeoData.value = null;
  }
};

watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) {
      Object.assign(form, newVal);
    }
  },
  { immediate: true }
);

watch(() => form.id_plan_suivi, fetchMesuresForPlan, { immediate: true });
watch(() => form.unite_pastorale, fetchUpGeoData, { immediate: true });

onMounted(() => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/typeSuivi/`)
    .then(({ data }) => {
      typesuivis.value = data;
    })
    .catch(() => {});

  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/unitePastorale/light/`)
    .then(({ data }) => {
      ups.value = data;
    })
    .catch(() => {});

  const onGeoDataChanged = ({ detail }) => {
    if (detail?.modelName === "mesuredeplan") fetchMesuresForPlan(form.id_plan_suivi);
  };
  window.addEventListener("geo-data-changed", onGeoDataChanged);
  onUnmounted(() => window.removeEventListener("geo-data-changed", onGeoDataChanged));
});

const rulesDateFin = computed(() => [
  (v) =>
    !v ||
    !form.date_debut ||
    v >= form.date_debut ||
    "La date de fin doit être postérieure à la date de début.",
]);

const isFormValid = computed(() => {
  const debut = form.date_debut;
  const fin = form.date_fin;
  return !fin || !debut || fin >= debut;
});

const onMapFeatureClick = async ({ id, layer }) => {
  if (!id) {
    selectedFeature.value = null;
    return;
  }
  const isSame = selectedFeature.value?.id === id;
  selectedFeature.value = isSame ? null : { id, layer };
  if (!selectedFeature.value) return;
  activeTab.value = "mesures";
  await nextTick();
  const rawId = typeof id === "string" && id.includes(":") ? Number(id.split(":")[1]) : Number(id);
  await new Promise((r) => setTimeout(r, 320));
  mesuresListRef.value?.scrollToId(rawId);
};

const onMesureRowClick = (entry) => {
  const rawId = entry.id_mesure_plan;
  if (!rawId) return;
  const prefixedId = `mesure_plan:${rawId}`;
  const isSame = selectedFeature.value?.id === prefixedId;
  selectedFeature.value = isSame
    ? null
    : {
        id: prefixedId,
        layer: entry.obligation ? "mesure_plan_obligation" : "mesure_plan_preconisation",
      };
  if (selectedFeature.value) mapRef.value?.zoomToId(prefixedId);
};

const submitForm = () => {
  if (props.onSubmit) {
    props.onSubmit(form);
  }
};

const closeModal = () => {
  props.onClose?.();
};
</script>

<style scoped>
.plan-suivi-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 1rem;
  align-items: stretch;
  margin-top: 0.5rem;
}
.plan-suivi-left {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.plan-suivi-left.full-width {
  grid-column: 1 / -1;
}
.map-card {
  position: sticky;
  top: 1rem;
  min-height: 400px;
  display: flex;
  flex-direction: column;
}
.plan-suivi-form :deep(.ol-map-wrapper) {
  flex: 1;
  min-height: 0;
}
.plan-suivi-form :deep(.ol-map) {
  height: 100%;
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
.mesures-card {
  min-height: 200px;
}
.plan-tabs {
  margin-bottom: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
}
.tab-content {
  min-height: 180px;
}
.plan-suivi-form :deep(.v-input--density-compact .v-field__input) {
  min-height: 38px;
  padding-top: 6px;
  padding-bottom: 6px;
}
.plan-suivi-form :deep(.v-label.v-field-label) {
  font-size: 0.82rem;
}
.plan-suivi-form :deep(.v-input) {
  font-size: 0.88rem;
}
.plan-suivi-form :deep(.v-field__input),
.plan-suivi-form :deep(.v-select__selection-text) {
  font-size: 0.88rem;
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
  margin-top: 1.5rem;
}
@media (max-width: 1100px) {
  .plan-suivi-layout {
    grid-template-columns: 1fr;
  }
  .plan-suivi-left.full-width {
    grid-column: 1;
  }
  .map-card {
    position: static;
  }
}
</style>
