<template>
  <h3 class="w3-center w3-margin">{{ formTitle }}</h3>
  <form @submit.prevent="submitForm">
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-select
          id="abri"
          v-model="form.abri_urgence"
          :class="{ 'disable-events': true }"
          :items="abris"
          item-title="description"
          item-value="id_abri_urgence"
          label="Abri d'urgence"
          dense
          hide-details
          clearable
        />
      </div>
      <div class="w3-half form-cell">
        <v-select
          id="commodite"
          v-model="form.commodite"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          :items="commodites"
          item-title="description"
          item-value="id_commodite"
          label="Commodité"
          dense
          hide-details
          clearable
        />
      </div>
    </div>
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-text-field
          type="text"
          label="Etat"
          v-model="form.etat"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          dense
          hide-details
          clearable
        />
      </div>
      <div class="w3-half form-cell">
        <v-text-field
          type="number"
          label="Quantité"
          v-model.number="form.quantite"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          dense
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
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          dense
          hide-details
          clearable
        />
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
  id_abri_urgence_commodite: null,
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

// Ensure abri id is applied when parent passes it explicitly
watch(
  () => props.abriId,
  (newVal) => {
    if (newVal != null) {
      form.abri_urgence = newVal;
    }
  },
  { immediate: true }
);

// Next ID pour l'ajout
const nextId = ref(null);
onMounted(() => {
  if (props.mode === "add") {
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/abriDUrgenceCommodite/getNextId/`)
      .then((response) => {
        nextId.value = response.data.next_id;
        form.id_abri_urgence_commodite = nextId.value;
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération du Next ID", error);
      });
  }

  // Récupère les abris
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/abriDUrgence/`)
    .then((response) => {
      abris.value = response.data;
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération de la liste des abris.", error);
    });

  // Récupère les commodités
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/commodite/`)
    .then((response) => {
      commodites.value = response.data;
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération de la liste des commodites.", error);
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
