<template>
  <h3 class="w3-center w3-margin">{{ formTitle }}</h3>

  <form class="eqpt-form" @submit.prevent="submitForm">
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-text-field
          v-model.number="form.id_equipement_alpage"
          type="number"
          label="ID"
          :disabled="props.mode === 'view' || autoId"
          :readonly="autoId"
          density="compact"
          variant="outlined"
          hide-details
        />
      </div>
      <div class="w3-half form-cell">
        <v-switch
          v-model="autoId"
          label="ID auto"
          color="primary"
          :disabled="props.mode === 'view'"
          density="compact"
          hide-details
        />
      </div>
    </div>

    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-text-field
          v-model="form.description"
          label="Description"
          :disabled="props.mode === 'view'"
          density="compact"
          variant="outlined"
          hide-details
          required
        />
      </div>
      <div class="w3-half form-cell">
        <v-text-field
          v-model="form.etat"
          label="État"
          :disabled="props.mode === 'view'"
          density="compact"
          variant="outlined"
          hide-details
          required
        />
      </div>
    </div>

    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-select
          v-model="form.type_equipement"
          :items="typesEquipement"
          item-title="description"
          item-value="id_type_equipement"
          label="Type équipement"
          :disabled="props.mode === 'view'"
          density="compact"
          variant="outlined"
          hide-details
          clearable
        />
      </div>
      <div class="w3-half form-cell">
        <v-select
          v-model="form.unite_pastorale"
          :items="ups"
          item-title="nom_up"
          item-value="id_unite_pastorale"
          label="Unité pastorale"
          :disabled="props.mode === 'view'"
          density="compact"
          variant="outlined"
          hide-details
          clearable
        />
      </div>
    </div>

    <div class="form-actions">
      <v-btn color="info" @click="closeModal" prepend-icon="mdi-arrow-left-circle">Retour</v-btn>
      <v-btn v-if="props.mode !== 'view'" color="success" type="submit" prepend-icon="mdi-content-save">{{ btTitle }}</v-btn>
    </div>
  </form>
</template>

<script setup>
import { computed, reactive, ref, watch, onMounted } from "vue";
import config from "../../config";
import auth from "../../auth";

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
  return `Voir les details d'${props.itemLabel}`;
});

const btTitle = computed(() => (props.mode === "add" ? "Ajouter" : "Enregistrer"));

const autoId = ref(true);
const typesEquipement = ref([]);
const ups = ref([]);

const form = reactive({
  id_equipement_alpage: null,
  description: "",
  etat: "",
  type_equipement: null,
  unite_pastorale: null,
});

const closeModal = () => props.onClose?.();

const fetchNextId = async () => {
  if (props.mode !== "add" || !autoId.value) return;
  try {
    const res = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/equipementAlpage/getNextId/`);
    form.id_equipement_alpage = res.data?.next_id ?? form.id_equipement_alpage;
  } catch (err) {
    console.error("Erreur next id equipement alpage", err);
  }
};

watch(autoId, (enabled) => {
  if (enabled) fetchNextId();
});

watch(
  () => props.initialForm,
  (newVal) => {
    const src = newVal?.properties ? { ...newVal.properties, id_equipement_alpage: newVal.id ?? newVal.properties.id_equipement_alpage } : (newVal || {});
    form.id_equipement_alpage = src.id_equipement_alpage ?? src.id ?? null;
    form.description = src.description ?? "";
    form.etat = src.etat ?? "";
    form.type_equipement = src.type_equipement ?? null;
    form.unite_pastorale = src.unite_pastorale ?? null;
    if (props.mode !== "add") autoId.value = false;
  },
  { deep: true, immediate: true }
);

const submitForm = async () => {
  const payload = {
    id_equipement_alpage: form.id_equipement_alpage,
    description: form.description,
    etat: form.etat,
    type_equipement: form.type_equipement,
    unite_pastorale: form.unite_pastorale,
    geometry: null,
  };
  if (props.mode === "add") delete payload.geometry;
  return props.onSubmit?.(payload);
};

onMounted(async () => {
  try {
    const [typeRes, upRes] = await Promise.all([
      auth.axiosInstance.get(`${config.API_BASE_URL}/api/typeEquipement/`),
      auth.axiosInstance.get(`${config.API_BASE_URL}/api/unitePastorale/light/`),
    ]);
    typesEquipement.value = typeRes.data || [];
    ups.value = upRes.data || [];
  } catch (err) {
    console.error("Erreur chargement refs equipement alpage", err);
  }
  await fetchNextId();
});
</script>

<style scoped>
.form-ligne { padding: 4px; }
.form-cell { padding: 4px; }
.form-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.2rem;
}
</style>
