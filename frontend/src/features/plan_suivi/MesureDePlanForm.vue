<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <form class="mesure-plan-form" @submit.prevent="submitForm">
    <div class="mesure-layout">
      <section class="layout-card mesure-fields-card">
        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-text-field
              v-model="form.description"
              :disabled="props.mode === 'view'"
              label="Description"
              density="compact"
              variant="underlined"
              hide-details="auto"
              :rules="[maxLen(150)]"
              :counter="150"
              clearable
            />
          </div>
          <div class="w3-half form-cell">
            <v-text-field
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
        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-text-field
              type="date"
              label="Début de période"
              v-model="form.debut_periode"
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
              label="Fin de période"
              v-model="form.fin_periode"
              :disabled="props.mode === 'view'"
              density="compact"
              variant="underlined"
              hide-details="auto"
              clearable
              :rules="rulesFinPeriode"
            />
          </div>
        </div>
        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-select
              v-model="form.type_mesure"
              :items="typemesures"
              item-title="description"
              item-value="id_type_mesure"
              :disabled="props.mode === 'view'"
              label="Type de mesure"
              density="compact"
              variant="underlined"
              hide-details
              clearable
            />
          </div>
          <div class="w3-half form-cell">
            <v-select
              v-model="form.plan_suivi"
              :items="plansuivis"
              item-title="description"
              item-value="id_plan_suivi"
              :disabled="props.mode === 'view'"
              label="Suivi"
              density="compact"
              variant="underlined"
              hide-details
              clearable
            />
          </div>
        </div>
        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <div class="obligation-field" :class="{ 'is-disabled': props.mode === 'view' }">
              <span class="obligation-label">Obligation</span>
              <v-radio-group
                v-model="form.obligation"
                :disabled="props.mode === 'view'"
                inline
                density="compact"
                hide-details
              >
                <v-radio label="Préconisation" :value="false" />
                <v-radio label="Obligation" :value="true" />
              </v-radio-group>
            </div>
          </div>
          <div class="w3-half form-cell">
            <v-select
              v-model="geometryType"
              :items="geometryTypeOptions"
              item-title="label"
              item-value="value"
              :disabled="props.mode === 'view'"
              label="Type de géométrie"
              density="compact"
              variant="underlined"
              hide-details
            />
          </div>
        </div>
        <div
          class="w3-row form-ligne"
          v-if="submitted && !geometryValidity.isValid && form.geometry !== null"
        >
          <div class="form-cell">
            <v-alert
              type="warning"
              variant="tonal"
              density="compact"
              border="start"
              icon="mdi-alert-circle-outline"
            >
              Géométrie invalide — redessinez avant d'enregistrer.
            </v-alert>
          </div>
        </div>
      </section>

      <section class="layout-card mesure-map-card">
        <div class="geometry-status" :class="geometryValidity.isValid ? 'is-set' : 'is-missing'">
          {{ geometryValidity.isValid ? "Géométrie valide" : "Géométrie à dessiner (optionnel)" }}
        </div>
        <QuartierGeometryEditorOl
          v-model="form.geometry"
          :geometryType="geometryType"
          :contextLayers="mapContextLayers"
          :disabled="props.mode === 'view'"
          @geometry-validity-change="onGeometryValidityChange"
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
import QuartierGeometryEditorOl from "../../components/map/QuartierGeometryEditorOl.vue";
import { maxLen } from "@/utils/validators";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" },
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("mesuredeplan");

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
  id_mesure_plan: null,
  description: "",
  commentaire: "",
  debut_periode: "",
  fin_periode: "",
  type_mesure: null,
  plan_suivi: null,
  geometry: null,
  obligation: false,
});

const geometryType = ref("Polygon");
const geometryTypeOptions = [
  { label: "Point", value: "Point" },
  { label: "Polyligne", value: "LineString" },
  { label: "Polygone", value: "Polygon" },
];

const submitted = ref(false);
const geometryValidity = ref({ isValid: false, reason: "geometry_optional" });

const typemesures = ref([]);
const plansuivis = ref([]);
const upContextGeoData = ref(null);

const mapContextLayers = computed(() => {
  if (!upContextGeoData.value) return [];
  return [
    {
      id: "up_outline",
      label: "UP",
      data: upContextGeoData.value,
      style: {
        strokeColor: "#b23a2a",
        strokeWidth: 3,
        fillOpacity: 0,
        lineDash: [10, 7],
        pointRadius: 5,
      },
      visible: true,
    },
  ];
});

const onGeometryValidityChange = (payload) => {
  geometryValidity.value = payload || { isValid: false, reason: "geometry_optional" };
};

const fetchUpForPlan = async (planId) => {
  if (!planId) {
    upContextGeoData.value = null;
    return;
  }
  try {
    const res = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/planSuivi/${planId}/`);
    const upId = res.data?.unite_pastorale;
    if (upId) {
      const upRes = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/unitePastorale/${upId}/`
      );
      const data = upRes.data;
      upContextGeoData.value =
        data?.type === "Feature"
          ? { type: "FeatureCollection", features: [data] }
          : data?.type === "FeatureCollection"
            ? data
            : null;
    } else {
      upContextGeoData.value = null;
    }
  } catch {
    upContextGeoData.value = null;
  }
};

watch(
  () => props.initialForm,
  (newVal) => {
    if (!newVal) return;
    const src = newVal.properties ? { ...newVal.properties } : newVal;
    form.id_mesure_plan = src.id_mesure_plan ?? null;
    form.description = src.description ?? "";
    form.commentaire = src.commentaire ?? "";
    form.debut_periode = src.debut_periode ?? "";
    form.fin_periode = src.fin_periode ?? "";
    form.type_mesure = src.type_mesure ?? null;
    form.plan_suivi = src.plan_suivi ?? null;
    form.geometry = newVal.geometry ?? src.geometry ?? null;
    form.obligation = src.obligation ?? false;
    if (form.geometry?.type) {
      geometryType.value = form.geometry.type;
    }
  },
  { immediate: true, deep: true }
);

watch(
  () => form.plan_suivi,
  (planId) => fetchUpForPlan(planId),
  { immediate: true }
);

watch(
  () => geometryType.value,
  (newType) => {
    if (form.geometry?.type && form.geometry.type !== newType) {
      form.geometry = null;
    }
  }
);

onMounted(() => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/typeMesure/`)
    .then(({ data }) => {
      typemesures.value = data;
    })
    .catch(() => {});

  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/planSuivi/`)
    .then(({ data }) => {
      plansuivis.value = data;
    })
    .catch(() => {});
});

const submitForm = () => {
  submitted.value = true;
  if (props.onSubmit) {
    props.onSubmit({
      id_mesure_plan: form.id_mesure_plan,
      description: form.description,
      commentaire: form.commentaire || null,
      debut_periode: form.debut_periode || null,
      fin_periode: form.fin_periode || null,
      type_mesure: form.type_mesure || null,
      plan_suivi: form.plan_suivi || null,
      geometry: form.geometry ?? null,
      obligation: form.obligation,
    });
  }
};

const rulesFinPeriode = computed(() => [
  (v) =>
    !v ||
    !form.debut_periode ||
    v >= form.debut_periode ||
    "La fin de période doit être postérieure au début de période.",
]);

const isFormValid = computed(() => {
  const debut = form.debut_periode;
  const fin = form.fin_periode;
  return !fin || !debut || fin >= debut;
});

const closeModal = () => {
  props.onClose?.();
};
</script>

<style scoped>
.mesure-layout {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.05fr);
  grid-template-areas: "fields map";
  gap: 1rem;
  align-items: start;
  margin-top: 1rem;
}

.mesure-fields-card {
  grid-area: fields;
  min-width: 0;
}

.mesure-map-card {
  grid-area: map;
  min-width: 0;
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
.geometry-status {
  display: inline-block;
  margin: 0 0 10px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
}
.geometry-status.is-set {
  color: #166534;
  background: #dcfce7;
  border: 1px solid #86efac;
}
.geometry-status.is-missing {
  color: #92400e;
  background: #fef3c7;
  border: 1px solid #fcd34d;
}
.mesure-plan-form :deep(.v-input--density-compact .v-field__input) {
  min-height: 38px;
  padding-top: 6px;
  padding-bottom: 6px;
}
.mesure-plan-form :deep(.v-label.v-field-label) {
  font-size: 0.82rem;
}
.mesure-plan-form :deep(.v-input) {
  font-size: 0.88rem;
}
.mesure-plan-form :deep(.v-field__input),
.mesure-plan-form :deep(.v-select__selection-text) {
  font-size: 0.88rem;
}
.obligation-field {
  padding: 4px 0 2px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.42);
  transition: border-color 140ms ease;
}
.obligation-field:hover {
  border-bottom-color: rgba(0, 0, 0, 0.87);
}
.obligation-field.is-disabled {
  border-bottom-style: dashed;
  opacity: 0.6;
}
.obligation-label {
  display: block;
  font-size: 0.82rem;
  color: rgba(0, 0, 0, 0.6);
  line-height: 1;
  margin-bottom: 2px;
}
.obligation-field :deep(.v-radio-group) {
  padding-top: 0;
}
.obligation-field :deep(.v-label) {
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

@media (max-width: 1100px) {
  .mesure-layout {
    grid-template-columns: 1fr;
    grid-template-areas: "fields" "map";
  }
}
</style>
