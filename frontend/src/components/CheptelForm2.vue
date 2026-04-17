<template>
  <h3 class="w3-center w3-margin">{{ formTitle }}</h3>
  <!-- <div class="debug-block" style="margin:0.5rem 0;padding:0.5rem;border:1px dashed #ccc;">
    <div style="font-weight:600;margin-bottom:0.25rem;">initialForm (parent / selectedItem):</div>
    <pre style="max-height:160px;overflow:auto;margin:0 0 0.5rem 0;">{{ JSON.stringify(props.initialForm, null, 2) }}</pre>
    <div style="font-weight:600;margin-bottom:0.25rem;">form (local reactive):</div>
    <pre style="max-height:160px;overflow:auto;margin:0">{{ JSON.stringify(form, null, 2) }}</pre>
  </div> -->

  <form @submit.prevent="submitForm">
    <!-- Ligne 1 : Situation | Eleveur -->
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-select
          id="situation"
          v-model="form.situation_exploitation"
          :items="situations"
          item-title="nom_situation"
          item-value="id_situation"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') || situLocked }"         label="Situation d'exploitation"
          dense
          variant="underlined"
          hide-details
          clearable
        />
      </div>
      <div class="w3-half form-cell">
        <v-select
          id="eleveur"
          v-model="form.eleveur"
          :items="eleveurs"
          item-title="nom_complet"
          item-value="id_eleveur"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Eleveur"
          dense
          variant="underlined"
          hide-details
          clearable
        />
      </div>
    </div>
    <!-- Ligne 1 : Type cheptel | Nombre -->
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-select 
          id="typeCheptel"
          v-model="form.type_cheptel"
          :items="typeCs"
          item-title="description"
          item-value="id_type_cheptel"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Type de cheptel"
          dense
          variant="underlined"
          hide-details
          clearable
        />
      </div>
      <div class="w3-half form-cell">
        <v-text-field
          id="nombre" 
          v-model="form.nombre_animaux"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Nombre d'animaux"
          type="number"
          min="1"
          dense
          variant="underlined"
          hide-details
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
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          dense
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
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          dense
          variant="underlined"
          hide-details
          clearable
        />
      </div>
    </div>
    <div class="w3-row form-ligne">
      <div class="form-cell">
        <v-text-field
          id="description"
          v-model="form.description"
          label="Description"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          dense
          variant="underlined"
          hide-details
          clearable
        />
      </div>
    </div>
    
    <div class="form-actions">
      <v-btn density="comfortable" color="info" @click="closeModal" prepend-icon="mdi-arrow-left-circle">Retour</v-btn>
      <v-btn density="comfortable" v-if="props.mode !== 'view'" color="success" type="submit" prepend-icon="mdi-content-save">{{ btTitle }}</v-btn>
    </div>
  </form>
</template>

<script setup>
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

const { can } = usePermissions("elever");

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
  id_cheptel: null,
  eleveur: "",
  situation_exploitation: "",
  type_cheptel: "",
  nombre_animaux: "",
  description: "",
  date_debut: "",
  date_fin: "",
});

const situations = ref([]);
const eleveurs = ref([]);
const typeCs = ref([]);

const situLocked = computed(() => {
  console.log("initialForm for situLocked:", props.initialForm);
  const initialSitu = props.initialForm && (props.initialForm.situation_exploitation || props.initialForm.situation || props.initialForm.id_situation);
  return !!initialSitu;
});

// Helper to load eleveurs, optionally filtered by exploitant id
const loadEleveurs = (explId) => {
  const useExpl = explId ?? props.explId ?? props.initialForm?.exploitant ?? null;
  if (useExpl) {
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/eleveur/by-exploitant/${useExpl}/`)
      .then((response) => {
        const data = response.data || [];
        eleveurs.value = data.map(e => ({
          ...e,
          nom_complet: e.nom_complet ?? `${e.nom_eleveur || ''} ${e.prenom_eleveur || ''}`.trim()
        }));
        console.log("eleveur (filtered):", eleveurs.value);
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération de la liste des éleveurs.", error);
      });
  } else {
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/eleveur/`)
      .then((response) => {
        const data = response.data || [];
        eleveurs.value = data.map(e => ({
          ...e,
          nom_complet: e.nom_complet ?? `${e.nom_eleveur || ''} ${e.prenom_eleveur || ''}`.trim()
        }));
        console.log("eleveur:", eleveurs.value);
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération de la liste des éleveurs.", error);
      });
  }
};

watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) {
      Object.assign(form, newVal);
      // If initialForm contains an exploitant, reload eleveurs filtered by that exploitant
      if (newVal.exploitant) {
        loadEleveurs(newVal.exploitant);
      }
      else if (newVal.situation_detail && newVal.situation_detail.exploitant) {
        loadEleveurs(newVal.situation_detail.exploitant);
      }
      // If initialForm contains a situation, reload situations filtered accordingly
      const initialSitu = newVal.situation_exploitation || newVal.situation || newVal.id_situation;
      if (initialSitu) {
        auth.axiosInstance
          .get(`${config.API_BASE_URL}/api/situationExploitation/`)
          .then((response) => {
            const data = response.data || [];
            const found = data.find(s => s.id_situation === initialSitu || s.id === initialSitu || (s.properties && (s.properties.id_situation === initialSitu)));
            situations.value = found ? [found] : data.filter(s => s.id_situation === initialSitu || s.id === initialSitu);
            if (situLocked.value) {
              form.situation_exploitation = initialSitu;
            }
          })
          .catch((error) => {
            console.error("Erreur lors de la récupération de la liste des situations d'exploitation.", error);
          });
      }
    }
  },
  { immediate: true }
);

// Next ID pour l'ajout
const nextId = ref(null);
onMounted(() => {
  if (props.mode === "add") {
    // next id for cheptel
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/cheptel/getNextId/`)
      .then(res => {
        nextId.value = res.data.next_id;
        form.id_cheptel = nextId.value;
      })
      .catch(err => console.error("Erreur Next ID cheptel", err));
  };

  // Récupère les situations
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/situationExploitation/`)
    .then((response) => {
      const data = response.data || [];
      const initialSitu = props.initialForm && (props.initialForm.situation_exploitation || props.initialForm.situation || props.initialForm.id_situation);
      if (initialSitu) {
        // try to find the matching situation in the returned list
        const found = data.find(s => s.id_situation === initialSitu || s.id === initialSitu || (s.properties && (s.properties.id_situation === initialSitu)));
        situations.value = found ? [found] : data.filter(s => s.id_situation === initialSitu || s.id === initialSitu);
      } else {
        situations.value = data;
      }
      console.log("situations:", situations.value);
      // If initialForm provided a situation id, ensure the model uses it after items loaded
      if (situLocked.value) {
        form.situation_exploitation = props.initialForm.situation_exploitation || props.initialForm.situation || props.initialForm.id_situation;
      }
    })
    .catch((error) => {
      console.error(
        "Erreur lors de la récupération de la liste des situations d'exploitation.",
        error
      );
    });

  // Récupère les éleveurs via le helper
  loadEleveurs();
  

  // Récupère les types de cheptel
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/type_cheptel/`)
    .then((response) => {
      typeCs.value = response.data;
      console.log("typeCs:", typeCs.value);
    })
    .catch((error) => {
      console.error(
        "Erreur lors de la récupération de la liste des types de cheptel.",
        error
      );
    });
});


// Submits
const submitForm = () => {
  if (props.onSubmit) {
    // Ensure required fields exist for backend
    if (!form.description) {
      const ev = eleveurs.value.find(e => e.id_eleveur === form.eleveur) || {};
      const type = (typeCs.value || []).find(t => t.id_type_cheptel === form.type_cheptel) || {};
      form.description = `${ev.nom_complet || (ev.nom_eleveur ? `${ev.nom_eleveur} ${ev.prenom_eleveur}` : '')} ${type.description ? ' - ' + type.description : ''}`.trim();
    }
    if (!form.id_cheptel) {
      // try to fetch next id synchronously-ish
      auth.axiosInstance.get(`${config.API_BASE_URL}/api/cheptel/getNextId/`).then(res => {
        form.id_cheptel = res.data.next_id;
        props.onSubmit(form).then(() => console.log("Form submitted OK")).catch(err => console.error(err));
      }).catch(err => {
        console.error('Erreur Next ID cheptel', err);
        // fallback: still try to submit
        props.onSubmit(form).then(() => console.log("Form submitted OK")).catch(err => console.error(err));
      });
      return;
    }

    props.onSubmit(form)
      .then(() => console.log("Form submitted OK"))
      .catch(err => console.error(err));
  }
};

// Close
const closeModal = () => {
  props.onClose?.();
};
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
