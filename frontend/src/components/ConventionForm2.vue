<template>
  <h3 class="w3-center w3-margin">{{ formTitle }}</h3>
  <form @submit.prevent="submitForm">
    <div
      style="
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        align-items: stretch;
      "
    >
      <div style="">
        
        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-select
              id="exploitant"
              v-model="form.properties.exploitant"
              :items="exploitants"
              item-title="nom_exploitant"
              item-value="id_exploitant"
              :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
              label="Exploitant"
              dense
              hide-details
              clearable
            />
          </div>

          <div class="w3-half form-cell">
            <v-select 
              id="unitepastorale"
              v-model="form.properties.unite_pastorale"
              :items="ups"
              item-title="nom_up"
              item-value="id_unite_pastorale"
              :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
              label="Unité pastorale"
              dense
              hide-details
              clearable
            />
          </div>
        </div>

        
        <div class="w3-row form-ligne">
          <div class="w3-row form_cell">
            <v-select
              id="type_convention"
              v-model.number="form.properties.type_convention"
              :items="typeCs"
              item-title="description"
              item-value="id_type_convention"
              :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
              label="Type de convention"
              dense
              hide-details
              clearable
            />
          </div>
        </div>
        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">        
            <v-text-field
              id="dateDebut"
              type="date"
              label="Date de début"
              v-model="form.properties.date_debut"
              :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
              dense
              hide-details
              clearable
            />
          </div>
          <div class="w3-half form-cell">
            <v-text-field
              id="dateFin"
              type="date"
              label="Date de fin"
              v-model="form.properties.date_fin"
              :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
              dense
              hide-details
              clearable
            />
          </div>
        </div>

        
        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">        
            <v-text-field
              id="dateDebutExp"
              type="date"
              label="Début période exploitation"
              v-model="form.properties.debut_periode_expl"
              :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
              dense
              hide-details
              clearable
            />
          </div>
          <div class="w3-half form-cell">
            <v-text-field
              id="dateFinExp"
              type="date"
              label="Fin période exploitation"
              v-model="form.properties.fin_periode_expl"
              :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
              dense
              hide-details
              clearable
            />
          </div>
        </div>
        
        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-text-field
              id="surfaceLoc"
              type="number"
              label="Surface location (ha)"
              v-model="form.properties.surface_location"
              :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
              dense
              hide-details
              clearable
            />
            <!-- <label for="surfaceloc">Surface location:</label>
            <input
              class="w3-input w3-border"
              type="text"
              id="surfaceloc"
              v-model="form.properties.surface_location"
              required
            /> -->
          </div>
          <div class="w3-half form-cell">
            <v-text-field
              id="surfaceExp"
              type="number"
              label="Surface exploitable (ha)"
              v-model="form.properties.surface_exploitable"
              :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
              dense
              hide-details
              clearable
            />
            <!-- <label for="surfaceexp">Surface exploitable:</label>
            <input
              class="w3-input w3-border"
              type="text"
              id="surfaceexp"
              v-model="form.properties.surface_exploitable"
              required
            /> -->
          </div>
        </div>

        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-text-field
              id="effBo"
              type="number"
              label="Effectif bovin"
              v-model="form.properties.effectif_bovin"
              :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
              dense
              hide-details
              clearable
            />

            <!-- <label for="effBo">Effectif bovin:</label>
            <input
              class="w3-input w3-border"
              type="text"
              id="effBo"
              v-model="form.properties.effectif_bovin"
              required
            /> -->
          </div>
          <div class="w3-half form-cell">
            <v-text-field
              id="effOv"
              type="number"
              label="Effectif ovin"
              v-model="form.properties.effectif_ovin"
              :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
              dense
              hide-details
              clearable
            />
            <!-- <label for="effOv">Effectif ovin:</label>
            <input
              class="w3-input w3-border"
              type="text"
              id="effOv"
              v-model="form.properties.effectif_ovin"
              required
            /> -->
          </div>
        </div>
        
        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-text-field
              id="effCa"
              type="number"
              label="Effectif caprin"
              v-model="form.properties.effectif_caprin"
              :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
              dense
              hide-details
              clearable
            />
            <!-- <label for="effCa">Effectif caprin:</label>
            <input
              class="w3-input w3-border"
              type="text"
              id="effCa"
              v-model="form.properties.effectif_caprin"
              required
            /> -->
          </div>
          <div class="w3-half form-cell">
            <v-text-field
              id="effPo"
              type="number"
              label="Effectif porcin"
              v-model="form.properties.effectif_porcin"
              :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
              dense
              hide-details
              clearable
            />
          </div>
        </div>
      </div>
      <div style="">
        <div class="form-cell">
          Géométrie:
          <MapEditMultipolygon2
            :key="form.geometry.coordinates"
            v-model="form.geometry"
            :geometryType="'Polygon'"
          />
        </div>
      </div>
    </div>

    <div class="form-actions">      
      <v-btn
        color="info" @click="closeModal"
        prepend-icon="mdi-arrow-left-circle">
        Retour</v-btn>

      <v-btn
        v-if="props.mode !== 'view'"
        color="success"
        type="submit"
        prepend-icon="mdi-content-save">
        {{ btTitle }}</v-btn>
      
    </div>
  </form>
</template>

<script setup>
import MapEditMultipolygon2 from "./MapEditMultipolygon2.vue";
import { reactive, watch, ref, computed, onMounted } from "vue";
import config from "../../config";
import auth from "../../auth";
import { usePermissions } from "../composables/usePermissions";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" }, // add | change | view
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("conventiondexploitation");

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

const exploitants = ref([]);
const ups = ref([]);
const typeCs = ref([]);

const form = reactive({
  id: null,
  properties: {
    surface_location: "",
    surface_exploitable: "",
    date_debut: "",
    date_fin: "",
    effectif_bovin: "",
    effectif_ovin: "",
    effectif_caprin: "",
    effectif_porcin: "",
    debut_periode_expl: "",
    fin_periode_expl: "",
    up_nom: "",
    exploitant_nom: "",
  },
  geometry: {
    type: "Polygon",
    coordinates: [],
  },
});

// Submits
const submitForm = () => {
  if (props.onSubmit) {
    return props.onSubmit(form)
      .then(() => console.log("Form submitted OK"))
      .catch((err) => console.error(err));
  }
};

// Close
const closeModal = () => {
  props.onClose?.();
};

watch(
  () => props.initialForm,
  (newForm) => {
    console.log("ConventionForm2 initialForm changed:", newForm);

    // Reset when no form
    if (!newForm) {
      form.id = null;
      form.properties = {
        surface_location: "",
        surface_exploitable: "",
        date_debut: "",
        date_fin: "",
        effectif_bovin: "",
        effectif_ovin: "",
        effectif_caprin: "",
        effectif_porcin: "",
        debut_periode_expl: "",
        fin_periode_expl: "",
        up_nom: "",
        exploitant_nom: "",
      };
      form.geometry = { type: "Polygon", coordinates: [] };
      return;
    }

    // If already a Feature-like object
    if (newForm.properties) {
      try {
        const clone = JSON.parse(JSON.stringify(newForm || {}));
        form.id = clone.id ?? null;
        form.properties = clone.properties || {};
        form.geometry = clone.geometry || { type: "Polygon", coordinates: [] };
      } catch (e) {
        form.id = newForm.id ?? null;
        form.properties = { ...(newForm.properties || {}) };
        form.geometry = newForm.geometry || { type: "Polygon", coordinates: [] };
      }
      console.log("Normalized form (from Feature):", form);
      return;
    }

    // Flattened object: move non-meta keys into properties
    const propsBag = {};
    Object.keys(newForm).forEach((k) => {
      if (k === "id" || k === "geometry") return;
      propsBag[k] = newForm[k];
    });
    form.id = newForm.id ?? null;
    form.properties = propsBag;
    form.geometry = newForm.geometry || { type: "Polygon", coordinates: [] };
    console.log("Normalized form (from flattened):", form);
  },
  { deep: true, immediate: true }
);

watch(
  () => form.id,
  (newId) => {
    if (newId) {
      fetchTypesConvention();
      fetchExploitants();
      fetchUPs();
    }
  }
);


const fetchTypesConvention = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/typeConvention/`)
    .then((response) => {
      const data = response.data;
      console.log("list response data:", response.data);
      if (data && data.type === 'FeatureCollection' && Array.isArray(data.features)) {
        typeCs.value = data.features.map(f => f.properties || {});
      } else {
        typeCs.value = Array.isArray(data) ? data : data || [];
      }
      console.log("fetchTypesConvention.value:", typeCs.value);

    })
    .catch((error) => {
      console.error("There was an error!", error);
    })
    .finally(() => {
      //isLoading.value = false;
      console.log("fetchTypesConvention done");
    });
};

const fetchExploitants = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/exploitant/`)
    .then((response) => {
      const data = response.data;
      console.log("list response data:", response.data);
      if (data && data.type === 'FeatureCollection' && Array.isArray(data.features)) {
        exploitants.value = data.features.map(f => ({ ...(f.properties || {}), id: f.id }));
      } else {
        exploitants.value = Array.isArray(data) ? data : data || [];
      }
      console.log("fetchExploitants.value:", exploitants.value);

    })
    .catch((error) => {
      console.error("There was an error!", error);
    })
    .finally(() => {
      //isLoading.value = false;
      console.log("fetchExploitants done");
    });
};

const fetchUPs = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/unitePastorale/light/`)
    .then((response) => {
      const data = response.data;
      console.log("list response data:", response.data);
      if (data && data.type === 'FeatureCollection' && Array.isArray(data.features)) {
        ups.value = data.features.map(f => ({ ...(f.properties || {}), id: f.id }));
      } else {
        ups.value = Array.isArray(data) ? data : data || [];
      }
      console.log("fetchUPs.value:", ups.value);

    })
    .catch((error) => {
      console.error("There was an error!", error);
    })
    .finally(() => {
      //isLoading.value = false;
      console.log("fetchUPs done");
    });
};

// Also load reference lists at mount so selects are populated for add/edit
onMounted(() => {
  fetchTypesConvention();
  fetchExploitants();
  fetchUPs();
});

</script>


<style scoped>
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
