<template>
  <h3 class="w3-center w3-margin">{{ formTitle }}</h3>
  <form @submit.prevent="submitForm">
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-select
          v-model="form.logement"
          :items="logements"
          item-title="logement_code"
          item-value="id"
          label="Logement"
          :menu-props="selectMenuProps"
          :disabled="props.mode === 'view'"
          density="compact"
          variant="outlined"
          hide-details
          clearable
        />
      </div>
      <div class="w3-half form-cell">
        <v-select
          v-model="form.commodite"
          :items="commodites"
          item-title="description"
          item-value="id_commodite"
          label="Commodité"
          :menu-props="selectMenuProps"
          :disabled="props.mode === 'view'"
          density="compact"
          variant="outlined"
          hide-details
          clearable
        />
      </div>
    </div>
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-text-field
          v-model="form.etat"
          label="État"
          :disabled="props.mode === 'view'"
          density="compact"
          variant="outlined"
          hide-details
        />
      </div>
      <div class="w3-half form-cell">
        <v-text-field
          v-model.number="form.quantite"
          label="Quantité"
          type="number"
          :disabled="props.mode === 'view'"
          density="compact"
          variant="outlined"
          hide-details
        />
      </div>
    </div>
    <div class="w3-row form-ligne">
      <div class="w3-col s12 form-cell">
        <v-text-field
          v-model="form.commentaire"
          label="Commentaire"
          :disabled="props.mode === 'view'"
          density="compact"
          variant="outlined"
          hide-details
        />
      </div>
    </div>

    <div class="form-actions">
      <v-btn color="info" @click="closeModal" prepend-icon="mdi-arrow-left-circle">Retour</v-btn>
      <v-btn v-if="props.mode !== 'view'" color="success" type="submit" prepend-icon="mdi-content-save">
        {{ btTitle }}
      </v-btn>
    </div>
  </form>
</template>

<script setup>
import { computed, reactive, ref, watch, onMounted } from "vue";
import config from "../../../config";
import auth from "@/services/axios";
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

const logements = ref([]);
const commodites = ref([]);

const form = reactive({
  logement: null,
  commodite: null,
  etat: "",
  quantite: null,
  commentaire: "",
});

watch(
  () => props.initialForm,
  (newVal) => {
    const src = newVal || {};
    form.logement = src.logement ?? null;
    form.commodite = src.commodite ?? null;
    form.etat = src.etat ?? "";
    form.quantite = src.quantite ?? null;
    form.commentaire = src.commentaire ?? "";
  },
  { deep: true, immediate: true }
);

const submitForm = () => {
  props.onSubmit?.({ ...form })
    .catch((err) => console.error("Erreur soumission logement/commodité", err));
};

const closeModal = () => props.onClose?.();

onMounted(async () => {
  try {
    const [resLog, resCom] = await Promise.all([
      auth.axiosInstance.get(`${config.API_BASE_URL}/api/logement/`),
      auth.axiosInstance.get(`${config.API_BASE_URL}/api/commodite/`),
    ]);
    const fc = resLog.data;
    logements.value = (fc.features ?? []).map(f => ({
      id: f.id,
      logement_code: f.properties?.logement_code ?? f.id,
    }));
    commodites.value = resCom.data ?? [];
  } catch (err) {
    console.error("Erreur chargement données logement/commodité", err);
  }
});
</script>

<style scoped>
.form-ligne { padding: 4px; }
.form-cell  { padding: 4px; }

.form-actions {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1.2rem;
}
</style>
