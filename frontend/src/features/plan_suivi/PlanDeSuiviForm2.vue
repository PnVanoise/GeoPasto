<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <form class="plan-suivi-form" @submit.prevent="submitForm">
    <section class="layout-card">
      <div class="w3-row form-ligne">
        <div class="form-cell">
          <v-text-field
            v-model="form.description"
            :disabled="props.mode === 'view'"
            label="Description"
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
            hide-details="auto"
            clearable
            :rules="rulesDateFin"
          />
        </div>
      </div>
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-select
            v-model="form.type_suivi"
            :items="typesuivis"
            item-title="description"
            item-value="id_type_suivi"
            :disabled="props.mode === 'view'"
            label="Type de suivi"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
        <div class="w3-half form-cell">
          <v-select
            v-model="form.unite_pastorale"
            :items="ups"
            item-title="nom_up"
            item-value="id_unite_pastorale"
            :disabled="props.mode === 'view'"
            label="Unité pastorale"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
      </div>
    </section>

    <template v-if="props.mode !== 'add' && form.id_plan_suivi">
      <section class="layout-card mesures-card">
        <v-tabs v-model="activeTab" density="compact" class="plan-tabs">
          <v-tab value="mesures" prepend-icon="mdi-clipboard-list-outline">Mesures</v-tab>
          <v-tab value="avancement" prepend-icon="mdi-chart-bar">Avancement</v-tab>
        </v-tabs>

        <v-window v-model="activeTab" class="tab-content">
          <v-window-item value="mesures">
            <CrudListPage
              title="Mesures de plan"
              modelName="mesuredeplan"
              apiRouteName="mesurePlan"
              itemLabel="une mesure de plan"
              idField="id_mesure_plan"
              :columns="mesureColumns"
              :bgColor="'#64748b'"
              :geojsonMode="true"
              :showTitle="false"
              :showHeader="true"
              :showSearch="false"
              :showExportButtons="false"
              :showFilters="false"
              :viewOnly="props.mode === 'view'"
              :requestParams="{ plan_suivi: form.id_plan_suivi }"
              :addQueryParams="{ plan_suivi: form.id_plan_suivi }"
            />
          </v-window-item>

          <v-window-item value="avancement">
            <PlanAvancementView
              :plan-id="form.id_plan_suivi"
              :unite-pastorale-id="form.unite_pastorale"
              :view-only="props.mode === 'view'"
            />
          </v-window-item>
        </v-window>
      </section>
    </template>

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
import CrudListPage from "../../components/crud/CrudListPage.vue";
import PlanAvancementView from "./PlanAvancementView.vue";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" },
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("plandesuivi");

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
  id_plan_suivi: null,
  description: "",
  date_debut: "",
  date_fin: "",
  type_suivi: null,
  unite_pastorale: null,
});

const activeTab = ref("mesures");

const typesuivis = ref([]);
const ups = ref([]);

const mesureColumns = [
  { field: "description", label: "Description", sortable: true },
  { field: "type_mesure_detail.description", label: "Type", sortable: true },
  { field: "debut_periode", label: "Début", sortable: true },
  { field: "fin_periode", label: "Fin", sortable: true },
];

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
    .get(`${config.API_BASE_URL}/api/typeSuivi/`)
    .then(({ data }) => {
      typesuivis.value = data;
    })
    .catch(() => {});

  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/unitePastorale/light/`)
    .then(({ data }) => {
      ups.value = data;
    })
    .catch(() => {});
});

const rulesDateFin = computed(() => [
  (v) =>
    !v ||
    !form.date_debut ||
    v >= form.date_debut ||
    "La date de fin doit être postérieure à la date de début.",
]);

const isFormValid = computed(() => {
  const debut = form.date_debut;
  const fin = form.date_fin;
  return !fin || !debut || fin >= debut;
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
  margin-bottom: 1rem;
}
.layout-card:hover {
  border-color: #c8d0db;
  box-shadow: 0 2px 5px rgba(15, 23, 42, 0.08);
}
.mesures-card {
  min-height: 200px;
}
.plan-tabs {
  margin-bottom: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
}
.tab-content {
  min-height: 180px;
}
.plan-suivi-form :deep(.v-input--density-compact .v-field__input) {
  min-height: 38px;
  padding-top: 6px;
  padding-bottom: 6px;
}
.plan-suivi-form :deep(.v-label.v-field-label) {
  font-size: 0.82rem;
}
.plan-suivi-form :deep(.v-input) {
  font-size: 0.88rem;
}
.plan-suivi-form :deep(.v-field__input),
.plan-suivi-form :deep(.v-select__selection-text) {
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
</style>
