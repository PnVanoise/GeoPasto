<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <form class="garde-situation-form" @submit.prevent="submitForm">
    <section class="layout-card">
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-select
            id="situation"
            v-model="form.situation_exploitation"
            :items="situations"
            item-title="nom_situation"
            item-value="id_situation"
            :disabled="props.mode === 'view'"
            label="Situation d'exploitation"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
        <div class="w3-half form-cell">
          <v-select
            id="berger"
            v-model="form.berger"
            :items="bergers"
            item-title="fullName"
            item-value="id_berger"
            :disabled="props.mode === 'view'"
            label="Berger"
            density="compact"
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
            id="commentaire"
            v-model="form.commentaire"
            :disabled="props.mode === 'view'"
            label="Commentaire"
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

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" }, // add | change | view
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("gardesituation");

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
  situation_exploitation: "",
  berger: "",
  date_debut: "",
  date_fin: "",
  commentaire: "",
});

const situations = ref([]);
const bergers = ref([]);

watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) {
      Object.assign(form, newVal);
    }
  },
  { immediate: true }
);

onMounted(() => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/situationExploitation/`)
    .then((response) => {
      situations.value = response.data;
    })
    .catch((error) => {});

  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/berger/`)
    .then((response) => {
      bergers.value = response.data.map((b) => ({
        ...b,
        fullName: `${b.nom_berger} ${b.prenom_berger}`,
      }));
    })
    .catch((error) => {});
});

const selectedSituation = computed(
  () => situations.value.find((s) => s.id_situation === form.situation_exploitation) ?? null
);
const situDateDebut = computed(() => selectedSituation.value?.date_debut ?? null);
const situDateFin = computed(() => selectedSituation.value?.date_fin ?? null);

const rulesDateDebut = computed(() => [
  (v) => !!v || "La date de début est obligatoire.",
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
  if (!debut) return false;
  if (fin && fin < debut) return false;
  if (situDateDebut.value) {
    if (debut < situDateDebut.value) return false;
    if (fin && fin < situDateDebut.value) return false;
  }
  if (situDateFin.value) {
    if (debut > situDateFin.value) return false;
    if (fin && fin > situDateFin.value) return false;
  }
  return true;
});

watch([() => form.situation_exploitation, situations], () => {
  if (props.mode !== "add" || !selectedSituation.value) return;
  form.date_debut = situDateDebut.value ?? "";
  form.date_fin = situDateFin.value ?? "";
});

const submitForm = () => {
  if (props.onSubmit) {
    props.onSubmit(form);
  }
};

const closeModal = () => {
  props.onClose?.();
};
</script>
