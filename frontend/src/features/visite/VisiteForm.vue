<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <v-form ref="formRef" class="visite-form" @submit.prevent="handleSubmitClick">
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
            class="required"
            label="Date de visite"
            density="compact"
            variant="underlined"
            hide-details="auto"
            :rules="props.mode !== 'view' ? [required] : []"
          />
        </div>
        <div class="w3-half form-cell">
          <v-select
            v-model="form.contact_alpagiste_ids"
            :items="alpagistes"
            item-value="id_eleveur"
            item-title="full_name"
            :disabled="props.mode === 'view'"
            label="Contacts alpagistes"
            density="compact"
            variant="underlined"
            hide-details
            multiple
            chips
            closable-chips
            clearable
            :menu-props="{ maxHeight: '300px' }"
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
          class="required"
          label="Observateurs PNV"
          density="compact"
          variant="underlined"
          hide-details="auto"
          :rules="props.mode !== 'view' ? [rulesObservateurs] : []"
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
          class="required"
          label="Description"
          density="compact"
          variant="underlined"
          hide-details="auto"
          :rules="props.mode !== 'view' ? [required, maxLen(150)] : []"
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
        :disabled="formRef?.isValid === false"
        >{{ btTitle }}</v-btn
      >
    </div>
  </v-form>

  <v-dialog v-model="confirmDialog" max-width="420" persistent>
    <v-card>
      <v-card-title class="text-h6">Aucun contact alpagiste</v-card-title>
      <v-card-text>
        Aucun contact alpagiste n'a été renseigné. Voulez-vous continuer sans contact alpagiste ?
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="confirmDialog = false">Annuler</v-btn>
        <v-btn color="success" variant="flat" @click="confirmAndSubmit">Continuer</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { reactive, ref, computed, onMounted, watch } from "vue";
import config from "../../../config";
import auth from "@/services/axios";
import { maxLen, required } from "@/utils/validators";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" },
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const formRef = ref(null);

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
  contact_alpagiste_ids: [],
  observateur_ids: [],
});

const alpagistes = ref([]);
const users = ref([]);
const upNom = ref("");
const confirmDialog = ref(false);

const rulesObservateurs = (v) =>
  (Array.isArray(v) && v.length > 0) || "Au moins un observateur PNV est requis.";

watch(
  () => props.initialForm,
  (val) => {
    if (!val) return;
    form.date_visite = val.date_visite ?? "";
    form.description = val.description ?? "";
    form.commentaire = val.commentaire ?? "";
    form.unite_pastorale = val.unite_pastorale ?? null;
    form.contact_alpagiste_ids = Array.isArray(val.contacts_alpagistes)
      ? val.contacts_alpagistes.map((e) => e.id)
      : Array.isArray(val.contact_alpagiste_ids)
        ? val.contact_alpagiste_ids
        : [];
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

const buildPayload = () => ({
  date_visite: form.date_visite || null,
  description: form.description,
  commentaire: form.commentaire || null,
  unite_pastorale: form.unite_pastorale,
  contact_alpagiste_ids: form.contact_alpagiste_ids,
  observateur_ids: form.observateur_ids,
});

const handleSubmitClick = async () => {
  const { valid } = await formRef.value.validate();
  if (!valid) return;
  if (!form.contact_alpagiste_ids.length) {
    confirmDialog.value = true;
    return;
  }
  props.onSubmit?.(buildPayload());
};

const confirmAndSubmit = () => {
  confirmDialog.value = false;
  props.onSubmit?.(buildPayload());
};

const closeModal = () => props.onClose?.();
</script>
