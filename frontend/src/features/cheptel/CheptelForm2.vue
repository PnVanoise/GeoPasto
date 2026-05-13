<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>

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
            :disabled="props.mode === 'view' || !can('change') || situLocked"
            label="Situation d'exploitation"
            density="compact"
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
            :disabled="props.mode === 'view' || !can('change')"
            label="Eleveur"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
      </div>
      <!-- Ligne : Espèce (filtre UI) -->
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-select
            v-model="selectedEspece"
            :items="especes"
            item-title="description"
            item-value="id_espece"
            :disabled="props.mode === 'view'"
            label="Espèce (filtre)"
            density="compact"
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
            :items="racesFiltrees"
            item-title="description"
            item-value="id_race"
            :disabled="props.mode === 'view'"
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
            :items="categoriesFiltrees"
            item-title="description"
            item-value="id_categorie_animaux"
            :disabled="props.mode === 'view'"
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
            :disabled="props.mode === 'view'"
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
            :disabled="props.mode === 'view'"
            label="Catégorie de pension"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
      </div>
      <!-- Ligne : Nombre d'animaux | Coefficient UGB -->
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-text-field
            id="nombre"
            v-model="form.nombre_animaux"
            :disabled="props.mode === 'view'"
            label="Nombre d'animaux"
            type="number"
            min="1"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
        <div class="w3-half form-cell">
          <v-text-field
            v-model="form.coefficient_UGB"
            label="Coefficient UGB"
            type="number"
            min="0"
            max="1"
            step="0.01"
            :disabled="props.mode === 'view'"
            density="compact"
            variant="underlined"
            hide-details
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
            :disabled="props.mode === 'view'"
            density="compact"
            variant="underlined"
            hide-details
            clearable
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
const especes = ref([]);
const allRaces = ref([]);
const allCategoriesAnimaux = ref([]);

// Espèce sélectionnée — champ UI uniquement, non envoyé au backend
const selectedEspece = ref(null);

const racesFiltrees = computed(() =>
  selectedEspece.value
    ? allRaces.value.filter((r) => r.espece === selectedEspece.value)
    : allRaces.value
);

const categoriesFiltrees = computed(() =>
  selectedEspece.value
    ? allCategoriesAnimaux.value.filter((c) => c.espece === selectedEspece.value)
    : allCategoriesAnimaux.value
);

const situLocked = computed(() => !!props.initialForm?.situation_exploitation);

const loadEleveurs = (explId) => {
  const useExpl = explId ?? props.explId ?? props.initialForm?.exploitant ?? null;
  const url = useExpl
    ? `${config.API_BASE_URL}/api/eleveur/by-exploitant/${useExpl}/`
    : `${config.API_BASE_URL}/api/eleveur/`;
  auth.axiosInstance
    .get(url)
    .then((response) => {
      const data = response.data || [];
      eleveurs.value = data.map((e) => ({
        ...e,
        nom_complet: e.nom_complet ?? `${e.nom_eleveur || ""} ${e.prenom_eleveur || ""}`.trim(),
      }));
    })
    .catch(() => {});
};

watch(
  () => props.initialForm,
  (newVal) => {
    if (!newVal) return;
    Object.assign(form, newVal);

    // Initialise l'espèce depuis les détails de la race ou de la catégorie
    const especeId = newVal.race_detail?.espece ?? newVal.categorie_animaux_detail?.espece ?? null;
    selectedEspece.value = especeId;

    if (newVal.exploitant) {
      loadEleveurs(newVal.exploitant);
    } else if (newVal.situation_detail?.exploitant) {
      loadEleveurs(newVal.situation_detail.exploitant);
    }

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
          if (situLocked.value) form.situation_exploitation = initialSitu;
        })
        .catch(() => {});
    }
  },
  { immediate: true }
);

watch(
  () => form.situation_exploitation,
  (newSituId, oldSituId) => {
    if (newSituId === oldSituId) return;
    const situ = situations.value.find((s) => s.id_situation === newSituId || s.id === newSituId);
    form.eleveur = null;
    loadEleveurs(situ?.exploitant ?? null);
  }
);

watch(selectedEspece, (newEspece) => {
  const raceOk =
    !form.race || allRaces.value.find((r) => r.id_race === form.race)?.espece === newEspece;
  if (!raceOk) form.race = null;

  const catOk =
    !form.categorie_animaux ||
    allCategoriesAnimaux.value.find((c) => c.id_categorie_animaux === form.categorie_animaux)
      ?.espece === newEspece;
  if (!catOk) form.categorie_animaux = null;
});

watch(
  () => form.categorie_animaux,
  (newId) => {
    const cat = allCategoriesAnimaux.value.find((c) => c.id_categorie_animaux === newId);
    if (cat?.coefficient_UGB != null) form.coefficient_UGB = cat.coefficient_UGB;
  }
);

onMounted(() => {
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
      if (situLocked.value) {
        form.situation_exploitation =
          props.initialForm.situation_exploitation ||
          props.initialForm.situation ||
          props.initialForm.id_situation;
      }
    })
    .catch(() => {});

  const explId =
    props.initialForm?.exploitant ?? props.initialForm?.situation_detail?.exploitant ?? null;
  loadEleveurs(explId);

  auth.axiosInstance.get(`${config.API_BASE_URL}/api/espece/`).then((r) => {
    especes.value = r.data;
  });

  auth.axiosInstance.get(`${config.API_BASE_URL}/api/production/`).then((r) => {
    productions.value = r.data;
  });

  auth.axiosInstance.get(`${config.API_BASE_URL}/api/categorie_pension/`).then((r) => {
    pensions.value = r.data;
  });

  auth.axiosInstance.get(`${config.API_BASE_URL}/api/race/`).then((r) => {
    allRaces.value = r.data;
  });

  auth.axiosInstance.get(`${config.API_BASE_URL}/api/categorie_animaux/`).then((r) => {
    allCategoriesAnimaux.value = r.data;
  });
});

const submitForm = () => {
  if (props.onSubmit) {
    if (!form.description) {
      const ev = eleveurs.value.find((e) => e.id_eleveur === form.eleveur) || {};
      form.description =
        `${ev.nom_complet || (ev.nom_eleveur ? `${ev.nom_eleveur} ${ev.prenom_eleveur}` : "")}`.trim();
    }
    props.onSubmit(form);
  }
};

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

.cheptel-form :deep(.v-field--disabled) {
  opacity: 1;
}
.cheptel-form :deep(.v-field--disabled input),
.cheptel-form :deep(.v-field--disabled .v-select__selection-text) {
  color: #000000;
  -webkit-text-fill-color: #000000;
}

.form-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
}
</style>
