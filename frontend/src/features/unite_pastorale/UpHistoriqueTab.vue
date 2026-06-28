<template>
  <div class="historique-tab">
    <div v-if="isLoading" class="histo-loading">
      <v-progress-circular indeterminate color="primary" size="28" />
    </div>

    <div v-else-if="entries.length === 0" class="histo-empty">Aucun historique disponible.</div>

    <v-expansion-panels v-else variant="accordion" class="histo-panels">
      <v-expansion-panel v-for="(entry, i) in entries" :key="i">
        <v-expansion-panel-title class="histo-panel-title">
          <span class="histo-date">{{ formatDate(entry.timestamp) }}</span>
          <span class="histo-actor">{{ entry.actor ?? "—" }}</span>
          <v-chip
            v-if="entry.model === 'geometrieunitepastorale'"
            color="purple-lighten-2"
            size="x-small"
            label
            class="histo-chip"
            >Géométrie</v-chip
          >
          <v-chip
            v-else-if="entry.model === 'proprietaireunitepastorale'"
            color="orange-lighten-1"
            size="x-small"
            label
            class="histo-chip"
            >Propriétaire</v-chip
          >
          <v-chip
            :color="ACTION_COLORS[entry.action] ?? 'grey'"
            size="x-small"
            label
            class="histo-chip"
          >
            {{ entry.action }}
          </v-chip>
          <span v-if="changesCount(entry.changes) > 0" class="histo-count">
            {{ changesCount(entry.changes) }} champ{{ changesCount(entry.changes) > 1 ? "s" : "" }}
          </span>
        </v-expansion-panel-title>

        <v-expansion-panel-text class="histo-panel-text">
          <div v-if="changesCount(entry.changes) === 0" class="diff-empty">
            Aucun détail disponible.
          </div>
          <template v-else-if="entry.action === 'Création' || entry.action === 'Suppression'">
            <table class="histo-diff-table">
              <tbody>
                <tr v-for="(vals, field) in entry.changes" :key="field">
                  <td class="diff-field">{{ fieldLabel(field, entry.model) }}</td>
                  <td class="diff-value">
                    {{ display(entry.action === "Création" ? vals[1] : vals[0]) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </template>
          <template v-else>
            <table class="histo-diff-table">
              <thead>
                <tr>
                  <th>Champ</th>
                  <th>Avant</th>
                  <th></th>
                  <th>Après</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(vals, field) in entry.changes" :key="field">
                  <td class="diff-field">{{ fieldLabel(field, entry.model) }}</td>
                  <td class="diff-old">{{ display(vals[0]) }}</td>
                  <td class="diff-arrow"><v-icon size="12">mdi-arrow-right</v-icon></td>
                  <td class="diff-new">{{ display(vals[1]) }}</td>
                </tr>
              </tbody>
            </table>
          </template>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import auth from "@/services/axios";
import config from "@/../config";

const props = defineProps({
  upId: { type: [Number, String], default: null },
});

const FIELD_LABELS = {
  unitepastorale: {
    code_up: "Code UP",
    nom_up: "Nom UP",
    secteur: "Secteur",
    active: "Actif",
  },
  geometrieunitepastorale: {
    date_debut_validite: "Début de validité",
    date_fin_validite: "Fin de validité",
    geom: "Géométrie",
  },
  proprietaireunitepastorale: {
    proprietaire: "Propriétaire foncier",
  },
};

const ACTION_COLORS = {
  Création: "success",
  Modification: "info",
  Suppression: "error",
};

const entries = ref([]);
const isLoading = ref(false);

const fieldLabel = (field, model) => FIELD_LABELS[model]?.[field] ?? field;

const changesCount = (changes) => Object.keys(changes ?? {}).length;

const display = (val) => {
  if (val === null || val === undefined) return "—";
  const s = String(val);
  return s.length > 100 ? s.slice(0, 97) + "…" : s;
};

const formatDate = (iso) => {
  if (!iso) return "";
  return new Date(iso).toLocaleString("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const fetchHistorique = async () => {
  if (!props.upId) return;
  isLoading.value = true;
  try {
    const resp = await auth.axiosInstance.get(
      `${config.API_BASE_URL}/api/unitePastorale/${props.upId}/historique/`
    );
    entries.value = resp.data ?? [];
  } catch {
    entries.value = [];
  } finally {
    isLoading.value = false;
  }
};

watch(() => props.upId, fetchHistorique, { immediate: true });
</script>

<style scoped>
.historique-tab {
  padding: 0.25rem 0;
}
.histo-loading,
.histo-empty {
  display: flex;
  justify-content: center;
  padding: 2rem;
  color: #64748b;
  font-size: 0.88rem;
}
.histo-panels {
  border-radius: 6px;
  overflow: hidden;
}
.histo-panel-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.82rem;
  min-height: 36px !important;
}
.histo-date {
  white-space: nowrap;
  color: #475569;
  min-width: 120px;
}
.histo-actor {
  min-width: 80px;
  font-weight: 500;
}
.histo-chip {
  flex-shrink: 0;
}
.histo-count {
  color: #94a3b8;
  font-size: 0.78rem;
}
.histo-panel-text :deep(.v-expansion-panel-text__wrapper) {
  padding: 4px 12px 10px;
}
.diff-empty {
  font-size: 0.8rem;
  color: #94a3b8;
  font-style: italic;
}
.histo-diff-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
}
.histo-diff-table th {
  text-align: left;
  color: #94a3b8;
  font-weight: 500;
  padding: 2px 8px 4px 0;
}
.histo-diff-table td {
  padding: 2px 8px 2px 0;
  vertical-align: middle;
}
.diff-field {
  font-weight: 600;
  color: #334155;
  min-width: 130px;
}
.diff-old {
  color: #b91c1c;
  text-decoration: line-through;
}
.diff-new {
  color: #15803d;
}
.diff-arrow {
  color: #cbd5e1;
  width: 20px;
}
.diff-value {
  color: #334155;
}
</style>
