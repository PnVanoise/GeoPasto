<template>
  <h3 class="w3-center w3-margin">{{ formTitle }}</h3>
  
  <form @submit.prevent="submitForm">
    <div style="
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        align-items: stretch;
      ">
      <div style="">
        <div class="form-cell">
          <v-text-field
            id="code_up"
            v-model="form.properties.code_up"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Code UP"
            dense
            hide-details
            clearable
          />
        </div>
        <div class="form-cell">
          <v-text-field
            id="nom_up"
            v-model="form.properties.nom_up"
            class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Nom UP"
            dense
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
            dense
            hide-details
            clearable
          />
        </div>
        <div class="form-cell">
          <v-text-field
            id="annee_version"
            v-model="form.properties.annee_version"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Année version"
            dense
            hide-details
            clearable
          />
        </div>
        <div class="form-cell">
          <v-switch
            id="version_active"
            v-model="form.properties.version_active"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Version active ?"
            color="primary"
            dense
            hide-details
          />
        </div>
        <!-- Test grille 1 -->
        <div class="grid-container">
          <h3>Situations d'exploitation</h3>
          <h4>A compléter</h4>
          <!-- <Grid :data="situationExploitations" :columns="situGridColumns" :bgColor="'#f7ba0b'"
            :columnLabels="situColumnLabels" :actions="gridActions" @edit="situOnEdit" @delete="situOnDelete">
          </Grid>
          <div class="form-actions">
            <v-btn density="comfortable" color="info" @click="goToAddSituation" prepend-icon="mdi-plus-circle">
              Nouvelle situation d'exploitation</v-btn>
          </div> -->
        </div>

        <div class="grid-container">
          <h3>Quartiers</h3>
          <h4>A DEPLACER DANS LES SITUATIONS</h4>
          <!-- <Grid :data="quartiers" :columns="quarGridColumns" :bgColor="'#f7ba0b'" :columnLabels="quarColumnLabels"
            :actions="gridActions" @edit="quarOnEdit" @delete="quarOnDelete">
          </Grid>
          <div class="form-actions">
            <v-btn density="comfortable" color="info" @click="goToAddQuartier" prepend-icon="mdi-plus-circle">
              Nouveau quartier</v-btn>
            <v-btn density="comfortable" color="info" @click="goToQuartiersList" prepend-icon="mdi-eye">
              Voir les quartiers de l'UP</v-btn> -->
          <!-- <button v-if="!isReadOnly" type="button" @click="goToAddQuartier" class="w3-button w3-blue">
            Nouveau quartier
          </button>
          <button type="button" @click="goToQuartiersList" class="w3-button w3-blue">
            Voir les quartiers de l'UP
          </button>
          </div> -->
        </div>
        <br />
      </div>
      <div style="">
        <div class="form-cell">
              <h3>Géométrie</h3>
              <h4>A compléter</h4>
              <MapEditMultipolygon2
                :key="form.geometry ? JSON.stringify(form.geometry) : 'no-geom'"
                v-model="form.geometry"
                :geometryType="'MultiPolygon'"
                :referenceGeometry="refUPs"
                :vector-layers="vectorLayers"
              />
        </div>
      </div>
      <!-- Membres -->
      <div class="form-cell">
        <v-select
          id="membres"
          v-model="form.properties.proprios"
          :items="proprietaires"
          item-value="id_proprietaire"
          :item-title="proprietaire => proprietaire.nom_propr + ' ' + proprietaire.prenom_propr"
          multiple
          chips
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Membres"
          :menu-props="{ maxHeight: '300px' }"
        />
      </div>
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
import MapEditMultipolygon2 from "./MapEditMultipolygon2.vue";
import Grid from "./Grid.vue";

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

// const situGridColumns = ref(["nom_situation", "situation_active"]);
// const situColumnLabels = ref({
//   nom_situation: "Nom",
//   situation_active: "Active ?",
// });

// const gridActions = computed(() => {
//   if (props.isReadOnly) {
//     // En mode lecture seule → uniquement la vue
//     return {
//       view: true,
//       edit: false,
//       delete: false,
//     };
//   } else {
//     // En mode édition → tout est permis
//     return {
//       view: true,
//       edit: true,
//       delete: true,
//     };
//   }
// });

// const quarGridColumns = ref(["id", "code_quartier", "nom_quartier"]);
// const quarColumnLabels = ref({
//   id: "ID",
//   code_quartier: "Code",
//   nom_quartier: "Nom",
// });

// const proprietaires = ref([]);
const situationExploitations = ref([]);
const quartiers = ref([]);
const quartiersGeoJSON = ref(null);
const evenementsGeoJSON = ref(null);
const evenements = ref([]);


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

const fetchQuartiers = () => {
  console.log(`${config.API_BASE_URL}/api/quartierPasto/?up_id=${form.id}`);
  // transformer en features
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/quartierPasto/?up_id=${form.id}`)
    .then((response) => {
      const data = response.data;
      console.log("list response data:", response.data);
      console.log("fetchQuartiers.value:", quartiers.value);

      if (data.type === "FeatureCollection") {
        // Transformer les features en tableau
        quartiers.value = data.features.map((feature) => {
          return {
            ...feature.properties, // Ajoute toutes les propriétés
            id: feature.id, // Ajoute l'id
          };
        });
        // keep the full GeoJSON for map overlay
        quartiersGeoJSON.value = data;
      } else {
        quartiersGeoJSON.value = null;
      }
    })
    .catch((error) => {
      console.error("There was an error!", error);
    })
    .finally(() => {
      //isLoading.value = false;
      console.log("fetchQuartiers done");
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

const proprietaires = ref([]);

// prepare vectorLayers for the map: include quartiers and evenements when available
const vectorLayers = computed(() => {
  const layers = [];
  if (quartiersGeoJSON.value) {
    layers.push({
      id: "quartiers",
      label: "Quartiers",
      data: quartiersGeoJSON.value,
      visible: true,
      style: {
        color: "#00E5FF",
        weight: 3,
        fill: false,
      },
      onEachFeature: (feature, layer) => {
        const props = feature.properties || {};
        const title = props.nom_quartier || props.code_quartier || "Quartier";
        layer.bindPopup(title);
      },
    });
  }

  if (evenementsGeoJSON.value) {
    layers.push({
      id: "evenements",
      label: "Événements",
      data: evenementsGeoJSON.value,
      visible: true,
      // use point style for events (if points), fallback to red outline for polygons
      style: (feature) => {
        if (feature.geometry && feature.geometry.type === "Point") return {
          radius: 8,
          color: "#F4511E",
          fillColor: "#F4511E",
          fillOpacity: 0,
          weight: 2,
        };
        // markers default
        return { color: "#ff3333", weight: 2, fill: false };
      },
      onEachFeature: (feature, layer) => {
        const props = feature.properties || {};
        const title = props.description || props.source || "Événement";
        const date = props.date_evenement || props.date_observation || null;
        const content = date ? `${title}<br/><small>${date}</small>` : title;
        layer.bindPopup(content);
      },
    });
  }

  return layers;
});

const router = useRouter();

// Variable pour stocker le nextId
const nextId = ref(null);

const goToQuartiersList = () => {
  // Utilisation de l'ID de l'UP pour la navigation
  if (form.id) {
    router.push(`/QuartierPastos/${form.id}`);
  } else {
    console.warn("L'ID de l'UP n'est pas défini !");
  }
};

// const submitForm = () => {
//   console.log("Form submitted with:", form.value);

//   if (!props.isEdit) {
//     form.value.id = nextId.value;
//   }

//   props
//     .onSubmit(form.value)
//     .then(() => {
//       console.log("Form submission then block executed");
//     })
//     .catch((error) => {
//       console.error("There was an error in form submission!", error);
//     });
// };

onMounted(() => {
  console.log('UnitePastoraleForm initialForm prop at mount:', props.initialForm);

  // Récupére le prochain ID si on est en mode création uniquement
  const fetchNextId = () => {
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/unitePastorale/getNextId/`)
      .then((response) => {
        console.log("Next ID response:", response.data);
        nextId.value = response.data.next_id;
        form.id = nextId.value;
        // set domain-specific id inside properties as API expects
        if (!form.properties) form.properties = {};
        form.properties.id_unite_pastorale = nextId.value;
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération du Next ID", error);
      });
  };

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
    console.log('UnitePastoraleForm initialForm changed:', newForm);
      try {
        Object.assign(form, JSON.parse(JSON.stringify(newForm || {})));
      } catch (e) {
        Object.assign(form, newForm || {});
      }
      // assurer l'ID pour le mode "change" (compatibilité id / id_unite_pastorale)
      // if (newForm.id_unite_pastorale) form.id_unite_pastorale = newForm.id_unite_pastorale;
      // else if (newForm.id) form.id_unite_pastorale = newForm.id;


      // keep proprietaires selection in sync when initialForm changes
      const initIds = newForm?.properties?.proprios_ids || newForm?.membres_ids || newForm?.proprios_ids;
      if (Array.isArray(initIds)) form.properties.proprios = initIds.map(id => Number(id));
      // ensure id_unite_pastorale is preserved when editing an existing UP
      if (!form.properties) form.properties = {};
      form.properties.id_unite_pastorale = newForm?.properties?.id_unite_pastorale || newForm?.id_unite_pastorale || newForm?.id || form.properties.id_unite_pastorale;
  },
  { deep: true, immediate: true }
);

watch(
  () => form.id,
  (newId) => {
    if (newId) {
      fetchSituations();
      fetchQuartiers();
      fetchRefUPs();
      fetchEvenements();
    }
  }
);

// Méthode pour gérer l'édition
function situOnEdit(entry) {
  console.log("Éditer:", entry.id_situation);
  router.push(`/SituationExploitation/edit/${entry.id_situation}`);
}

// Méthode pour gérer la suppression
function situOnDelete(entry) {
  console.log("Supprimer:", entry.id_situation);
  deleteSituation(entry.id_situation);
}

const deleteSituation = (id) => {
  auth.axiosInstance
    .delete(`${config.API_BASE_URL}/api/situationExploitation/${id}/`)
    .then((response) => {
      fetchSituations();
      mainStore.setSuccessMessage("Situation d'exploitation supprimée!");
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

// Méthode pour gérer l'édition
function quarOnEdit(entry) {
  console.log("Éditer:", entry.id_quartier);
  router.push(`/QuartierPasto/edit/${entry.id_quartier}`);
}

// Méthode pour gérer la suppression
function quarOnDelete(entry) {
  console.log("Supprimer:", entry.id_quartier);
  deleteQuartier(entry.id_quartier);
}

const deleteQuartier = (id) => {
  auth.axiosInstance
    .delete(`${config.API_BASE_URL}/api/quar/${id}/`)
    .then((response) => {
      fetchSituations();
      mainStore.setSuccessMessage("Situation d'exploitation supprimée!");
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

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
  padding: 8px;
}

.form-cell {
  padding: 8px;
}

.grid-container {
  border-radius: 5px;
  /* Arrondi des coins de la grille */
  overflow: hidden;
  /* Assure que le contenu s'adapte à l'arrondi */
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

</style>
