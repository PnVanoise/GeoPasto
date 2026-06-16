<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <v-form ref="formRef" class="up-form" @submit.prevent="submitForm">
    <div class="up-form-layout">
      <section class="layout-card">
        <v-tabs v-model="activeTab" density="compact" color="primary" class="up-tabs">
          <v-tab value="fiche">Fiche</v-tab>
          <v-tab value="geometries" :disabled="props.mode === 'add'">Géométries</v-tab>
          <v-tab value="conventions" :disabled="props.mode === 'add'">Conventions</v-tab>
          <v-tab value="visites" :disabled="props.mode === 'add'">Visites</v-tab>
          <v-tab value="suivis" :disabled="props.mode === 'add'">Suivis</v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <v-window-item value="fiche">
            <div class="form-cell">
              <v-text-field
                v-model="form.properties.code_up"
                :disabled="props.mode === 'view' || !can('change')"
                class="required"
                label="Code UP"
                density="compact"
                variant="underlined"
                hide-details="auto"
                :rules="[required]"
                clearable
              />
            </div>
            <div class="form-cell">
              <v-text-field
                v-model="form.properties.nom_up"
                :disabled="props.mode === 'view' || !can('change')"
                class="required"
                label="Nom UP"
                density="compact"
                variant="underlined"
                hide-details="auto"
                :rules="[required]"
                clearable
              />
            </div>
            <div class="form-cell">
              <v-select
                v-model="form.properties.secteur"
                :items="secteurOptions"
                :disabled="props.mode === 'view' || !can('change')"
                label="Secteur"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
            </div>
            <div class="form-cell">
              <v-select
                v-model="form.properties.proprios"
                :items="proprietairesOptions"
                item-value="id_proprietaire"
                item-title="full_name"
                multiple
                chips
                :disabled="props.mode === 'view' || !can('change')"
                label="Propriétaires"
                density="compact"
                variant="underlined"
                :menu-props="{ maxHeight: '300px' }"
              />
            </div>

            <div class="up-section-gap">
              <h4 class="section-title">Situations d'exploitation</h4>
              <template v-if="props.mode === 'add'">
                <div class="w3-panel w3-pale-yellow info-panel">
                  Enregistrez l'unité pastorale pour pouvoir ajouter des situations d'exploitation.
                </div>
              </template>
              <template v-else-if="form.id">
                <CrudListPage
                  modelName="situationdexploitation"
                  apiRouteName="situationExploitation"
                  itemLabel="une situation"
                  idField="id_situation"
                  :columns="situGridColumns"
                  :bgColor="'#154889'"
                  :showTitle="false"
                  :showHeader="true"
                  :showSearch="true"
                  :showFilters="false"
                  :filters="[]"
                  :forceAdd="false"
                  :viewOnly="props.mode === 'view'"
                  :requestParams="form.id ? { id_up: form.id } : null"
                  :addQueryParams="form.id ? { unite_pastorale: form.id } : {}"
                />
              </template>
            </div>
          </v-window-item>

          <v-window-item value="geometries">
            <CrudList
              modelName="geometrieunitepastorale"
              apiRouteName="geometrieUP"
              itemLabel="une géométrie"
              idField="id_geometrie_up"
              :geojsonMode="true"
              :formComponent="GeometrieUPForm"
              :columns="geomGridColumns"
              :showTitle="false"
              :showHeader="true"
              :showSearch="false"
              :showFilters="false"
              :filters="[]"
              :viewOnly="props.mode === 'view'"
              :requestParams="form.id ? { unite_pastorale: form.id } : null"
              :initialNewItem="form.id ? { properties: { unite_pastorale: form.id } } : null"
              :defaultSort="{ field: 'date_debut_validite', direction: 'desc' }"
              @row-hover="
                (entry) => {
                  hoveredGeomId = entry ? (entry.id_geometrie_up ?? entry.id) : null;
                }
              "
            />
          </v-window-item>

          <v-window-item value="conventions">
            <template v-if="props.mode === 'add'">
              <div class="w3-panel w3-pale-yellow info-panel">
                Enregistrez l'unité pastorale pour pouvoir voir les conventions.
              </div>
            </template>
            <template v-else-if="form.id">
              <CrudListPage
                modelName="conventiondexploitation"
                apiRouteName="conventionExploitation"
                itemLabel="une convention"
                idField="id_convention"
                :geojsonMode="true"
                :columns="conventionGridColumns"
                :bgColor="'#154889'"
                :showTitle="false"
                :showHeader="true"
                :showSearch="false"
                :showFilters="false"
                :filters="[]"
                :viewOnly="props.mode === 'view'"
                :requestParams="form.id ? { unite_pastorale: form.id } : null"
                :addQueryParams="form.id ? { unite_pastorale: form.id } : {}"
                :selectedId="selectedConventionId"
                @row-click="(row) => (selectedConventionId = row?.id_convention ?? row?.id ?? null)"
              />
            </template>
          </v-window-item>

          <v-window-item value="visites">
            <template v-if="props.mode === 'add'">
              <div class="w3-panel w3-pale-yellow info-panel">
                Enregistrez l'unité pastorale pour pouvoir ajouter des visites.
              </div>
            </template>
            <template v-else-if="form.id">
              <CrudListPage
                modelName="visite"
                apiRouteName="visite"
                itemLabel="une visite"
                idField="id_visite"
                :columns="visiteGridColumns"
                :bgColor="'#0f766e'"
                :showTitle="false"
                :showHeader="true"
                :showSearch="false"
                :showFilters="false"
                :filters="[]"
                :viewOnly="props.mode === 'view'"
                :requestParams="form.id ? { unite_pastorale: form.id } : null"
                :addQueryParams="form.id ? { unite_pastorale: form.id } : {}"
              />
            </template>
          </v-window-item>

          <v-window-item value="suivis">
            <template v-if="props.mode === 'add'">
              <div class="w3-panel w3-pale-yellow info-panel">
                Enregistrez l'unité pastorale pour pouvoir ajouter des suivis.
              </div>
            </template>
            <template v-else-if="form.id">
              <CrudListPage
                modelName="plandesuivi"
                apiRouteName="planSuivi"
                itemLabel="un suivi"
                idField="id_plan_suivi"
                :columns="suiviGridColumns"
                :bgColor="'#64748b'"
                :showTitle="false"
                :showHeader="true"
                :showSearch="false"
                :showFilters="false"
                :filters="[]"
                :viewOnly="props.mode === 'view'"
                :requestParams="form.id ? { unite_pastorale: form.id } : null"
                :addQueryParams="form.id ? { unite_pastorale: form.id } : {}"
              />
            </template>
          </v-window-item>
        </v-window>
      </section>

      <section class="layout-card map-card">
        <OpenLayersGeoJsonMap
          :layers="
            activeTab === 'geometries'
              ? geomTabLayers
              : activeTab === 'conventions'
                ? conventionTabLayers
                : activeMapLayer
          "
          :highlightedId="
            activeTab === 'geometries'
              ? hoveredGeomId
              : activeTab === 'conventions'
                ? selectedConventionId
                : null
          "
          @feature-click="
            (f) => activeTab === 'conventions' && (selectedConventionId = f?.id ?? null)
          "
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
        :disabled="formRef?.isValid === false"
        >{{ btTitle }}</v-btn
      >
    </div>
  </v-form>
</template>

<script setup>
import { reactive, ref, watch, onMounted, onBeforeUnmount, computed } from "vue";
import auth from "@/services/axios";
import { usePermissions } from "@/composables/usePermissions";
import { required } from "@/utils/validators";
import config from "@/../config";
import OpenLayersGeoJsonMap from "@/components/map/OpenLayersGeoJsonMap.vue";
import CrudListPage from "@/components/crud/CrudListPage.vue";
import CrudList from "@/components/crud/CrudList.vue";
import GeometrieUPForm from "./GeometrieUPForm.vue";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" },
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
  initialTab: { type: String, default: "fiche" },
  onTabChange: Function,
});

const { can } = usePermissions("unitepastorale");

const formRef = ref(null);

const formTitle = computed(() => {
  const nom = form.properties?.nom_up;
  if (props.mode === "add") return `Ajouter ${props.itemLabel}`;
  if (props.mode === "change") return `Modifier l'unité pastorale - ${nom ?? ""}`;
  return `Unité pastorale - ${nom ?? ""}`;
});

const btTitle = computed(() => (props.mode === "add" ? "Ajouter" : "Enregistrer"));

const histGeometries = ref([]);
const hoveredGeomId = ref(null);
const proprietaires = ref([]);
const activeTab = ref(props.initialTab || "fiche");
const secteurOptions = ["Haute Tarentaise", "Haute Maurienne", "Pralognan"];

const selectedConventionId = ref(null);
const conventionsGeoData = ref(null);

const situGridColumns = ref([
  { field: "date_debut", label: "Début", sortable: true },
  { field: "date_fin", label: "Fin", sortable: true },
  { field: "exploitant_nom", label: "Alpagiste", sortable: true },
]);

const geomGridColumns = ref([
  { field: "date_debut_validite", label: "Début validité", sortable: true },
  { field: "date_fin_validite", label: "Fin validité", sortable: true },
]);

const visiteGridColumns = ref([
  { field: "date_visite", label: "Date", sortable: true },
  { field: "description", label: "Description", sortable: false },
]);

const conventionGridColumns = ref([
  { field: "exploitant_nom", label: "Alpagiste", sortable: true },
  { field: "date_debut", label: "Début", sortable: true },
  { field: "date_fin", label: "Fin", sortable: true },
]);

const suiviGridColumns = ref([
  { field: "description", label: "Description", sortable: true },
  { field: "date_debut", label: "Début", sortable: true },
  { field: "date_fin", label: "Fin", sortable: true },
  { field: "type_suivi_detail.description", label: "Type de suivi", sortable: true },
]);

const form = reactive({
  ...props.initialForm,
  properties: {
    ...(props.initialForm?.properties || {}),
    code_up: props.initialForm?.properties?.code_up || "",
    nom_up: props.initialForm?.properties?.nom_up || "",
    secteur: props.initialForm?.properties?.secteur || "",
    proprios: Array.isArray(props.initialForm?.properties?.proprios)
      ? [...props.initialForm.properties.proprios]
      : [],
  },
  geometry: props.initialForm?.geometry || null,
});

const proprietairesOptions = computed(() =>
  (proprietaires.value || []).map((p) => ({
    ...p,
    full_name: `${p.nom_propr || ""} ${p.prenom_propr || ""}`.trim(),
  }))
);

const activeMapLayer = computed(() => {
  if (!form.geometry) return [];
  return [
    {
      id: "geom_active",
      title: "Géométrie active",
      data: {
        type: "FeatureCollection",
        features: [{ type: "Feature", geometry: form.geometry, properties: {} }],
      },
      style: { strokeColor: "#16a34a", fillColor: "#16a34a", fillOpacity: 0.2, strokeWidth: 2 },
    },
  ];
});

const geomTabLayers = computed(() => {
  const layers = [];

  if (form.geometry) {
    layers.push({
      id: "geom_active_up",
      title: "Géométrie active (UP)",
      data: {
        type: "FeatureCollection",
        features: [{ type: "Feature", geometry: form.geometry, properties: {} }],
      },
      style: { strokeColor: "#16a34a", fillColor: "#16a34a", fillOpacity: 0.2, strokeWidth: 2 },
    });
  }

  for (const geom of histGeometries.value) {
    const id = geom.id ?? geom.properties?.id_geometrie_up;
    const dateDebut = geom.properties?.date_debut_validite || "?";
    const dateFin = geom.properties?.date_fin_validite;
    const isActive = !dateFin;
    layers.push({
      id: `geom_${id}`,
      title: isActive ? `${dateDebut} → en cours` : `${dateDebut} → ${dateFin}`,
      data: { type: "FeatureCollection", features: [geom] },
      style: isActive
        ? { strokeColor: "#2563eb", fillColor: "#2563eb", fillOpacity: 0.15, strokeWidth: 2 }
        : {
            strokeColor: "#64748b",
            fillColor: "#64748b",
            fillOpacity: 0.08,
            strokeWidth: 1.5,
            lineDash: [6, 4],
          },
    });
  }

  return layers;
});

const fetchHistGeometries = () => {
  if (!form.id) return;
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/geometrieUP/`, { params: { unite_pastorale: form.id } })
    .then((resp) => {
      histGeometries.value = resp.data?.features ?? resp.data ?? [];
    })
    .catch(() => {});
};

const fetchConventions = () => {
  if (!form.id) return;
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/conventionExploitation/`, {
      params: { unite_pastorale: form.id },
    })
    .then((resp) => {
      conventionsGeoData.value = resp.data?.type === "FeatureCollection" ? resp.data : null;
    })
    .catch(() => {});
};

const conventionTabLayers = computed(() => {
  const layers = [];
  if (form.geometry) {
    layers.push({
      id: "up_outline",
      title: "UP",
      data: {
        type: "FeatureCollection",
        features: [{ type: "Feature", geometry: form.geometry, properties: {} }],
      },
      style: { strokeColor: "#b23a2a", strokeWidth: 3, fillOpacity: 0, lineDash: [10, 7] },
    });
  }
  if (selectedConventionId.value && conventionsGeoData.value) {
    const feature = conventionsGeoData.value.features?.find(
      (f) => (f.id ?? f.properties?.id_convention) === selectedConventionId.value
    );
    if (feature) {
      layers.push({
        id: "convention_selected",
        title: "Convention",
        data: { type: "FeatureCollection", features: [feature] },
        style: { strokeColor: "#2563eb", fillColor: "#2563eb", fillOpacity: 0.2, strokeWidth: 2 },
      });
    }
  }
  return layers;
});

onMounted(() => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/proprietaireFoncier/`)
    .then((response) => {
      proprietaires.value = response.data;
      const initIds =
        props.initialForm?.properties?.proprios_ids || props.initialForm?.proprios_ids;
      if (Array.isArray(initIds)) form.properties.proprios = initIds.map((id) => Number(id));
    })
    .catch(() => {});

  fetchHistGeometries();

  window.addEventListener("geo-data-changed", onGeoDataChanged);
});

onBeforeUnmount(() => {
  window.removeEventListener("geo-data-changed", onGeoDataChanged);
});

const onGeoDataChanged = (event) => {
  if (event?.detail?.modelName === "geometrieunitepastorale") {
    fetchHistGeometries();
  }
  if (event?.detail?.modelName === "conventiondexploitation") {
    fetchConventions();
  }
};

watch(activeTab, (tab) => {
  if (tab === "geometries") fetchHistGeometries();
  if (tab === "conventions") fetchConventions();
  props.onTabChange?.(tab);
});

watch(
  () => props.initialForm,
  (newForm) => {
    const isEmptyInitialForm =
      !newForm ||
      (Object.prototype.toString.call(newForm) === "[object Object]" &&
        Object.keys(newForm).length === 0);

    if (props.mode === "add" && isEmptyInitialForm) return;

    try {
      Object.assign(form, JSON.parse(JSON.stringify(newForm || {})));
    } catch (e) {
      Object.assign(form, newForm || {});
    }

    const initIds = newForm?.properties?.proprios_ids || newForm?.proprios_ids;
    if (Array.isArray(initIds)) form.properties.proprios = initIds.map((id) => Number(id));
    if (!form.properties) form.properties = {};
    form.properties.id_unite_pastorale =
      newForm?.properties?.id_unite_pastorale ||
      newForm?.id_unite_pastorale ||
      newForm?.id ||
      form.properties.id_unite_pastorale;
  },
  { deep: true, immediate: true }
);

const buildPayload = () => {
  const payload = JSON.parse(JSON.stringify(form));
  const propsObj = payload.properties || {};
  if (Array.isArray(propsObj.proprios) && propsObj.proprios.length > 0) {
    propsObj.proprios_ids = Array.from(propsObj.proprios);
  }
  payload.properties = propsObj;
  if (props.mode === "add") delete payload.id;
  return payload;
};

const submitForm = async () => {
  if (!props.onSubmit) return;
  const { valid } = await formRef.value.validate();
  if (!valid) return;
  props.onSubmit(buildPayload());
};

const closeModal = () => props.onClose?.();
</script>

<style scoped>
.up-form-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  grid-auto-rows: minmax(480px, auto);
  gap: 1rem;
  align-items: stretch;
  margin-top: 0.5rem;
}
.map-card {
  display: flex;
  flex-direction: column;
}
.up-form :deep(.ol-map-wrapper) {
  flex: 1;
  min-height: 0;
}
.up-form :deep(.ol-map) {
  height: 100%;
}

.up-form :deep(.v-label),
.up-form :deep(.v-chip__content) {
  font-size: 0.82rem;
}
.up-form :deep(.v-field__input),
.up-form :deep(.v-select__selection-text),
.up-form :deep(.v-chip__content) {
  font-size: 0.88rem;
}
.up-form :deep(.v-switch) {
  margin-top: 0;
}

.up-section-gap {
  margin-top: 0.75rem;
}
.section-title {
  margin: 0 0 0.5rem;
  font-size: 0.95rem;
  font-weight: 600;
}
.info-panel {
  padding: 12px;
  border: 1px solid #ddd;
}
.up-tabs {
  margin-bottom: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
}

@media (max-width: 1100px) {
  .up-form-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px) {
  .form-actions :deep(.v-btn) {
    width: 100%;
  }
}
</style>
