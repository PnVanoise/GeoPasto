<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <form class="abri-urgence-commodite-form" @submit.prevent="submitForm">
    <section class="layout-card">
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-select
            id="abri"
            v-model="form.abri_urgence"
            :disabled="true"
            :items="abris"
            item-title="description"
            item-value="id_abri_urgence"
            label="Abri d'urgence"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
        <div class="w3-half form-cell">
          <v-select
            id="commodite"
            v-model="form.commodite"
            :disabled="props.mode === 'view' || !can('change')"
            :items="commodites"
            item-title="description"
            item-value="id_commodite"
            label="Commodité"
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
            type="text"
            label="Etat de la commodité"
            v-model="form.etat"
            :disabled="props.mode === 'view' || !can('change')"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
        <div class="w3-half form-cell">
          <v-text-field
            type="number"
            label="Quantité"
            v-model.number="form.quantite"
            :disabled="props.mode === 'view' || !can('change')"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
      </div>
      <div class="w3-row form-ligne">
        <div class="form-cell">
          <v-text-field
            type="text"
            label="Commentaire"
            v-model="form.commentaire"
            :disabled="props.mode === 'view' || !can('change')"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
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
import { reactive, watch, ref, computed, onMounted } from "vue";
import config from "../../../config";
import auth from "@/services/axios";
import { usePermissions } from "../../composables/usePermissions";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" }, // add | change | view
  itemLabel: { type: String, default: "une commodité d'abri" },
  abriId: { type: [String, Number], default: null },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("abridurgencecommodite");

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

const abris = ref([]);
const commodites = ref([]);

const form = reactive({
  abri_urgence: null,
  commodite: null,
  etat: "",
  quantite: null,
  commentaire: "",
});
watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) {
      Object.assign(form, newVal);
    }
  },
  { immediate: true, deep: true }
);

watch(
  () => props.abriId,
  (newVal) => {
    if (newVal != null) {
      form.abri_urgence = newVal;
    }
  },
  { immediate: true }
);

onMounted(() => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/abriDUrgence/`)
    .then((response) => {
      abris.value = response.data;
    })
    .catch(() => {});

  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/commodite/`)
    .then((response) => {
      commodites.value = response.data;
    })
    .catch(() => {});
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
}
.layout-card:hover {
  border-color: #c8d0db;
  box-shadow: 0 2px 5px rgba(15, 23, 42, 0.08);
}

.form-ligne {
  padding: 4px;
}
.form-cell {
  padding: 4px;
}

.abri-urgence-commodite-form :deep(.v-input--density-compact .v-field__input) {
  min-height: 38px;
  padding-top: 6px;
  padding-bottom: 6px;
}
.abri-urgence-commodite-form :deep(.v-label.v-field-label) {
  font-size: 0.82rem;
}
.abri-urgence-commodite-form :deep(.v-input) {
  font-size: 0.88rem;
}
.abri-urgence-commodite-form :deep(.v-field__input),
.abri-urgence-commodite-form :deep(.v-select__selection-text) {
  font-size: 0.88rem;
}

.form-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
}
</style>
