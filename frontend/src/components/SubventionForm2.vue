<template>
  <h3 class="w3-center w3-margin">{{ formTitle }}</h3>

  <form @submit.prevent="submitForm">
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-text-field
          id="description"
          v-model="form.description"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Description"
          dense
          hide-details
          clearable
        />
        <!-- <label for="description">Description:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="description"
          v-model="form.description"
          required
          :disabled="props.mode === 'view' || !can('change')"
        /> -->
      </div>
      <div class="w3-half form-cell">
        <v-text-field
          id="montant"
          v-model="form.montant"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Montant"
          dense
          hide-details
          clearable
        />
        <!-- <label for="montant">Montant:</label>
        <label for="montant">Montant:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="nom"
          v-model="form.montant"
          :disabled="props.mode === 'view' || !can('change')"
        /> -->
      </div>
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
        <!-- <label for="engage">Engagé:</label>
        <input
          type="checkbox"
          id="active"
          v-model="form.engage"
          :disabled="props.mode === 'view' || !can('change')"
        /> -->
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
        <!-- <label for="paye">Payé:</label>
        <input
          type="checkbox"
          id="active"
          v-model="form.paye"
          :disabled="props.mode === 'view' || !can('change')"
        /> -->
      </div>
      <div class="w3-half form-cell">
        <v-select
          id="exploitant"
          v-model="form.exploitant"
          :items="exploitants"
          item-title="nom_exploitant"
          item-value="id_exploitant"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Exploitant"
          dense
          hide-details
          clearable
        />
        <!-- <label for="exploitant">Exploitant:</label>
        <select
          class="w3-input w3-border"
          id="exploitant"
          v-model="form.exploitant"
          :disabled="props.mode === 'view' || !can('change')"
        >
          <option
            v-for="exploitant in exploitants"
            :key="exploitant.id_exploitant"
            :value="exploitant.id_exploitant"
          >
            {{ exploitant.nom_exploitant }}
          </option>
        </select> -->
      </div>
    </div>
    
    <div class="form-actions">
      <v-btn density="comfortable" color="info" @click="closeModal" prepend-icon="mdi-arrow-left-circle">Retour</v-btn>
      <v-btn density="comfortable" v-if="props.mode !== 'view'" color="success" type="submit" prepend-icon="mdi-content-save">{{ btTitle }}</v-btn>
    </div>
  </form>
</template>

<script setup>
import { reactive, watch, ref, computed, onMounted } from "vue";
import config from "../../config";
import auth from "../../auth";
import { usePermissions } from "../composables/usePermissions";

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
  description: "",
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
    .then(res => {
      exploitants.value = res.data; 
    })
    .catch((error) => {
      console.error(
        "Erreur lors de la récupération de la liste des exploitants.",
        error
      );
    });
});

// Submit
const submitForm = () => {
  if (props.onSubmit) {
    props.onSubmit(form)
      .then(() => console.log("Form submitted OK"))
      .catch(err => console.error(err));
  }
};

// Close
const closeModal = () => {
  props.onClose?.();
};
</script>

<style scoped>
.form-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.disable-events {
  pointer-events: none
}
</style>
