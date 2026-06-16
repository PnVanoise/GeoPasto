<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>

  <form class="subvention-form" @submit.prevent="submitForm">
    <section class="layout-card">
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-textarea
            v-model="form.commentaire"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Commentaire"
            dense
            variant="underlined"
            hide-details
            rows="2"
            auto-grow
            clearable
          />
        </div>
        <div class="w3-half form-cell">
          <v-text-field
            id="montant"
            v-model="form.montant"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Montant"
            dense
            variant="underlined"
            hide-details
            clearable
          />
        </div>
      </div>
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-switch
            id="engage"
            v-model="form.engage"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Engagé ?"
            color="primary"
            dense
            hide-details
          />
        </div>
        <div class="w3-half form-cell">
          <v-switch
            id="paye"
            v-model="form.paye"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Payé ?"
            color="primary"
            dense
            hide-details
          />
        </div>
      </div>
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-select
            id="exploitant"
            v-model="form.exploitant"
            :items="exploitants"
            item-title="nom_exploitant"
            item-value="id_exploitant"
            :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
            label="Alpagiste"
            dense
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

const { can } = usePermissions("subventionpnv");

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
  commentaire: "",
  montant: "",
  engage: false,
  paye: false,
  exploitant: null,
});

const exploitants = ref([]);

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
  // Récupère les exploitants
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/exploitant/`)
    .then((res) => {
      exploitants.value = res.data;
    })
    .catch((error) => {});
});

// Submit
const submitForm = () => {
  if (props.onSubmit) {
    props.onSubmit(form);
  }
};

// Close
const closeModal = () => {
  props.onClose?.();
};
</script>

<style scoped>
.disable-events {
  pointer-events: none;
}
</style>
