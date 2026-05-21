<template>
  <div class="plan-avancement">
    <div v-if="isLoading" class="w3-center" style="padding: 1.5rem">
      <img src="/spinner_2.gif" alt="Chargement" style="height: 32px" />
    </div>

    <div
      v-else-if="!mesures.length"
      class="w3-panel w3-pale-yellow"
      style="padding: 10px; margin: 0"
    >
      Aucune mesure pour ce plan.
    </div>

    <template v-else>
      <div v-if="!situations.length" class="w3-panel w3-pale-blue" style="padding: 10px; margin: 0">
        Aucune situation d'exploitation liée à cette unité pastorale.
      </div>

      <div v-else class="matrix-wrapper">
        <table class="avancement-table">
          <thead>
            <tr>
              <th class="col-mesure">Mesure</th>
              <th class="col-type">Type</th>
              <th
                v-for="situ in situations"
                :key="situ.id_situation"
                class="col-situ"
                :title="situ.nom_situation"
              >
                <div class="situ-header">
                  <span class="situ-annee">{{
                    situ.date_debut ? new Date(situ.date_debut).getFullYear() : ""
                  }}</span>
                  <span v-if="situ.exploitant_nom" class="situ-exploitant">
                    {{ situ.exploitant_nom }}
                  </span>
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="mesure in mesures" :key="mesure.id_mesure_plan" class="mesure-tr">
              <td class="col-mesure">
                <span class="mesure-desc">{{ mesure.description }}</span>
              </td>
              <td class="col-type">
                <span v-if="mesure.type_mesure_detail" class="type-chip">
                  {{ mesure.type_mesure_detail.description }}
                </span>
              </td>
              <td
                v-for="situ in situations"
                :key="situ.id_situation"
                class="col-situ cell-statut"
                :class="cellClass(mesure.id_mesure_plan, situ.id_situation)"
              >
                <v-menu v-if="!viewOnly" location="bottom center" :close-on-content-click="true">
                  <template #activator="{ props: menuProps }">
                    <button
                      v-bind="menuProps"
                      class="statut-btn"
                      :title="statutLabel(mesure.id_mesure_plan, situ.id_situation)"
                    >
                      <v-icon size="16">{{
                        statutIcon(mesure.id_mesure_plan, situ.id_situation)
                      }}</v-icon>
                    </button>
                  </template>
                  <v-list density="compact" class="statut-menu">
                    <v-list-item
                      v-for="opt in statutOptions"
                      :key="opt.value"
                      :prepend-icon="opt.icon"
                      :title="opt.label"
                      @click="setStatut(mesure.id_mesure_plan, situ.id_situation, opt.value)"
                    />
                  </v-list>
                </v-menu>
                <span
                  v-else
                  class="statut-badge"
                  :title="statutLabel(mesure.id_mesure_plan, situ.id_situation)"
                >
                  <v-icon size="16">{{
                    statutIcon(mesure.id_mesure_plan, situ.id_situation)
                  }}</v-icon>
                </span>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="legend">
          <span v-for="opt in statutOptions" :key="opt.value" class="legend-item">
            <v-icon size="14" :color="opt.iconColor">{{ opt.icon }}</v-icon>
            {{ opt.label }}
          </span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import config from "../../../config";
import auth from "@/services/axios";
import { useMainStore } from "../../store";

const props = defineProps({
  planId: { type: [Number, String], default: null },
  unitePastoraleId: { type: [Number, String], default: null },
  viewOnly: { type: Boolean, default: false },
});

const mainStore = useMainStore();

const isLoading = ref(false);
const mesures = ref([]);
const situations = ref([]);
// realisationsIndex[mesurePlanId][situationId] = realisationObj
const realisationsIndex = reactive({});
// savingKey[`${mesurePlanId}-${situationId}`] = true/false
const savingKey = reactive({});

const statutOptions = [
  {
    value: "non_realisee",
    label: "Non réalisée",
    icon: "mdi-circle-outline",
    iconColor: "#ef4444",
  },
  {
    value: "partielle",
    label: "Partiellement réalisée",
    icon: "mdi-circle-half-full",
    iconColor: "#f59e0b",
  },
  { value: "realisee", label: "Réalisée", icon: "mdi-check-circle", iconColor: "#22c55e" },
];

const getRealisation = (mesurePlanId, situationId) =>
  realisationsIndex[mesurePlanId]?.[situationId] ?? null;

const getStatut = (mesurePlanId, situationId) =>
  getRealisation(mesurePlanId, situationId)?.statut ?? null;

const statutLabel = (mesurePlanId, situationId) => {
  const statut = getStatut(mesurePlanId, situationId);
  return statutOptions.find((o) => o.value === statut)?.label ?? "Non renseignée";
};

const statutIcon = (mesurePlanId, situationId) => {
  const statut = getStatut(mesurePlanId, situationId);
  return statutOptions.find((o) => o.value === statut)?.icon ?? "mdi-minus-circle-outline";
};

const cellClass = (mesurePlanId, situationId) => {
  const statut = getStatut(mesurePlanId, situationId);
  if (!statut) return "statut-none";
  return `statut-${statut}`;
};

const setStatut = async (mesurePlanId, situationId, statut) => {
  const key = `${mesurePlanId}-${situationId}`;
  if (savingKey[key]) return;
  savingKey[key] = true;

  const existing = getRealisation(mesurePlanId, situationId);
  try {
    let resp;
    if (existing?.id_realisation_mesure) {
      resp = await auth.axiosInstance.put(
        `${config.API_BASE_URL}/api/realisationMesure/${existing.id_realisation_mesure}/`,
        {
          mesure_plan: mesurePlanId,
          situation: situationId,
          statut,
          commentaire: existing.commentaire ?? null,
        }
      );
    } else {
      resp = await auth.axiosInstance.post(`${config.API_BASE_URL}/api/realisationMesure/`, {
        mesure_plan: mesurePlanId,
        situation: situationId,
        statut,
      });
    }
    if (!realisationsIndex[mesurePlanId]) realisationsIndex[mesurePlanId] = {};
    realisationsIndex[mesurePlanId][situationId] = resp.data;
  } catch (e) {
    const msg = e?.response?.data?.detail || "Erreur lors de l'enregistrement.";
    mainStore.setErrorMessage(msg);
  } finally {
    savingKey[key] = false;
  }
};

const fetchAll = async () => {
  if (!props.planId) return;
  isLoading.value = true;
  try {
    const [mesuresRes, realisationsRes] = await Promise.all([
      auth.axiosInstance.get(`${config.API_BASE_URL}/api/mesurePlan/?plan_suivi=${props.planId}`),
      auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/realisationMesure/?plan_suivi=${props.planId}`
      ),
    ]);

    const features =
      mesuresRes.data?.features ?? (Array.isArray(mesuresRes.data) ? mesuresRes.data : []);
    mesures.value = features.map((f) =>
      f.properties ? { ...f.properties, id_mesure_plan: f.id ?? f.properties.id_mesure_plan } : f
    );

    const realisations = Array.isArray(realisationsRes.data)
      ? realisationsRes.data
      : (realisationsRes.data?.results ?? []);
    for (const r of realisations) {
      const mesurePlanId =
        typeof r.mesure_plan === "object" ? r.mesure_plan.id_mesure_plan : r.mesure_plan;
      const situationId = typeof r.situation === "object" ? r.situation.id_situation : r.situation;
      if (!realisationsIndex[mesurePlanId]) realisationsIndex[mesurePlanId] = {};
      realisationsIndex[mesurePlanId][situationId] = r;
    }

    if (props.unitePastoraleId) {
      const situRes = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/situationExploitation/?id_up=${props.unitePastoraleId}`
      );
      const raw = Array.isArray(situRes.data) ? situRes.data : (situRes.data?.results ?? []);
      situations.value = [...raw].sort((a, b) => {
        const ya = a.date_debut ? new Date(a.date_debut).getFullYear() : 0;
        const yb = b.date_debut ? new Date(b.date_debut).getFullYear() : 0;
        return ya - yb;
      });
    }
  } catch {
    mesures.value = [];
    situations.value = [];
  } finally {
    isLoading.value = false;
  }
};

onMounted(fetchAll);
defineExpose({ refresh: fetchAll });
</script>

<style scoped>
.plan-avancement {
  padding: 0.5rem 0;
}

.matrix-wrapper {
  overflow-x: auto;
}

.avancement-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.84rem;
  min-width: 400px;
}

.avancement-table thead tr {
  background: #f1f5f9;
  border-bottom: 2px solid #e2e8f0;
}

.avancement-table th {
  padding: 6px 10px;
  text-align: left;
  font-weight: 600;
  color: #475569;
  font-size: 0.8rem;
  white-space: nowrap;
}

.avancement-table td {
  padding: 5px 10px;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.mesure-tr:hover td {
  background: #f8fafc;
}

.col-mesure {
  min-width: 160px;
  max-width: 260px;
}

.col-type {
  min-width: 100px;
  max-width: 140px;
}

.col-situ {
  min-width: 80px;
  text-align: center;
}

.situ-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
}

.situ-annee {
  font-size: 0.85rem;
  font-weight: 700;
  color: #1e293b;
}

.situ-exploitant {
  font-size: 0.72rem;
  color: #64748b;
  font-weight: 400;
  max-width: 90px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mesure-desc {
  font-weight: 500;
  color: #1e293b;
}

.type-chip {
  display: inline-block;
  background: #f1f5f9;
  color: #475569;
  border-radius: 4px;
  padding: 1px 6px;
  font-size: 0.78rem;
}

.cell-statut {
  text-align: center;
}

.statut-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background 120ms;
}

.statut-btn:hover {
  background: rgba(0, 0, 0, 0.06);
}

.statut-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.statut-none .statut-btn,
.statut-none .statut-badge {
  color: #cbd5e1;
}

.statut-non_realisee .statut-btn,
.statut-non_realisee .statut-badge {
  color: #ef4444;
}

.statut-partielle .statut-btn,
.statut-partielle .statut-badge {
  color: #f59e0b;
}

.statut-realisee .statut-btn,
.statut-realisee .statut-badge {
  color: #22c55e;
}

.statut-menu {
  min-width: 200px;
}

.legend {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid #e2e8f0;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.78rem;
  color: #64748b;
}
</style>
