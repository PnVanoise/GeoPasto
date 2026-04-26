<template>
  <h3 class="w3-center w3-margin">{{ formTitle }}</h3>
  <form @submit.prevent="submitForm">
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-select
          id="situation"
          v-model="form.situation_exploitation"
          :items="situations"
          item-title="nom_situation"
          item-value="id_situation"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Situation d'exploitation"
          dense
          hide-details
          clearable
        />
      </div>
      <div class="w3-half form-cell">
        <v-select
          id="berger"
          v-model="form.berger"
          :items="bergers"
          item-title="fullName"
          item-value="id_berger"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Berger"
          dense
          hide-details
          clearable
        />
      </div>
    </div>
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">        
        <v-text-field type="date" label="Date de début" v-model="form.date_debut" :class="{ 'disable-events': props.mode === 'view' || !can('change') }" dense hide-details clearable />
      </div>
      <div class="w3-half form-cell">
        <v-text-field type="date" label="Date de fin" v-model="form.date_fin" :class="{ 'disable-events': props.mode === 'view' || !can('change') }" dense hide-details clearable />
      </div>
    </div>
    <div class="w3-row form-ligne">
      <div class="form-cell">
        <v-text-field
          id="commentaire"
          v-model="form.commentaire"
          :class="{ 'disable-events': props.mode === 'view' || !can('change') }"
          label="Commentaire"
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
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("gardesituation");

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
  situation_exploitation: "",
  berger: "",
  date_debut: "",
  date_fin: "",
  commentaire: "",
});

const situations = ref([]);
const bergers = ref([]);

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
  // Récupère les situations
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/situationExploitation/`)
    .then((response) => {
      situations.value = response.data;
      // console.log("situations:", situations.value);
    })
    .catch((error) => {
      console.error(
        "Erreur lors de la récupération de la liste des situations d'exploitation.",
        error
      );
    });

  // Récupère les bergers
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/berger/`)
    .then((response) => {
      // Ajoute un champ `fullName` pour l'affichage dans le v-select
      bergers.value = response.data.map((b) => ({
        ...b,
        fullName: `${b.nom_berger} ${b.prenom_berger}`,
      }));
      // console.log("bergers (with fullName):", bergers.value);
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération de la liste des bergers.", error);
    });
});


// Submits
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

