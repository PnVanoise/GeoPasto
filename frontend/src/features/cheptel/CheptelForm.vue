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
            id="proprietaire"
            v-model="proprietaireKey"
            :items="proprietaires"
            item-title="label"
            item-value="key"
            :disabled="props.mode === 'view' || !can('change')"
            label="Propriétaire"
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
            hide-details="auto"
            clearable
            :rules="rulesDateDebut"
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
            hide-details="auto"
            clearable
            :rules="rulesDateFin"
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
            hide-details="auto"
            :rules="[maxLen(150)]"
            :counter="150"
            clearable
          />
        </div>
      </div>
      <div class="w3-row form-ligne">
        <div class="form-cell">
          <v-textarea
            v-model="form.commentaire"
            label="Commentaire"
            :disabled="props.mode === 'view'"
            density="compact"
            variant="underlined"
            hide-details
            rows="2"
            auto-grow
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
        :disabled="!isFormValid"
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
import { maxLen } from "@/utils/validators";

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
  eleveur: null,
  exploitant_proprietaire: null,
  situation_exploitation: "",
  nombre_animaux: "",
  description: "",
  commentaire: "",
  date_debut: "",
  date_fin: "",
  coefficient_UGB: 0,
  production: null,
  pension: null,
  race: null,
  categorie_animaux: null,
});

const situations = ref([]);
const proprietaires = ref([]);
const proprietaireKey = ref(null);

const makeKey = (type, id) => (id ? `${type}-${id}` : null);
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

const loadProprietaires = (explId) => {
  const useExpl = explId ?? props.explId ?? props.initialForm?.exploitant ?? null;
  if (!useExpl) {
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/eleveur/`)
      .then((response) => {
        const data = response.data || [];
        proprietaires.value = data.map((e) => ({
          key: makeKey("eleveur", e.id_eleveur),
          type: "eleveur",
          id: e.id_eleveur,
          label:
            e.nom_complet ??
            `${(e.nom_eleveur || "").toUpperCase()} ${e.prenom_eleveur || ""}`.trim(),
        }));
        ensureProprietaireOption();
      })
      .catch(() => {});
    return;
  }
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/exploitant/${useExpl}/proprietaires/`)
    .then((response) => {
      const data = response.data || [];
      proprietaires.value = data.map((p) => ({
        key: makeKey(p.type, p.id),
        type: p.type,
        id: p.id,
        label: p.label,
      }));
      ensureProprietaireOption();
    })
    .catch(() => {});
};

// Si la valeur sélectionnée (en mode edit/view) ne fait pas partie de la liste
// renvoyée par l'API (cas d'un propriétaire qui n'est plus membre), l'ajouter
// pour préserver l'affichage.
const ensureProprietaireOption = () => {
  if (!proprietaireKey.value) return;
  if (proprietaires.value.some((p) => p.key === proprietaireKey.value)) return;
  const [type, idStr] = proprietaireKey.value.split("-");
  const id = Number(idStr);
  if (type === "eleveur" && props.initialForm?.eleveur_detail) {
    const d = props.initialForm.eleveur_detail;
    proprietaires.value.push({
      key: proprietaireKey.value,
      type: "eleveur",
      id,
      label:
        d.nom_complet || `${(d.nom_eleveur || "").toUpperCase()} ${d.prenom_eleveur || ""}`.trim(),
    });
  } else if (type === "exploitant" && props.initialForm?.exploitant_proprietaire_detail) {
    const d = props.initialForm.exploitant_proprietaire_detail;
    proprietaires.value.push({
      key: proprietaireKey.value,
      type: "exploitant",
      id,
      label: d.nom_exploitant,
    });
  }
};

watch(
  () => props.initialForm,
  (newVal) => {
    if (!newVal) return;
    Object.assign(form, newVal);

    // Initialise l'espèce depuis les détails de la race ou de la catégorie
    const especeId = newVal.race_detail?.espece ?? newVal.categorie_animaux_detail?.espece ?? null;
    selectedEspece.value = especeId;

    // Initialise la clé propriétaire depuis les champs reçus
    if (newVal.eleveur) {
      proprietaireKey.value = makeKey("eleveur", newVal.eleveur);
    } else if (newVal.exploitant_proprietaire) {
      proprietaireKey.value = makeKey("exploitant", newVal.exploitant_proprietaire);
    }

    if (newVal.exploitant) {
      loadProprietaires(newVal.exploitant);
    } else if (newVal.situation_detail?.exploitant) {
      loadProprietaires(newVal.situation_detail.exploitant);
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
    proprietaireKey.value = null;
    form.eleveur = null;
    form.exploitant_proprietaire = null;
    loadProprietaires(situ?.exploitant ?? null);
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
  loadProprietaires(explId);

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
  if (!props.onSubmit) return;

  form.eleveur = null;
  form.exploitant_proprietaire = null;
  const selected = proprietaires.value.find((p) => p.key === proprietaireKey.value);
  if (selected) {
    if (selected.type === "eleveur") form.eleveur = selected.id;
    else if (selected.type === "exploitant") form.exploitant_proprietaire = selected.id;
  }

  if (!form.description && selected) {
    form.description = selected.label || "";
  }
  props.onSubmit(form);
};

const selectedSituation = computed(
  () => situations.value.find((s) => s.id_situation === form.situation_exploitation) ?? null
);
const situDateDebut = computed(() => selectedSituation.value?.date_debut ?? null);
const situDateFin = computed(() => selectedSituation.value?.date_fin ?? null);

const rulesDateDebut = computed(() => [
  (v) =>
    !v ||
    !situDateDebut.value ||
    v >= situDateDebut.value ||
    `Date antérieure au début de la situation (${situDateDebut.value}).`,
  (v) =>
    !v ||
    !situDateFin.value ||
    v <= situDateFin.value ||
    `Date postérieure à la fin de la situation (${situDateFin.value}).`,
]);

const rulesDateFin = computed(() => [
  (v) =>
    !v ||
    !form.date_debut ||
    v >= form.date_debut ||
    "La date de fin doit être postérieure à la date de début.",
  (v) =>
    !v ||
    !situDateDebut.value ||
    v >= situDateDebut.value ||
    `Date antérieure au début de la situation (${situDateDebut.value}).`,
  (v) =>
    !v ||
    !situDateFin.value ||
    v <= situDateFin.value ||
    `Date postérieure à la fin de la situation (${situDateFin.value}).`,
]);

const isFormValid = computed(() => {
  const debut = form.date_debut;
  const fin = form.date_fin;
  if (fin && debut && fin < debut) return false;
  if (situDateDebut.value) {
    if (debut && debut < situDateDebut.value) return false;
    if (fin && fin < situDateDebut.value) return false;
  }
  if (situDateFin.value) {
    if (debut && debut > situDateFin.value) return false;
    if (fin && fin > situDateFin.value) return false;
  }
  return true;
});

watch([() => form.situation_exploitation, situations], () => {
  if (props.mode !== "add" || !selectedSituation.value) return;
  form.date_debut = situDateDebut.value ?? "";
  form.date_fin = situDateFin.value ?? "";
});

const closeModal = () => {
  props.onClose?.();
};
</script>
<style scoped>
.cheptel-form :deep(.v-field--disabled) {
  opacity: 1;
}
.cheptel-form :deep(.v-field--disabled input),
.cheptel-form :deep(.v-field--disabled .v-select__selection-text) {
  color: #000000;
  -webkit-text-fill-color: #000000;
}
</style>
