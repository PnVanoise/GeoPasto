<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <form class="up-form" @submit.prevent="submitForm">
    <div class="up-form-layout">
      <section class="layout-card">
        <v-tabs v-model="activeTab" density="compact" color="primary" class="up-tabs">
          <v-tab value="fiche">Fiche</v-tab>
          <v-tab value="geometries" :disabled="props.mode === 'add'">Géométries</v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <v-window-item value="fiche">
            <div class="form-cell">
              <v-text-field
                v-model="form.properties.code_up"
                :disabled="props.mode === 'view' || !can('change')"
                label="Code UP"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
            </div>
            <div class="form-cell">
              <v-text-field
                v-model="form.properties.nom_up"
                :disabled="props.mode === 'view' || !can('change')"
                label="Nom UP"
                density="compact"
                variant="underlined"
                hide-details
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
            <CrudList2
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
            />
          </v-window-item>
        </v-window>
      </section>

      <section class="layout-card map-card">
        <OpenLayersGeoJsonMap
          v-if="props.mode === 'view' && mapLayers.length"
          :layers="mapLayers"
        />
        <QuartierGeometryEditorOl
          v-else
          :key="`up-geom-${form.id ?? 'new'}`"
          v-model="form.geometry"
          geometryType="MultiPolygon"
          :contextGeoData="refUPs"
          :disabled="props.mode === 'view'"
          :drawOnly="props.mode === 'add'"
          :editOnly="props.mode === 'change'"
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

  <v-dialog v-model="showMissingGeometry" max-width="480">
    <v-card>
      <v-card-title class="text-h6">Géométrie manquante</v-card-title>
      <v-card-text
        >Veuillez dessiner la géométrie de l'unité pastorale avant d'enregistrer.</v-card-text
      >
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" text @click="showMissingGeometry = false">OK</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="showGeomChangeDialog" max-width="480" persistent>
    <v-card>
      <v-card-title class="text-h6">Changement de géométrie</v-card-title>
      <v-card-text>
        <p class="mb-3">
          La géométrie a été modifiée. Indiquez la date à partir de laquelle la nouvelle géométrie
          est valide. L'ancienne sera clôturée la veille.
        </p>
        <v-text-field
          v-model="nouvelleGeomDebut"
          label="Date de début de la nouvelle géométrie"
          type="date"
          density="compact"
          variant="underlined"
          hide-details="auto"
          :error-messages="geomChangeError"
        />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="showGeomChangeDialog = false">Annuler</v-btn>
        <v-btn color="success" @click="confirmerChangementGeom">Confirmer</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { reactive, ref, watch, onMounted, computed } from "vue";
import auth from "@/services/axios";
import { usePermissions } from "@/composables/usePermissions";
import config from "@/../config";
import QuartierGeometryEditorOl from "@/components/map/QuartierGeometryEditorOl.vue";
import OpenLayersGeoJsonMap from "@/components/map/OpenLayersGeoJsonMap.vue";
import CrudListPage from "@/components/crud/CrudListPage.vue";
import CrudList2 from "@/components/crud/CrudList2.vue";
import GeometrieUPForm from "./GeometrieUPForm.vue";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" },
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("unitepastorale");

const formTitle = computed(() => {
  if (props.mode === "add") return `Ajouter ${props.itemLabel}`;
  if (props.mode === "change") return `Modifier ${props.itemLabel}`;
  return `Voir les détails d'${props.itemLabel}`;
});

const btTitle = computed(() => (props.mode === "add" ? "Ajouter" : "Enregistrer"));

const refUPs = ref([]);
const histGeometries = ref([]);
const showMissingGeometry = ref(false);
const proprietaires = ref([]);
const activeTab = ref("fiche");
const secteurOptions = ["Haute Tarentaise", "Haute Maurienne", "Pralognan"];

const originalGeometry = ref(null);
const showGeomChangeDialog = ref(false);
const nouvelleGeomDebut = ref("");
const geomChangeError = ref("");
let pendingPayload = null;

const situGridColumns = ref([
  { field: "date_debut", label: "Début", sortable: true },
  { field: "date_fin", label: "Fin", sortable: true },
  { field: "exploitant_nom", label: "Exploitant", sortable: true },
]);

const geomGridColumns = ref([
  { field: "date_debut_validite", label: "Début validité", sortable: true },
  { field: "date_fin_validite", label: "Fin validité", sortable: true },
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

originalGeometry.value = props.initialForm?.geometry
  ? JSON.stringify(props.initialForm.geometry)
  : null;

const proprietairesOptions = computed(() =>
  (proprietaires.value || []).map((p) => ({
    ...p,
    full_name: `${p.nom_propr || ""} ${p.prenom_propr || ""}`.trim(),
  }))
);

const mapLayers = computed(() => {
  if (!histGeometries.value.length) return [];
  return histGeometries.value.map((geom) => {
    const isActive = !geom.properties?.date_fin_validite;
    const dateDebut = geom.properties?.date_debut_validite || "?";
    const dateFin = geom.properties?.date_fin_validite || "en cours";
    return {
      id: `geom_${geom.id ?? geom.properties?.id_geometrie_up}`,
      title: isActive ? `Active (depuis ${dateDebut})` : `${dateDebut} → ${dateFin}`,
      data: { type: "FeatureCollection", features: [geom] },
      style: isActive
        ? { strokeColor: "#16a34a", fillColor: "#16a34a", fillOpacity: 0.2, strokeWidth: 2 }
        : {
            strokeColor: "#64748b",
            fillColor: "#64748b",
            fillOpacity: 0.08,
            strokeWidth: 1.5,
            lineDash: [6, 4],
          },
    };
  });
});

onMounted(() => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/unitePastorale/`)
    .then((response) => {
      refUPs.value = response.data;
    })
    .catch((error) => {});

  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/proprietaireFoncier/`)
    .then((response) => {
      proprietaires.value = response.data;
      const initIds =
        props.initialForm?.properties?.proprios_ids || props.initialForm?.proprios_ids;
      if (Array.isArray(initIds)) form.properties.proprios = initIds.map((id) => Number(id));
    })
    .catch((error) => {});

  if (form.id) {
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/geometrieUP/`, { params: { unite_pastorale: form.id } })
      .then((resp) => {
        histGeometries.value = resp.data?.features ?? resp.data ?? [];
      })
      .catch(() => {});
  }
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

const geometryChanged = () => {
  if (!form.geometry) return false;
  return JSON.stringify(form.geometry) !== originalGeometry.value;
};

const submitForm = () => {
  if (!props.onSubmit) return;
  const payload = buildPayload();
  if (!payload.geometry) {
    showMissingGeometry.value = true;
    return;
  }
  if (props.mode === "change" && geometryChanged()) {
    pendingPayload = payload;
    nouvelleGeomDebut.value = new Date().toISOString().slice(0, 10);
    geomChangeError.value = "";
    showGeomChangeDialog.value = true;
    return;
  }
  props.onSubmit(payload);
};

const confirmerChangementGeom = async () => {
  if (!nouvelleGeomDebut.value) {
    geomChangeError.value = "La date de début est obligatoire.";
    return;
  }
  geomChangeError.value = "";

  const upId = form.id;
  const dateDebut = nouvelleGeomDebut.value;
  const dateFin = new Date(new Date(dateDebut) - 86400000).toISOString().slice(0, 10);

  try {
    // Clôturer la géométrie active courante (date_fin_validite = dateDebut - 1 jour)
    const geomResp = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/geometrieUP/`, {
      params: { unite_pastorale: upId },
    });
    const features = geomResp.data?.features ?? geomResp.data ?? [];
    const active = features.find((f) => !f.properties?.date_fin_validite);
    if (active) {
      const activeId = active.id ?? active.properties?.id_geometrie_up;
      await auth.axiosInstance.patch(`${config.API_BASE_URL}/api/geometrieUP/${activeId}/`, {
        type: "Feature",
        id: activeId,
        geometry: active.geometry,
        properties: { ...active.properties, date_fin_validite: dateFin },
      });
    }

    // Créer la nouvelle géométrie
    await auth.axiosInstance.post(`${config.API_BASE_URL}/api/geometrieUP/`, {
      type: "Feature",
      geometry: pendingPayload.geometry,
      properties: {
        unite_pastorale: upId,
        date_debut_validite: dateDebut,
        date_fin_validite: null,
      },
    });

    showGeomChangeDialog.value = false;
    props.onSubmit(pendingPayload);
  } catch (e) {
    geomChangeError.value = "Erreur lors de la mise à jour des géométries.";
  }
};

const closeModal = () => props.onClose?.();
</script>

<style scoped>
.up-form-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 1rem;
  align-items: start;
  margin-top: 0.5rem;
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

.up-form :deep(.v-input--density-compact .v-field__input) {
  min-height: 38px;
  padding-top: 6px;
  padding-bottom: 6px;
}
.up-form :deep(.v-label.v-field-label) {
  font-size: 0.82rem;
}
.up-form :deep(.v-label),
.up-form :deep(.v-chip__content) {
  font-size: 0.82rem;
}
.up-form :deep(.v-input) {
  font-size: 0.88rem;
}
.up-form :deep(.v-field__input),
.up-form :deep(.v-select__selection-text),
.up-form :deep(.v-chip__content) {
  font-size: 0.88rem;
}
.up-form :deep(.v-switch) {
  margin-top: 0;
}

.form-ligne {
  padding: 4px;
}
.form-cell {
  padding: 4px;
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
.inline-two-fields {
  margin: 0;
}
.inline-switch-cell {
  display: flex;
  align-items: center;
}
.form-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
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
  .form-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 0.4rem;
  }
  .form-actions :deep(.v-btn) {
    width: 100%;
  }
}
</style>
