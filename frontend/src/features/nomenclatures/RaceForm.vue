<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <v-form ref="formRef" class="race-form" @submit.prevent="submitForm">
    <section class="layout-card">
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-text-field
            id="description"
            v-model="form.description"
            :disabled="props.mode === 'view' || !can('change')"
            class="required"
            label="Description"
            density="compact"
            variant="underlined"
            hide-details="auto"
            :rules="[required, maxLen(150)]"
            :counter="150"
            clearable
          />
        </div>
        <div class="w3-half form-cell">
          <v-select
            id="espece"
            v-model="form.espece"
            :items="especes"
            item-title="description"
            item-value="id_espece"
            :disabled="props.mode === 'view' || !can('change')"
            label="Espèce"
            density="compact"
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
        :disabled="formRef?.isValid === false"
        >{{ btTitle }}</v-btn
      >
    </div>
  </v-form>
</template>

<script setup>
import { reactive, watch, ref, computed, onMounted } from "vue";
import config from "../../../config";
import auth from "@/services/axios";
import { usePermissions } from "../../composables/usePermissions";
import { maxLen, required } from "@/utils/validators";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" },
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("race");

const formRef = ref(null);

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
  espece: "",
});

const especes = ref([]);

watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) {
      Object.assign(form, newVal);
      if (newVal.id_race !== undefined && newVal.id_race !== null) {
        form.id_race = newVal.id_race;
      } else if (newVal.id !== undefined && newVal.id !== null) {
        form.id_race = newVal.id;
      }
    }
  },
  { immediate: true }
);

onMounted(() => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/espece/`)
    .then((response) => {
      especes.value = response.data;
    })
    .catch((error) => {});
});

const submitForm = async () => {
  if (!props.onSubmit) return;
  const { valid } = await formRef.value.validate();
  if (!valid) return;
  const payload = JSON.parse(JSON.stringify(form));
  if (props.mode === "add") delete payload.id_race;
  props.onSubmit(payload);
};

const closeModal = () => {
  props.onClose?.();
};
</script>
