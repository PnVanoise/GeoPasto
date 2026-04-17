<template>
  <h3 class="w3-center w3-margin">{{ formTitle }}</h3>
  
  <form class="up-form" @submit.prevent="submitForm">
    <div class="up-form-layout">
      <div class="up-form-col">
        <div class="form-cell">
          <v-text-field
            id="code_up"
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
            id="nom_up"
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
          <v-text-field
            id="secteur"
            v-model="form.properties.secteur"
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
              id="annee_version"
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
              id="version_active"
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
          id="proprietaires"
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
        <div class="grid-container up-section-gap">
          <h3>Situations d'exploitation</h3>
          <template v-if="props.mode === 'add'">
            <div class="w3-panel w3-pale-yellow" style="padding:12px; border:1px solid #ddd;">
              Enregistrez l'unité pastorale pour pouvoir ajouter des situations d'exploitation.
            </div>
          </template>
          <template v-else>
            <CrudList2
              title="Situations d'exploitation"
              modelName="situationdexploitation"
              apiRouteName="situationExploitation"
              itemLabel="une situation"
              idField="id"
              :columns="situGridColumns"
              :formComponent="SituationExploitationForm2"
              :bgColor="'#154889'"
              :showTitle="false"
              :showHeader="true"
              :showSearch="true"
              :showFilters="false"
              :filters="situFilters"
              :forceAdd="false"
              :viewOnly="props.mode === 'view'"
              :initialNewItem="{ unite_pastorale: form.id, exploitant: null }"
            />
          </template>
        </div>

        
      </div>
      <div class="up-form-col">
        <div class="form-cell">
              <!-- <h4>Géométrie</h4> -->
              <QuartierGeometryEditorOl
                :key="`up-geom-${form.id ?? 'new'}`"
                v-model="form.geometry"
                geometryType="MultiPolygon"
                :contextGeoData="refUPs"
              />
        </div>
      </div>
      <!-- Membres -->
      
    </div>

    <div class="form-actions">
      <v-btn density="comfortable" color="info" @click="closeModal" prepend-icon="mdi-arrow-left-circle">Retour</v-btn>
      <v-btn density="comfortable" v-if="props.mode !== 'view'" color="success" type="submit" prepend-icon="mdi-content-save">{{ btTitle }}</v-btn>
      
    </div>
  </form>
  <!-- Modal for missing geometry -->
  <v-dialog v-model="showMissingGeometry" max-width="480">
    <v-card>
      <v-card-title class="text-h6">Géométrie manquante</v-card-title>
      <v-card-text>Veuillez dessiner la géométrie de l'unité pastorale avant d'enregistrer.</v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" text @click="showMissingGeometry = false">OK</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { reactive, ref, watch, onMounted, computed } from "vue";
import { useRouter } from "vue-router";

import auth from "../../auth";
import { usePermissions } from "../composables/usePermissions";

import config from "../../config";
import QuartierGeometryEditorOl from "./QuartierGeometryEditorOl.vue";
import CrudList2 from "./CrudList2.vue";
import SituationExploitationForm2 from "./SituationExploitationForm2.vue";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" }, // add | change | view
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("unitepastorale");

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

const refUPs = ref([]);

const showMissingGeometry = ref(false);

const proprietaires = ref([]);
const situationExploitations = ref([]);
const evenementsGeoJSON = ref(null);
const evenements = ref([]);

const situGridColumns = ref([
  { field: "annee", label: "Année", sortable: true },
  { field: "exploitant_nom", label: "Exploitant", sortable: true },
  { field: "situation_active", label: "Active ?", sortable: true },
]);

const situFilters = ref([
  {
    key: "upFilter",
    type: "hidden",
    default: "",
    apply: (items, _value) => {
      if (!form.id) return [];
      return (items || []).filter((i) => {
        const upId = i.unite_pastorale ?? i.unite_pastorale_id ?? i.properties?.unite_pastorale;
        return String(upId) === String(form.id);
      });
    },
  },
]);

const fetchSituations = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/situationExploitation/?id_up=${form.id}`)
    .then((response) => {
      situationExploitations.value = response.data;
      console.log("list response data:", response.data);
      console.log("situationExploitation.value:", situationExploitations.value);
    })
    .catch((error) => {
      console.error("There was an error!", error);
    })
    .finally(() => {
      //isLoading.value = false;
      console.log("fetchSituations done");
    });
};

const fetchRefUPs = () => {
  console.log(`${config.API_BASE_URL}/api/unitePastorale/`);
  // transformer en features
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/unitePastorale/`)
    .then((response) => {
      const data = response.data;
      console.log("list response data:", response.data);
      refUPs.value = data;
      console.log("fetchRefUPs.value:", refUPs.value);

    })
    .catch((error) => {
      console.error("There was an error!", error);
    })
    .finally(() => {
      //isLoading.value = false;
      console.log("fetchRefUPs done");
    });
};

const fetchEvenements = () => {
  if (!form.id) return;
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/evenement/?up_id=${form.id}`)
    .then((response) => {
      const data = response.data;
      // If API returns FeatureCollection, use it directly
      if (data && data.type === "FeatureCollection") {
        evenementsGeoJSON.value = data;
        // build list for grid
        evenements.value = data.features.map(f => ({ id: f.id ?? f.properties?.id, properties: f.properties || {}, geometry: f.geometry }));
      } else if (Array.isArray(data)) {
        // Try to convert array of features to FeatureCollection
        const features = data
          .map((item) => {
            if (item.geometry) return item;
            // try to construct from lat/lng fields if present
            if (item.longitude != null && item.latitude != null) {
              return {
                type: "Feature",
                geometry: { type: "Point", coordinates: [item.longitude, item.latitude] },
                properties: item,
              };
            }
            return null;
          })
          .filter(Boolean);
        if (features.length > 0) {
          evenementsGeoJSON.value = { type: "FeatureCollection", features };
          evenements.value = features.map(f => ({ id: f.id ?? f.properties?.id, properties: f.properties || {}, geometry: f.geometry }));
        } else {
          evenementsGeoJSON.value = null;
          evenements.value = [];
        }
      } else {
        evenementsGeoJSON.value = null;
        evenements.value = [];
      }
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération des événements!", error);
      evenementsGeoJSON.value = null;
      evenements.value = [];
    });
};

const form = reactive({
  ...props.initialForm,
  properties: {
    ...(props.initialForm?.properties || {}),
    code_up: props.initialForm?.properties?.code_up || "",
    nom_up: props.initialForm?.properties?.nom_up || "",
    secteur: props.initialForm?.properties?.secteur || "",
    annee_version: props.initialForm?.properties?.annee_version || new Date().getFullYear().toString(),
    proprios: Array.isArray(props.initialForm?.properties?.proprios) ? [...props.initialForm.properties.proprios] : [],
    version_active: props.initialForm?.properties?.version_active ?? false,
  },
  geometry: props.initialForm?.geometry || null,
 });



// prepare vectorLayers for the map: include quartiers and evenements when available
// const vectorLayers = computed(() => {
//   const layers = [];
//   if (quartiersGeoJSON.value) {
//     layers.push({
//       id: "quartiers",
//       label: "Quartiers",
//       data: quartiersGeoJSON.value,
//       visible: true,
//       style: {
//         color: "#00E5FF",
//         weight: 3,
//         fill: false,
//       },
//       onEachFeature: (feature, layer) => {
//         const props = feature.properties || {};
//         const title = props.nom_quartier || props.code_quartier || "Quartier";
//         layer.bindPopup(title);
//       },
//     });
//   }

//   if (evenementsGeoJSON.value) {
//     layers.push({
//       id: "evenements",
//       label: "Événements",
//       data: evenementsGeoJSON.value,
//       visible: true,
//       // use point style for events (if points), fallback to red outline for polygons
//       style: (feature) => {
//         if (feature.geometry && feature.geometry.type === "Point") return {
//           radius: 8,
//           color: "#F4511E",
//           fillColor: "#F4511E",
//           fillOpacity: 0,
//           weight: 2,
//         };
//         // markers default
//         return { color: "#ff3333", weight: 2, fill: false };
//       },
//       onEachFeature: (feature, layer) => {
//         const props = feature.properties || {};
//         const title = props.description || props.source || "Événement";
//         const date = props.date_evenement || props.date_observation || null;
//         const content = date ? `${title}<br/><small>${date}</small>` : title;
//         layer.bindPopup(content);
//       },
//     });
//   }

//   return layers;
// });

const router = useRouter();

// Variable pour stocker le nextId
const nextId = ref(null);

const fetchNextId = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/unitePastorale/getNextId/`)
    .then((response) => {
      console.log("Next ID response:", response.data);
      nextId.value = response.data.next_id;
      form.id = nextId.value;
      if (!form.properties) form.properties = {};
      form.properties.id_unite_pastorale = nextId.value;
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération du Next ID", error);
    });
};

const proprietairesOptions = computed(() => {
  return (proprietaires.value || []).map((p) => ({
    ...p,
    full_name: `${p.nom_propr || ""} ${p.prenom_propr || ""}`.trim(),
  }));
});

onMounted(() => {
  console.log('UnitePastoraleForm initialForm prop at mount:', props.initialForm);

  fetchRefUPs();

  if (props.mode === 'add') fetchNextId();

  // Récupère la liste des propriétaires fonciers pour le sélecteur de membres
    auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/proprietaireFoncier/`)
    .then((response) => {
      proprietaires.value = response.data;
      console.log("proprietaires:", proprietaires.value);
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération de la liste des propriétaires.", error);
    });

    // initialize proprietaires selection from various possible input shapes
    const initIds = props.initialForm?.properties?.proprios_ids || props.initialForm?.membres_ids || props.initialForm?.proprios_ids;
    if (Array.isArray(initIds)) {
      form.properties.proprios = initIds.map((id) => Number(id));
    }
});

// Watch mode so that when modal opens in 'add' we fetch a next id
watch(() => props.mode, (m) => {
  if (m === 'add') {
    // only fetch if not already set
    if (!form.properties?.id_unite_pastorale && !form.id) fetchNextId();
  }
});

watch(
  () => props.initialForm,
  (newForm) => {
    const isPlainObject = (value) => Object.prototype.toString.call(value) === "[object Object]";
    const isEmptyInitialForm =
      !newForm || (isPlainObject(newForm) && Object.keys(newForm).length === 0);

    // In add mode, parent rerenders can resend an empty initialForm object.
    // Do not reset the local draft (including drawn geometry) in that case.
    if (props.mode === "add" && isEmptyInitialForm) {
      return;
    }

    console.log('UnitePastoraleForm initialForm changed:', newForm);
      try {
        Object.assign(form, JSON.parse(JSON.stringify(newForm || {})));
      } catch (e) {
        Object.assign(form, newForm || {});
      }

      // keep proprietaires selection in sync when initialForm changes
      const initIds = newForm?.properties?.proprios_ids || newForm?.membres_ids || newForm?.proprios_ids;
      if (Array.isArray(initIds)) form.properties.proprios = initIds.map(id => Number(id));
      // ensure id_unite_pastorale is preserved when editing an existing UP
      if (!form.properties) form.properties = {};
      form.properties.id_unite_pastorale = newForm?.properties?.id_unite_pastorale || newForm?.id_unite_pastorale || newForm?.id || form.properties.id_unite_pastorale;
  },
  { deep: true, immediate: true }
);


// Submits
const submitForm = () => {
  if (!props.onSubmit) return;
  // payload propre (deep copy) : enlever champs read-only et n'envoyer l'id que pour update
  const payload = JSON.parse(JSON.stringify(form));
  console.log("Submitting form with payload:", payload);
  // Validate geometry for GeoJSON resources
  if (!payload.geometry) {
    // console.error("Cannot submit: geometry is missing on the UP");
    showMissingGeometry.value = true;
    return; // stop submission without throwing an unhandled rejection
  }
  // Map frontend owner selection to API expected fields
  try {
    const propsObj = payload.properties || {};
    if (Array.isArray(propsObj.proprios) && propsObj.proprios.length > 0) {
      // API may expect `proprietaires` or `proprios_ids` depending on backend; provide both
      
      propsObj.proprios_ids = Array.from(propsObj.proprios);
    }
    payload.properties = propsObj;
  } catch (e) {
    // ignore mapping errors
  }
  if (props.mode === 'add') delete payload.id;
  props.onSubmit(payload)
    .then(() => console.log("Form submitted OK"))
    .catch(err => console.error(err));
};

// Close
const closeModal = () => {
  props.onClose?.();
};
</script>

<style scoped>
.form-ligne {
  padding: 4px;
}

.form-cell {
  padding: 4px;
}

.up-form-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  align-items: start;
}

.up-form-col {
  min-width: 0;
}

.up-section-gap {
  margin-top: 0.75rem;
}

.grid-container {
  border-radius: 5px;
  /* Arrondi des coins de la grille */
  overflow: hidden;
  /* Assure que le contenu s'adapte à l'arrondi */
}

.up-form :deep(.v-input--density-compact .v-field__input) {
  min-height: 38px;
  padding-top: 6px;
  padding-bottom: 6px;
}

.up-form :deep(.v-label.v-field-label) {
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
  pointer-events: none
}

@media (max-width: 1100px) {
  .up-form-layout {
    grid-template-columns: 1fr;
  }
}

</style>
