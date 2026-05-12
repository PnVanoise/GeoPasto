<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <!-- <div class="debug-block" style="margin:0.5rem 0;padding:0.5rem;border:1px dashed #ccc;">
    <div style="font-weight:600;margin-bottom:0.25rem;">initialForm (parent / selectedItem):</div>
    <pre style="max-height:160px;overflow:auto;margin:0 0 0.5rem 0;">{{ JSON.stringify(props.initialForm, null, 2) }}</pre>
    <div style="font-weight:600;margin-bottom:0.25rem;">form (local reactive):</div>
    <pre style="max-height:160px;overflow:auto;margin:0">{{ JSON.stringify(form, null, 2) }}</pre>
  </div> -->

  <form class="cheptel-form" @submit.prevent="submitForm">
    <section class="layout-card">
      <!-- Ligne 1 : Situation | Eleveur -->
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-select
            id="situation"
            v-model="form.situation_exploitation"
            :items="situations"
            item-title="nom_situation"
            item-value="id_situation"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') || situLocked }"
            label="Situation d'exploitation"
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
      <!-- Ligne : Nombre d'animaux -->
      <div class="w3-row form-ligne">
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
      <!-- Ligne : Race | Catégorie animaux -->
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-select
            v-model="form.race"
            :items="races"
            item-title="description"
            item-value="id_race"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Race"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
        <div class="w3-half form-cell">
          <v-select
            v-model="form.categorie_animaux"
            :items="categoriesAnimaux"
            item-title="description"
            item-value="id_categorie_animaux"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Catégorie d'animaux"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
      </div>
      <!-- Ligne : Production | Pension -->
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-select
            v-model="form.production"
            :items="productions"
            item-title="description"
            item-value="id_production"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Production"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
        <div class="w3-half form-cell">
          <v-select
            v-model="form.pension"
            :items="pensions"
            item-title="description"
            item-value="id_categorie_pension"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Catégorie de pension"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
      </div>
      <!-- Ligne : Coefficient UGB -->
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-text-field
            v-model="form.coefficient_UGB"
            label="Coefficient UGB"
            type="number"
            min="0"
            max="1"
            step="0.01"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            density="compact"
            variant="underlined"
            hide-details
          />
        </div>
      </div>
    </section>

    <div class="form-actions">
      <v-btn
        density="comfortable"
        color="info"
        @click="closeModal"
        prepend-icon="mdi-arrow-left-circle"
        >Retour</v-btn
      >
      <v-btn
        density="comfortable"
        v-if="props.mode !== 'view'"
        color="success"
        type="submit"
        prepend-icon="mdi-content-save"
        >{{ btTitle }}</v-btn
      >
    </div>
  </form>
</template>

<script setup>
import { reactive, watch, ref, computed, onMounted } from "vue";
import config from "../../../config";
import auth from "@/services/axios";
import { usePermissions } from "../../composables/usePermissions";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" }, // add | change | view
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("cheptel");

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
  nombre_animaux: "",
  description: "",
  date_debut: "",
  date_fin: "",
  coefficient_UGB: 0,
  production: null,
  pension: null,
  race: null,
  categorie_animaux: null,
});

const situations = ref([]);
const eleveurs = ref([]);
const productions = ref([]);
const pensions = ref([]);
const races = ref([]);
const categoriesAnimaux = ref([]);

const situLocked = computed(() => !!props.initialForm?.situation_exploitation);

// Helper to load eleveurs, optionally filtered by exploitant id
const loadEleveurs = (explId) => {
  const useExpl = explId ?? props.explId ?? props.initialForm?.exploitant ?? null;
  if (useExpl) {
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/eleveur/by-exploitant/${useExpl}/`)
      .then((response) => {
        const data = response.data || [];
        eleveurs.value = data.map((e) => ({
          ...e,
          nom_complet: e.nom_complet ?? `${e.nom_eleveur || ""} ${e.prenom_eleveur || ""}`.trim(),
        }));
      })
      .catch((error) => {
      });
  } else {
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/eleveur/`)
      .then((response) => {
        const data = response.data || [];
        eleveurs.value = data.map((e) => ({
          ...e,
          nom_complet: e.nom_complet ?? `${e.nom_eleveur || ""} ${e.prenom_eleveur || ""}`.trim(),
        }));
      })
      .catch((error) => {
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
      } else if (newVal.situation_detail && newVal.situation_detail.exploitant) {
        loadEleveurs(newVal.situation_detail.exploitant);
      }
      // If initialForm contains a situation, reload situations filtered accordingly
      const initialSitu = newVal.situation_exploitation || newVal.situation || newVal.id_situation;
      if (initialSitu) {
        auth.axiosInstance
          .get(`${config.API_BASE_URL}/api/situationExploitation/`)
          .then((response) => {
            const data = response.data || [];
            const found = data.find(
              (s) =>
                s.id_situation === initialSitu ||
                s.id === initialSitu ||
                (s.properties && s.properties.id_situation === initialSitu)
            );
            situations.value = found
              ? [found]
              : data.filter((s) => s.id_situation === initialSitu || s.id === initialSitu);
            if (situLocked.value) {
              form.situation_exploitation = initialSitu;
            }
          })
          .catch((error) => {
              "Erreur lors de la récupération de la liste des situations d'exploitation.",
              error
            );
          });
      }
    }
  },
  { immediate: true }
);

onMounted(() => {
  // Récupère les situations
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/situationExploitation/`)
    .then((response) => {
      const data = response.data || [];
      const initialSitu =
        props.initialForm &&
        (props.initialForm.situation_exploitation ||
          props.initialForm.situation ||
          props.initialForm.id_situation);
      if (initialSitu) {
        // try to find the matching situation in the returned list
        const found = data.find(
          (s) =>
            s.id_situation === initialSitu ||
            s.id === initialSitu ||
            (s.properties && s.properties.id_situation === initialSitu)
        );
        situations.value = found
          ? [found]
          : data.filter((s) => s.id_situation === initialSitu || s.id === initialSitu);
      } else {
        situations.value = data;
      }
      // If initialForm provided a situation id, ensure the model uses it after items loaded
      if (situLocked.value) {
        form.situation_exploitation =
          props.initialForm.situation_exploitation ||
          props.initialForm.situation ||
          props.initialForm.id_situation;
      }
    })
    .catch((error) => {
        "Erreur lors de la récupération de la liste des situations d'exploitation.",
        error
      );
    });

  // Récupère les éleveurs via le helper
  const explId =
    props.initialForm?.exploitant ?? props.initialForm?.situation_detail?.exploitant ?? null;
  loadEleveurs(explId);

  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/production/`)
    .then((response) => {
      productions.value = response.data;
    })

  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/categorie_pension/`)
    .then((response) => {
      pensions.value = response.data;
    })

  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/race/`)
    .then((response) => {
      races.value = response.data;
    })

  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/categorie_animaux/`)
    .then((response) => {
      categoriesAnimaux.value = response.data;
    })
});

// Submits
const submitForm = () => {
  if (props.onSubmit) {
    // Ensure required fields exist for backend
    if (!form.description) {
      const ev = eleveurs.value.find((e) => e.id_eleveur === form.eleveur) || {};
      form.description =
        `${ev.nom_complet || (ev.nom_eleveur ? `${ev.nom_eleveur} ${ev.prenom_eleveur}` : "")}`.trim();
    }
    props
      .onSubmit(form)
  }
};

// Close
const closeModal = () => {
  props.onClose?.();
};
</script>
<style scoped>
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

.cheptel-form :deep(.v-input--density-compact .v-field__input) {
  min-height: 38px;
  padding-top: 6px;
  padding-bottom: 6px;
}

.cheptel-form :deep(.v-label.v-field-label) {
  font-size: 0.82rem;
}

.cheptel-form :deep(.v-input) {
  font-size: 0.88rem;
}

.cheptel-form :deep(.v-field__input),
.cheptel-form :deep(.v-select__selection-text) {
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

.disable-events {
  pointer-events: none;
}
</style>
