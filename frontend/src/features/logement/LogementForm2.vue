<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <form class="logement-form" @submit.prevent="submitForm">
    <div class="logement-layout">
      <section class="layout-card tabs-card">
        <v-tabs v-model="activeTab" color="primary" density="compact" class="mb-2">
          <v-tab value="tab1">Identification</v-tab>
          <v-tab value="tab2">Hébergement</v-tab>
          <v-tab value="tab3">Eau &amp; équipements</v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <v-window-item value="tab1">
            <div class="fields-grid">
              <v-text-field
                v-model="form.logement_code"
                label="Code logement"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                required
              />
              <v-text-field
                v-model="form.nom_logement"
                label="Nom"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
              />
              <v-select
                v-model="form.unite_pastorale"
                :items="ups"
                item-title="nom_up"
                item-value="id_unite_pastorale"
                label="Unité pastorale"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
              <v-select
                v-model="form.statut"
                :items="choices.statut"
                item-title="display"
                item-value="value"
                label="Statut"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
              <v-select
                v-model="form.acces_final"
                :items="choices.acces_final"
                item-title="display"
                item-value="value"
                label="Accès final"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
              <v-select
                v-model="form.propriete"
                :items="choices.propriete"
                item-title="display"
                item-value="value"
                label="Propriété"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
              <v-select
                v-model="form.type_logement"
                :items="choices.type_logement"
                item-title="display"
                item-value="value"
                label="Type de logement"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
              <v-select
                v-model="form.multiusage"
                :items="choices.multiusage"
                item-title="display"
                item-value="value"
                label="Multiusage"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
              <v-select
                v-model="form.activite_laitiere"
                :items="choices.activite_laitiere"
                item-title="display"
                item-value="value"
                label="Activité laitière"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
              <v-select
                v-model="form.etat_batiment"
                :items="choices.etat_batiment"
                item-title="display"
                item-value="value"
                label="État structurel du bâtiment"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
            </div>
          </v-window-item>

          <v-window-item value="tab2">
            <div class="fields-grid">
              <v-select
                v-model="form.accueil_public"
                :items="choices.accueil_public"
                item-title="display"
                item-value="value"
                label="Accueil public"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
              <v-select
                v-model="form.mixite_possible"
                :items="choices.mixite_possible"
                item-title="display"
                item-value="value"
                label="Mixité possible"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
              <v-select
                v-model="form.surface_logement"
                :items="choices.surface_logement"
                item-title="display"
                item-value="value"
                label="Surface logement"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
              <v-select
                v-model="form.presence_douche"
                :items="choices.presence_douche"
                item-title="display"
                item-value="value"
                label="Douche"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
              <v-select
                v-model="form.type_wc"
                :items="choices.type_wc"
                item-title="display"
                item-value="value"
                label="WC"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
              <v-select
                v-model="form.alim_elec"
                :items="choices.alim_elec"
                item-title="display"
                item-value="value"
                label="Alimentation électrique"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
              <v-select
                v-model="form.alim_eau"
                :items="choices.alim_eau"
                item-title="display"
                item-value="value"
                label="Alimentation en eau"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
              <v-select
                v-model="form.origine_eau"
                :items="choices.origine_eau"
                item-title="display"
                item-value="value"
                label="Origine eau"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
            </div>
          </v-window-item>

          <v-window-item value="tab3">
            <div class="fields-grid">
              <v-select
                v-model="form.qualite_eau"
                :items="choices.qualite_eau"
                item-title="display"
                item-value="value"
                label="Qualité eau"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
              <v-select
                v-model="form.dispo_eau"
                :items="choices.dispo_eau"
                item-title="display"
                item-value="value"
                label="Disponibilité eau"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
              <v-select
                v-model="form.assainissement"
                :items="choices.assainissement"
                item-title="display"
                item-value="value"
                label="Assainissement"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
              <v-select
                v-model="form.chauffe_eau"
                :items="choices.chauffe_eau"
                item-title="display"
                item-value="value"
                label="Chauffe-eau"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
              <v-select
                v-model="form.chauffage"
                :items="choices.chauffage"
                item-title="display"
                item-value="value"
                label="Chauffage"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
              <v-select
                v-model="form.stockage_indep"
                :items="choices.stockage_indep"
                item-title="display"
                item-value="value"
                label="Stockage indépendant"
                :menu-props="selectMenuProps"
                :disabled="props.mode === 'view'"
                density="compact"
                variant="underlined"
                hide-details
                clearable
              />
            </div>
          </v-window-item>
        </v-window>
      </section>

      <section class="layout-card map-card">
        <h4 class="map-title">Position du logement</h4>
        <div class="geometry-status" :class="hasGeometry ? 'is-set' : 'is-missing'">
          {{ hasGeometry ? "Position définie" : "Position non définie" }}
        </div>
        <QuartierGeometryEditorOl
          v-model="form.geometry"
          geometryType="Point"
          :disabled="props.mode === 'view'"
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
      >
        {{ btTitle }}
      </v-btn>
    </div>
  </form>
</template>

<script setup>
import { computed, reactive, ref, watch, onMounted } from "vue";
import config from "../../../config";
import auth from "@/services/axios";
import QuartierGeometryEditorOl from "../../components/map/QuartierGeometryEditorOl.vue";
import { selectMenuProps } from "../../composables/useSelectMenuProps";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" },
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const formTitle = computed(() => {
  if (props.mode === "add") return `Ajouter ${props.itemLabel}`;
  if (props.mode === "change") return `Modifier ${props.itemLabel}`;
  return `Voir les détails d'${props.itemLabel}`;
});
const btTitle = computed(() => (props.mode === "add" ? "Ajouter" : "Enregistrer"));
const hasGeometry = computed(() => {
  const g = form.geometry;
  return g?.type === "Point" && Array.isArray(g.coordinates) && g.coordinates.length >= 2;
});

const activeTab = ref("tab1");
const choices = ref({});
const ups = ref([]);

const CHOICE_FIELDS = [
  "statut",
  "acces_final",
  "propriete",
  "type_logement",
  "multiusage",
  "activite_laitiere",
  "etat_batiment",
  "accueil_public",
  "mixite_possible",
  "surface_logement",
  "presence_douche",
  "type_wc",
  "alim_elec",
  "alim_eau",
  "origine_eau",
  "qualite_eau",
  "dispo_eau",
  "assainissement",
  "chauffe_eau",
  "chauffage",
  "stockage_indep",
];

const form = reactive({
  logement_code: "",
  nom_logement: "",
  unite_pastorale: null,
  ...Object.fromEntries(CHOICE_FIELDS.map((f) => [f, null])),
  geometry: null,
});

watch(
  () => props.initialForm,
  (newVal) => {
    const base = newVal || {};
    const src = base.properties ? { ...base.properties } : base;
    form.logement_code = src.logement_code ?? "";
    form.nom_logement = src.nom_logement ?? "";
    form.unite_pastorale = src.unite_pastorale ?? null;
    for (const f of CHOICE_FIELDS) {
      form[f] = src[f] ?? null;
    }
    form.geometry = base.geometry ?? src.geometry ?? null;
  },
  { deep: true, immediate: true }
);

const submitForm = () => {};

const closeModal = () => props.onClose?.();

onMounted(async () => {
  try {
    const [resChoices, resUP] = await Promise.all([
      auth.axiosInstance.get(`${config.API_BASE_URL}/choices_logement/`),
      auth.axiosInstance.get(`${config.API_BASE_URL}/api/unitePastorale/light/`),
    ]);
    choices.value = resChoices.data ?? {};
    ups.value = resUP.data ?? [];
  } catch (err) {}
});
</script>

<style scoped>
.logement-layout {
  display: grid;
  grid-template-columns: 1fr minmax(300px, 480px);
  gap: 16px;
  align-items: start;
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

.logement-form :deep(.v-input--density-compact .v-field__input) {
  min-height: 38px;
  padding-top: 6px;
  padding-bottom: 6px;
}
.logement-form :deep(.v-label.v-field-label) {
  font-size: 0.82rem;
}
.logement-form :deep(.v-input) {
  font-size: 0.88rem;
}
.logement-form :deep(.v-field__input),
.logement-form :deep(.v-select__selection-text) {
  font-size: 0.88rem;
}

.fields-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  padding: 8px 0;
}

.map-title {
  margin: 0 0 10px;
  font-size: 1rem;
  font-weight: 600;
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

.form-actions {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1.2rem;
}

@media (max-width: 900px) {
  .logement-layout {
    grid-template-columns: 1fr;
  }
  .fields-grid {
    grid-template-columns: 1fr;
  }
}
</style>
