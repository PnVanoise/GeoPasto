<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <form class="visite-form" @submit.prevent="submitForm">
    <section class="layout-card">
      <div class="form-cell">
        <v-text-field
          :model-value="upNom"
          label="Unité pastorale"
          density="compact"
          variant="underlined"
          hide-details
          disabled
        />
      </div>
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-text-field
            type="date"
            v-model="form.date_visite"
            :disabled="props.mode === 'view'"
            label="Date de visite"
            density="compact"
            variant="underlined"
            hide-details
          />
        </div>
        <div class="w3-half form-cell">
          <v-select
            v-model="form.contact_alpagiste"
            :items="alpagistes"
            item-value="id_eleveur"
            item-title="full_name"
            :disabled="props.mode === 'view'"
            label="Contact alpagiste"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
      </div>
      <div class="form-cell">
        <v-select
          v-model="form.observateur_ids"
          :items="users"
          item-value="id"
          item-title="full_name"
          :disabled="props.mode === 'view'"
          label="Observateurs PNV"
          density="compact"
          variant="underlined"
          hide-details
          multiple
          chips
          closable-chips
          :menu-props="{ maxHeight: '300px' }"
        />
      </div>
      <div class="form-cell">
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
      <div class="form-cell">
        <v-textarea
          v-model="form.commentaire"
          :disabled="props.mode === 'view'"
          label="Commentaire"
          density="compact"
          variant="underlined"
          hide-details
          rows="2"
          auto-grow
          clearable
        />
      </div>
    </section>

    <div class="form-actions">
      <v-btn color="info" @click="closeModal" prepend-icon="mdi-arrow-left-circle">Retour</v-btn>
      <v-btn
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
import { reactive, ref, computed, onMounted, watch } from "vue";
import config from "../../../config";
import auth from "@/services/axios";
import { maxLen } from "@/utils/validators";

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
  return `Détail — ${props.itemLabel}`;
});

const btTitle = computed(() => (props.mode === "add" ? "Ajouter" : "Enregistrer"));

const form = reactive({
  date_visite: "",
  description: "",
  commentaire: "",
  unite_pastorale: null,
  contact_alpagiste: null,
  observateur_ids: [],
});

const alpagistes = ref([]);
const users = ref([]);
const upNom = ref("");

watch(
  () => props.initialForm,
  (val) => {
    if (!val) return;
    form.date_visite = val.date_visite ?? "";
    form.description = val.description ?? "";
    form.commentaire = val.commentaire ?? "";
    form.unite_pastorale = val.unite_pastorale ?? null;
    form.contact_alpagiste = val.contact_alpagiste ?? null;
    form.observateur_ids = Array.isArray(val.observateurs)
      ? val.observateurs.map((o) => o.id)
      : Array.isArray(val.observateur_ids)
        ? val.observateur_ids
        : [];
    if (val.unite_pastorale_nom) upNom.value = val.unite_pastorale_nom;
  },
  { immediate: true }
);

watch(
  () => form.unite_pastorale,
  (upId) => {
    if (!upId || upNom.value) return;
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/unitePastorale/light/`)
      .then(({ data }) => {
        const up = (
          Array.isArray(data) ? data : (data.features?.map((f) => f.properties) ?? [])
        ).find((u) => u.id_unite_pastorale === upId);
        if (up) upNom.value = up.nom_up;
      })
      .catch(() => {});
  },
  { immediate: true }
);

watch(
  () => form.unite_pastorale,
  (upId) => {
    if (!upId) return;
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/eleveur/by-unite-pastorale/${upId}/`)
      .then(({ data }) => {
        alpagistes.value = data.map((e) => ({
          ...e,
          full_name: `${e.nom_eleveur ?? ""} ${e.prenom_eleveur ?? ""}`.trim(),
        }));
      })
      .catch(() => {});
  },
  { immediate: true }
);

onMounted(() => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/users/`)
    .then(({ data }) => {
      users.value = data;
    })
    .catch(() => {});
});

const submitForm = () => {
  props.onSubmit?.({
    date_visite: form.date_visite || null,
    description: form.description,
    commentaire: form.commentaire || null,
    unite_pastorale: form.unite_pastorale,
    contact_alpagiste: form.contact_alpagiste || null,
    observateur_ids: form.observateur_ids,
  });
};

const closeModal = () => props.onClose?.();
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
.visite-form :deep(.v-input--density-compact .v-field__input) {
  min-height: 38px;
  padding-top: 6px;
  padding-bottom: 6px;
}
.visite-form :deep(.v-label.v-field-label) {
  font-size: 0.82rem;
}
.visite-form :deep(.v-input) {
  font-size: 0.88rem;
}
.visite-form :deep(.v-field__input),
.visite-form :deep(.v-select__selection-text) {
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
