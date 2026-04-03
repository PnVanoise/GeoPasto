<template>
  <form @submit.prevent="submitForm">
    <!-- Add your form fields here -->
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
            :class="{ 'disable-events': props.isReadOnly }"
            label="Code UP"
            dense
            hide-details
            clearable
          />
          <!-- <label for="code_up">Code UP:</label>
          <input class="w3-input w3-border" type="text" id="code_up" v-model="form.properties.code_up" required
            :disabled="props.isReadOnly" /> -->
        </div>
        <div class="form-cell">
          <v-text-field
            id="nom_up"
            v-model="form.properties.nom_up"
            :class="{ 'disable-events': props.isReadOnly }"
            label="Nom UP"
            dense
            hide-details
            clearable
          />
          <!-- <label for="nom_up">Nom UP:</label>
          <input class="w3-input w3-border" type="text" id="nom_up" v-model="form.properties.nom_up" required
            :disabled="props.isReadOnly" /> -->
        </div>
        <div class="form-cell">
          <v-text-field
            id="secteur"
            v-model="form.properties.secteur"
            :class="{ 'disable-events': props.isReadOnly }"
            label="Secteur"
            dense
            hide-details
            clearable
          />
          <!-- <label for="secteur">Secteur:</label>
          <input class="w3-input w3-border" type="text" id="secteur" v-model="form.properties.secteur"
            :disabled="props.isReadOnly" /> -->
        </div>
        <div class="form-cell">
          <v-text-field
            id="annee_version"
            v-model="form.properties.annee_version"
            :class="{ 'disable-events': props.isReadOnly }"
            label="Année version"
            dense
            hide-details
            clearable
          />
          <!-- <label for="annee_version">Année version:</label>
          <input class="w3-input w3-border" type="text" id="annee_version" v-model="form.properties.annee_version"
            required :disabled="props.isReadOnly" /> -->
        </div>
        <div class="form-cell">
          <v-switch
            id="version_active"
            v-model="form.properties.version_active"
            :class="{ 'disable-events': props.isReadOnly }"
            label="Version active ?"
            color="primary"
            dense
            hide-details
          />
          <!-- <label for="active">Version active ?</label>
          <input type="checkbox" id="active" v-model="form.properties.version_active" :disabled="props.isReadOnly" /> -->
        </div>
        <!-- <div class="form-cell">
          <label for="proprietaire">Propriétaire :</label>
          <select
            class="w3-input w3-border"
            v-model="form.properties.proprietaire"
            id="proprietaire"
          >
            <option
              v-for="proprietaire in proprietaires"
              :key="proprietaire.id_proprietaire"
              :value="proprietaire.id_proprietaire"
            >
              {{ proprietaire.nom_propr }} {{ proprietaire.prenom_propr }}
            </option>
          </select>
        </div> -->
        <!-- Test grille 1 -->
        <div class="grid-container">
          <h3>Situations d'exploitation</h3>
          <Grid :data="situationExploitations" :columns="situGridColumns" :bgColor="'#f7ba0b'"
            :columnLabels="situColumnLabels" :actions="gridActions" @edit="situOnEdit" @delete="situOnDelete">
          </Grid>
          <div class="form-actions">
            <v-btn density="comfortable" color="info" @click="goToAddSituation" prepend-icon="mdi-plus-circle">
              Nouvelle situation d'exploitation</v-btn>
            <!-- <button v-if="!isReadOnly" type="button" @click="goToAddSituation" class="w3-button w3-blue">
              Nouvelle situation d'exploitation
            </button> -->
          </div>
        </div>

        <div class="grid-container">
          <h3>Quartiers</h3>
          <Grid :data="quartiers" :columns="quarGridColumns" :bgColor="'#f7ba0b'" :columnLabels="quarColumnLabels"
            :actions="gridActions" @edit="quarOnEdit" @delete="quarOnDelete">
          </Grid>
          <div class="form-actions">
            <v-btn density="comfortable" color="info" @click="goToAddQuartier" prepend-icon="mdi-plus-circle">
              Nouveau quartier</v-btn>
            <v-btn density="comfortable" color="info" @click="goToQuartiersList" prepend-icon="mdi-eye">
              Voir les quartiers de l'UP</v-btn>
          <!-- <button v-if="!isReadOnly" type="button" @click="goToAddQuartier" class="w3-button w3-blue">
            Nouveau quartier
          </button>
          <button type="button" @click="goToQuartiersList" class="w3-button w3-blue">
            Voir les quartiers de l'UP
          </button> -->
          </div>
        </div>

        <!-- <div class="grid-container">
          <label>Propriétaires :</label>
          <Grid
            :data="proprietaires"
            :columns="proprGridColumns"
            :bgColor="'#f7ba0b'"
            :columnLabels="proprColumnLabels"
            @edit="proprOnEdit"
            @delete="proprOnDelete"
          >
          </Grid>
          <button type="button" @click="goToAddProprio" class="w3-button w3-blue">
            Nouveau propriétaire
          </button>
        </div> -->

        <!-- next id is readonly -->
        <div v-if="!isEdit" class="form-cell">
          (Next ID:
          {{ nextId }}
          )
        </div>
        <br />
      </div>
      <div style="">
        <div class="form-cell">
              Géométrie:
              <MapEditMultipolygon2
                :key="form.geometry.coordinates"
                v-model="form.geometry"
                :geometryType="'MultiPolygon'"
                :referenceGeometry="refUPs"
                :vector-layers="vectorLayers"
              />
        </div>
      </div>
    </div>
    <div class="form-actions">
      <v-btn density="comfortable" color="info" @click="closeModal" prepend-icon="mdi-arrow-left-circle">Retour</v-btn>
      <v-btn density="comfortable" v-if="!isReadOnly" color="success" type="submit" prepend-icon="mdi-content-save">Enregistrer</v-btn>
      <!-- <button v-if="!isReadOnly" type="submit">Enregistrer</button> -->
    </div>
  </form>
</template>

<script setup>
import { ref, watch, onMounted, computed } from "vue";
import { useRouter } from "vue-router";

import auth from "../../auth";

import config from "../../config";
import MapEditMultipolygon2 from "./MapEditMultipolygon2.vue";
import Grid from "./Grid.vue";

const props = defineProps({
  initialForm: Object,
  isEdit: Boolean,
  isReadOnly: {
    type: Boolean,
    default: false,
  },
  onSubmit: Function,
});

const refUPs = ref([]);

const situGridColumns = ref(["nom_situation", "situation_active"]);
const situColumnLabels = ref({
  nom_situation: "Nom",
  situation_active: "Active ?",
});

const gridActions = computed(() => {
  if (props.isReadOnly) {
    // En mode lecture seule → uniquement la vue
    return {
      view: true,
      edit: false,
      delete: false,
    };
  } else {
    // En mode édition → tout est permis
    return {
      view: true,
      edit: true,
      delete: true,
    };
  }
});

const quarGridColumns = ref(["id", "code_quartier", "nom_quartier"]);
const quarColumnLabels = ref({
  id: "ID",
  code_quartier: "Code",
  nom_quartier: "Nom",
});

// const proprietaires = ref([]);
const situationExploitations = ref([]);
const quartiers = ref([]);
const quartiersGeoJSON = ref(null);
const evenementsGeoJSON = ref(null);
const evenements = ref([]);

const evenGridColumns = ref(["id", "properties.description", "properties.date_evenement"]);
const evenColumnLabels = ref({
  id: "ID",
  "properties.description": "Description",
  "properties.date_evenement": "Date",
});

const goToAddSituation = () => {
  // Utilisation de l'ID de l'UP pour la navigation
  if (form.value.id) {
    console.log("form.value.id : ", form.value.id);
    router.push({
      name: "addSituationWithUPId",
      params: { UPId: form.value.id },
    });
  } else {
    console.warn("L'ID de l'UP n'est pas défini !");
  }
};

const goToAddQuartier = () => {
  // Utilisation de l'ID de l'UP pour la navigations
  if (form.value.id) {
    console.log("form.value.id : ", form.value.id);
    router.push({
      name: "addQuartierWithUPId",
      params: { UPId: form.value.id },
    });
  } else {
    console.warn("L'ID de l'UP n'est pas défini !");
  }
};

const fetchSituations = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/situationExploitation/?id_up=${form.value.id}`)
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
  console.log(`${config.API_BASE_URL}/api/quartierPasto/?up_id=${form.value.id}`);
  // transformer en features
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/quartierPasto/?up_id=${form.value.id}`)
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
      console.log("fetchQuartiers done");
    });
};

const fetchEvenements = () => {
  if (!form.value.id) return;
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/evenement/?up_id=${form.value.id}`)
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

const form = ref({ ...props.initialForm });

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
  if (form.value.id) {
    router.push(`/QuartierPastos/${form.value.id}`);
  } else {
    console.warn("L'ID de l'UP n'est pas défini !");
  }
};

const submitForm = () => {
  console.log("Form submitted with:", form.value);

  if (!props.isEdit) {
    form.value.id = nextId.value;
  }

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
  console.log("Form mounted with geometry:", form.value.geometry);

  // Récupére le prochain ID si on est en mode création uniquement
  if (!props.isEdit) {
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/unitePastorale/getNextId/`)
      .then((response) => {
        nextId.value = response.data.next_id;
        form.value.id = nextId.value;
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération du Next ID", error);
      });
  }
});

watch(
  () => props.initialForm,
  (newForm) => {
    form.value = { ...newForm };
  },
  { deep: true }
);

watch(
  () => form.value.id,
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
