<template>
  <div class="plan-mesures-realisations">
    <div class="toolbar-actions">
      <v-btn
        v-if="!viewOnly && canAddPlan"
        color="primary"
        size="small"
        prepend-icon="mdi-plus"
        @click="goAddPlan"
        >Ajouter un plan</v-btn
      >
    </div>

    <div v-if="isLoading" class="w3-center" style="padding: 1rem">
      <img src="/spinner_2.gif" alt="Chargement" style="height: 32px" />
    </div>

    <div v-else-if="!plans.length" class="w3-panel w3-pale-blue" style="padding: 10px; margin: 0">
      Aucun suivi pour cette unité pastorale.
    </div>

    <v-expansion-panels v-else v-model="openedPanel" variant="accordion" class="plans-panels">
      <v-expansion-panel
        v-for="(plan, planIndex) in plans"
        :key="plan.id_plan_suivi"
        :value="planIndex"
        class="plan-panel"
      >
        <v-expansion-panel-title class="plan-title" @click="onPlanExpand(plan)">
          <div class="plan-header-content">
            <span class="plan-description">{{ plan.description }}</span>
            <span v-if="plan.type_suivi_detail" class="plan-type-chip">
              {{ plan.type_suivi_detail.description }}
            </span>
            <span class="plan-dates">
              {{ formatDate(plan.date_debut) }} → {{ formatDate(plan.date_fin) }}
            </span>
            <span class="plan-actions" @click.stop>
              <v-btn
                v-if="canEditPlan"
                icon="mdi-pencil"
                size="x-small"
                variant="text"
                color="primary"
                title="Modifier le plan"
                @click="goEditPlan(plan)"
              />
            </span>
          </div>
        </v-expansion-panel-title>

        <v-expansion-panel-text class="plan-body">
          <div v-if="mesuresLoading[plan.id_plan_suivi]" class="w3-center" style="padding: 0.5rem">
            <img src="/spinner_2.gif" alt="Chargement" style="height: 24px" />
          </div>

          <div
            v-else-if="!mesuresByPlan[plan.id_plan_suivi]?.length"
            class="w3-panel w3-pale-yellow"
            style="padding: 8px; margin: 4px 0; display: flex; align-items: center; gap: 12px"
          >
            <span style="font-size: 0.88rem">Aucune mesure pour ce plan.</span>
            <v-btn
              v-if="!viewOnly && canAddMesure"
              size="x-small"
              color="secondary"
              prepend-icon="mdi-plus"
              @click="goAddMesure(plan)"
              >Ajouter une mesure</v-btn
            >
          </div>

          <div v-else class="mesures-list">
            <div v-if="!viewOnly && canAddMesure" class="mesures-add-action">
              <v-btn
                size="x-small"
                color="secondary"
                prepend-icon="mdi-plus"
                @click="goAddMesure(plan)"
                >Ajouter une mesure</v-btn
              >
            </div>
            <div
              v-for="mesure in mesuresByPlan[plan.id_plan_suivi]"
              :key="mesure.id_mesure_plan"
              :ref="(el) => setMesureRowRef(mesure.id_mesure_plan, el)"
              class="mesure-row"
              :class="{ 'mesure-highlighted': mesure.id_mesure_plan === highlightedMesureId }"
            >
              <div class="mesure-info">
                <span class="mesure-description">{{ mesure.description }}</span>
                <span v-if="mesure.type_mesure_detail" class="mesure-type">
                  {{ mesure.type_mesure_detail.description }}
                </span>
                <span class="mesure-dates">
                  {{ formatDate(mesure.debut_periode) }} – {{ formatDate(mesure.fin_periode) }}
                </span>
                <v-btn
                  v-if="canEditMesure"
                  icon="mdi-pencil"
                  size="x-small"
                  variant="text"
                  color="primary"
                  title="Modifier la mesure"
                  @click="goEditMesure(mesure)"
                />
              </div>

              <div class="realisation-inline">
                <v-select
                  :model-value="getStatut(mesure.id_mesure_plan)"
                  :items="statutOptions"
                  item-title="label"
                  item-value="value"
                  :disabled="viewOnly"
                  density="compact"
                  variant="outlined"
                  hide-details
                  style="min-width: 180px; max-width: 200px"
                  :bg-color="statutColor(getStatut(mesure.id_mesure_plan))"
                  @update:model-value="(val) => onStatutChange(mesure.id_mesure_plan, val)"
                />
                <v-text-field
                  :model-value="getCommentaire(mesure.id_mesure_plan)"
                  :disabled="viewOnly"
                  label="Commentaire"
                  density="compact"
                  variant="outlined"
                  hide-details
                  style="min-width: 160px; flex: 1"
                  @update:model-value="(val) => onCommentaireChange(mesure.id_mesure_plan, val)"
                />
                <v-btn
                  v-if="!viewOnly"
                  color="success"
                  size="small"
                  icon="mdi-content-save"
                  :loading="savingIds.has(mesure.id_mesure_plan)"
                  @click="saveRealisation(mesure.id_mesure_plan)"
                />
              </div>
            </div>
          </div>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick } from "vue";
import { useRouter } from "vue-router";
import config from "../../../config";
import auth from "@/services/axios";
import { useMainStore } from "../../store";
import { usePermissions } from "../../composables/usePermissions";

const props = defineProps({
  unitePastoraleId: { type: [Number, String], default: null },
  situationId: { type: [Number, String], default: null },
  viewOnly: { type: Boolean, default: false },
});

const router = useRouter();
const mainStore = useMainStore();
const { can: canPlan } = usePermissions("plandesuivi");
const { can: canMesure } = usePermissions("mesuredeplan");

const canAddPlan = computed(() => canPlan("add"));
const canEditPlan = computed(() => canPlan("change"));
const canAddMesure = computed(() => canMesure("add"));
const canEditMesure = computed(() => canMesure("change"));

const goAddPlan = () => {
  router.push({ name: "plandesuivi-add", query: { unite_pastorale: props.unitePastoraleId } });
};

const goEditPlan = (plan) => {
  router.push({ name: "plandesuivi-edit", params: { id: plan.id_plan_suivi } });
};

const goAddMesure = (plan) => {
  router.push({ name: "mesuredeplan-add", query: { plan_suivi: plan.id_plan_suivi } });
};

const goEditMesure = (mesure) => {
  router.push({ name: "mesuredeplan-edit", params: { id: mesure.id_mesure_plan } });
};

const plans = ref([]);
const isLoading = ref(false);
const mesuresByPlan = reactive({});
const mesuresLoading = reactive({});
const realisationsMap = reactive({});
const pendingEdits = reactive({});
const savingIds = ref(new Set());
const openedPanel = ref(undefined);
const highlightedMesureId = ref(null);
const mesureRowRefs = {};

const setMesureRowRef = (id, el) => {
  if (el) mesureRowRefs[id] = el;
  else delete mesureRowRefs[id];
};

const statutOptions = [
  { label: "Non réalisée", value: "non_realisee" },
  { label: "Partiellement réalisée", value: "partielle" },
  { label: "Réalisée", value: "realisee" },
];

const statutColor = (statut) => {
  if (statut === "realisee") return "#dcfce7";
  if (statut === "partielle") return "#fef9c3";
  return "#fee2e2";
};

const formatDate = (d) => {
  if (!d) return "—";
  const date = new Date(d);
  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
};

const getStatut = (mesurePlanId) =>
  pendingEdits[mesurePlanId]?.statut ?? realisationsMap[mesurePlanId]?.statut ?? "non_realisee";

const getCommentaire = (mesurePlanId) =>
  pendingEdits[mesurePlanId]?.commentaire ?? realisationsMap[mesurePlanId]?.commentaire ?? "";

const onStatutChange = (mesurePlanId, val) => {
  if (!pendingEdits[mesurePlanId]) pendingEdits[mesurePlanId] = {};
  pendingEdits[mesurePlanId].statut = val;
};

const onCommentaireChange = (mesurePlanId, val) => {
  if (!pendingEdits[mesurePlanId]) pendingEdits[mesurePlanId] = {};
  pendingEdits[mesurePlanId].commentaire = val;
};

let fetchPlansPromise = null;

const fetchPlans = () => {
  if (!props.unitePastoraleId) return Promise.resolve();
  if (fetchPlansPromise) return fetchPlansPromise;
  if (plans.value.length) return Promise.resolve();
  isLoading.value = true;
  fetchPlansPromise = auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/planSuivi/?unite_pastorale=${props.unitePastoraleId}`)
    .then(({ data }) => {
      plans.value = Array.isArray(data) ? data : (data.results ?? []);
    })
    .catch(() => {
      plans.value = [];
    })
    .finally(() => {
      isLoading.value = false;
      fetchPlansPromise = null;
    });
  return fetchPlansPromise;
};

const fetchMesuresForPlan = async (planId) => {
  if (mesuresByPlan[planId] !== undefined) return;
  mesuresLoading[planId] = true;
  try {
    const { data } = await auth.axiosInstance.get(
      `${config.API_BASE_URL}/api/mesurePlan/?plan_suivi=${planId}`
    );
    const features = data?.features ?? (Array.isArray(data) ? data : []);
    mesuresByPlan[planId] = features.map((f) =>
      f.properties ? { ...f.properties, id_mesure_plan: f.id ?? f.properties.id_mesure_plan } : f
    );
  } catch {
    mesuresByPlan[planId] = [];
  } finally {
    mesuresLoading[planId] = false;
  }
};

const fetchRealisationsForSituation = async () => {
  if (!props.situationId) return;
  try {
    const { data } = await auth.axiosInstance.get(
      `${config.API_BASE_URL}/api/realisationMesure/?situation=${props.situationId}`
    );
    const items = Array.isArray(data) ? data : (data.results ?? []);
    for (const r of items) {
      const mesurePlanId =
        typeof r.mesure_plan === "object" ? r.mesure_plan.id_mesure_plan : r.mesure_plan;
      realisationsMap[mesurePlanId] = r;
    }
  } catch {}
};

const onPlanExpand = async (plan) => {
  await fetchMesuresForPlan(plan.id_plan_suivi);
  await fetchRealisationsForSituation();
};

const saveRealisation = async (mesurePlanId) => {
  if (!props.situationId) return;

  const existing = realisationsMap[mesurePlanId];
  const edit = pendingEdits[mesurePlanId] ?? {};
  const statut = edit.statut ?? existing?.statut ?? "non_realisee";
  const commentaire = edit.commentaire ?? existing?.commentaire ?? null;

  savingIds.value = new Set([...savingIds.value, mesurePlanId]);
  try {
    let resp;
    if (existing?.id_realisation_mesure) {
      resp = await auth.axiosInstance.put(
        `${config.API_BASE_URL}/api/realisationMesure/${existing.id_realisation_mesure}/`,
        { mesure_plan: mesurePlanId, situation: props.situationId, statut, commentaire }
      );
    } else {
      resp = await auth.axiosInstance.post(`${config.API_BASE_URL}/api/realisationMesure/`, {
        mesure_plan: mesurePlanId,
        situation: props.situationId,
        statut,
        commentaire,
      });
    }
    realisationsMap[mesurePlanId] = resp.data;
    delete pendingEdits[mesurePlanId];
    mainStore.setSuccessMessage("Réalisation enregistrée.");
  } catch (e) {
    const msg = e?.response?.data?.detail || "Erreur lors de l'enregistrement.";
    mainStore.setErrorMessage(msg);
  } finally {
    savingIds.value = new Set([...savingIds.value].filter((id) => id !== mesurePlanId));
  }
};

const highlightMesure = async (mesureId) => {
  // Attendre que les plans soient chargés (fetchPlans peut être en cours)
  await fetchPlans();

  // Charger les mesures de tous les plans si nécessaire pour trouver le bon
  for (const plan of plans.value) {
    if (mesuresByPlan[plan.id_plan_suivi] === undefined) {
      await fetchMesuresForPlan(plan.id_plan_suivi);
    }
  }
  await fetchRealisationsForSituation();

  // Trouver le plan qui contient cette mesure
  let planIndex = -1;
  let targetPlan = null;
  for (let i = 0; i < plans.value.length; i++) {
    const plan = plans.value[i];
    const mesures = mesuresByPlan[plan.id_plan_suivi] ?? [];
    if (mesures.find((m) => m.id_mesure_plan === mesureId)) {
      planIndex = i;
      targetPlan = plan;
      break;
    }
  }

  if (planIndex === -1 || !targetPlan) return;

  // Ouvrir le panel et attendre que Vuetify anime + rende le contenu
  openedPanel.value = planIndex;
  await nextTick();
  await new Promise((resolve) => setTimeout(resolve, 320));

  highlightedMesureId.value = mesureId;
  await nextTick();

  // Scroller jusqu'à la ligne
  const el = mesureRowRefs[mesureId];
  if (el) el.scrollIntoView({ behavior: "smooth", block: "nearest" });

  // Effacer le highlight après 2.5s
  setTimeout(() => {
    if (highlightedMesureId.value === mesureId) highlightedMesureId.value = null;
  }, 2500);
};

defineExpose({ fetchPlans, highlightMesure });

fetchPlans();
</script>

<style scoped>
.plan-mesures-realisations {
  padding: 0.25rem 0;
}

.toolbar-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 0.5rem;
}

.plans-panels {
  border-radius: 6px;
  overflow: hidden;
}

.plan-panel {
  border: 1px solid #e2e8f0;
  margin-bottom: 4px;
  border-radius: 6px !important;
  overflow: hidden;
}

.plan-title {
  font-size: 0.88rem;
  min-height: 40px !important;
  padding: 4px 12px;
}

.plan-header-content {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  width: 100%;
}

.plan-description {
  font-weight: 600;
  color: #1e293b;
}

.plan-type-chip {
  background: #e0f2fe;
  color: #0369a1;
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 0.78rem;
  font-weight: 500;
}

.plan-dates {
  color: #64748b;
  font-size: 0.8rem;
}

.plan-actions {
  display: flex;
  align-items: center;
  gap: 2px;
  margin-left: auto;
}

.mesures-add-action {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 4px;
}

.plan-body {
  padding: 0 !important;
}

.plan-body :deep(.v-expansion-panel-text__wrapper) {
  padding: 0.5rem 0.75rem;
}

.mesures-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.mesure-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 6px 8px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: #f8fafc;
  transition:
    background 300ms,
    border-color 300ms;
}

.mesure-highlighted {
  background: #ede9fe;
  border-color: #7c3aed;
  border-left-width: 3px;
}

.mesure-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.mesure-description {
  font-weight: 500;
  font-size: 0.85rem;
  color: #1e293b;
}

.mesure-type {
  font-size: 0.78rem;
  color: #64748b;
  background: #f1f5f9;
  border-radius: 4px;
  padding: 1px 6px;
}

.mesure-dates {
  font-size: 0.78rem;
  color: #94a3b8;
  margin-left: auto;
}

.realisation-inline {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
</style>
