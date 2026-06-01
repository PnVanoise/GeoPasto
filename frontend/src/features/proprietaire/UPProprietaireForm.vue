<template>
  <h3 class="w3-center w3-margin">{{ formTitle }}</h3>
  <form @submit.prevent="submitForm">
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <v-select
          v-model="form.unite_pastorale"
          :items="ups"
          item-title="nom_up"
          item-value="id_unite_pastorale"
          label="Unité pastorale"
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
          v-model="form.proprietaire"
          :items="proprietaires"
          item-title="nom_complet"
          item-value="id_proprietaire"
          label="Propriétaire"
          :menu-props="selectMenuProps"
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

const ups = ref([]);
const proprietaires = ref([]);

const form = reactive({
  unite_pastorale: null,
  proprietaire: null,
});

watch(
  () => props.initialForm,
  (newVal) => {
    const src = newVal || {};
    form.unite_pastorale = src.unite_pastorale ?? null;
    form.proprietaire = src.proprietaire ?? null;
  },
  { deep: true, immediate: true }
);

const submitForm = () => {
  props.onSubmit?.({ ...form });
};

const closeModal = () => props.onClose?.();

onMounted(async () => {
  try {
    const [resUP, resPropr] = await Promise.all([
      auth.axiosInstance.get(`${config.API_BASE_URL}/api/unitePastorale/light/`),
      auth.axiosInstance.get(`${config.API_BASE_URL}/api/proprietaireFoncier/`),
    ]);
    ups.value = resUP.data ?? [];
    proprietaires.value = (resPropr.data ?? []).map((p) => ({
      ...p,
      nom_complet: `${p.nom_propr} ${p.prenom_propr || ""}`.trim(),
    }));
  } catch (err) {}
});
</script>

<style scoped>
.form-ligne {
  padding: 4px;
}
.form-cell {
  padding: 4px;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1.2rem;
}
</style>
