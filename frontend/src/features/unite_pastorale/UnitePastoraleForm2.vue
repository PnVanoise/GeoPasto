<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <form class="up-form" @submit.prevent="submitForm">
    <div class="up-form-layout">
      <section class="layout-card">
        <div class="form-cell">
          <v-text-field
            v-model="form.properties.code_up"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
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
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
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
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Secteur"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
        <div class="w3-row form-ligne inline-two-fields">
          <div class="w3-half form-cell">
            <v-text-field
              v-model="form.properties.annee_version"
              :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
              label="Année version"
              density="compact"
              variant="underlined"
              hide-details
              clearable
            />
          </div>
          <div class="w3-half form-cell inline-switch-cell">
            <v-switch
              v-model="form.properties.version_active"
              :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
              label="Version active ?"
              color="primary"
              density="compact"
              hide-details
            />
          </div>
        </div>
        <div class="form-cell">
          <v-select
            v-model="form.properties.proprios"
            :items="proprietairesOptions"
            item-value="id_proprietaire"
            item-title="full_name"
            multiple
            chips
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
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
      </section>

      <section class="layout-card map-card">
        <QuartierGeometryEditorOl
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
</template>

<script setup>
import { reactive, ref, watch, onMounted, computed } from "vue";
import auth from "@/services/axios";
import { usePermissions } from "@/composables/usePermissions";
import config from "@/../config";
import QuartierGeometryEditorOl from "@/components/map/QuartierGeometryEditorOl.vue";
import CrudListPage from "@/components/crud/CrudListPage.vue";

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
const showMissingGeometry = ref(false);
const proprietaires = ref([]);
const secteurOptions = ["Haute Tarentaise", "Haute Maurienne", "Pralognan"];

const situGridColumns = ref([
  { field: "annee", label: "Année", sortable: true },
  { field: "exploitant_nom", label: "Exploitant", sortable: true },
  { field: "situation_active", label: "Active ?", sortable: true },
]);

const form = reactive({
  ...props.initialForm,
  properties: {
    ...(props.initialForm?.properties || {}),
    code_up: props.initialForm?.properties?.code_up || "",
    nom_up: props.initialForm?.properties?.nom_up || "",
    secteur: props.initialForm?.properties?.secteur || "",
    annee_version:
      props.initialForm?.properties?.annee_version || new Date().getFullYear().toString(),
    proprios: Array.isArray(props.initialForm?.properties?.proprios)
      ? [...props.initialForm.properties.proprios]
      : [],
    version_active: props.initialForm?.properties?.version_active ?? false,
  },
  geometry: props.initialForm?.geometry || null,
});

const proprietairesOptions = computed(() =>
  (proprietaires.value || []).map((p) => ({
    ...p,
    full_name: `${p.nom_propr || ""} ${p.prenom_propr || ""}`.trim(),
  }))
);

onMounted(() => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/unitePastorale/`)
    .then((response) => {
      refUPs.value = response.data;
    })
    .catch((error) => {
      console.error("Erreur chargement UPs de référence", error);
    });

  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/proprietaireFoncier/`)
    .then((response) => {
      proprietaires.value = response.data;
      const initIds =
        props.initialForm?.properties?.proprios_ids || props.initialForm?.proprios_ids;
      if (Array.isArray(initIds)) form.properties.proprios = initIds.map((id) => Number(id));
    })
    .catch((error) => {
      console.error("Erreur chargement propriétaires", error);
    });
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

const submitForm = () => {
  if (!props.onSubmit) return;
  const payload = JSON.parse(JSON.stringify(form));
  if (!payload.geometry) {
    showMissingGeometry.value = true;
    return;
  }
  const propsObj = payload.properties || {};
  if (Array.isArray(propsObj.proprios) && propsObj.proprios.length > 0) {
    propsObj.proprios_ids = Array.from(propsObj.proprios);
  }
  payload.properties = propsObj;
  if (props.mode === "add") delete payload.id;
  props.onSubmit(payload).catch((err) => console.error(err));
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
.disable-events {
  pointer-events: none;
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
