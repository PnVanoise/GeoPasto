<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>

  <v-form ref="formRef" class="subvention-form" @submit.prevent="submitForm">
    <section class="layout-card">
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-textarea
            v-model="form.commentaire"
            :disabled="props.mode === 'view' || !can('change')"
            label="Commentaire"
            density="compact"
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
            :disabled="props.mode === 'view' || !can('change')"
            class="required"
            label="Montant"
            density="compact"
            variant="underlined"
            hide-details="auto"
            :rules="[required]"
            clearable
          />
        </div>
      </div>
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-switch
            id="engage"
            v-model="form.engage"
            :disabled="props.mode === 'view' || !can('change')"
            label="Engagé ?"
            color="primary"
            density="compact"
            hide-details
          />
        </div>
        <div class="w3-half form-cell">
          <v-switch
            id="paye"
            v-model="form.paye"
            :disabled="props.mode === 'view' || !can('change')"
            label="Payé ?"
            color="primary"
            density="compact"
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
            :disabled="props.mode === 'view' || !can('change')"
            class="required"
            label="Alpagiste"
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
import { required } from "@/utils/validators";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" },
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("subventionpnv");

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
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/exploitant/`)
    .then((res) => {
      exploitants.value = res.data;
    })
    .catch((error) => {});
});

const submitForm = async () => {
  if (!props.onSubmit) return;
  const { valid } = await formRef.value.validate();
  if (!valid) return;
  props.onSubmit(form);
};

const closeModal = () => {
  props.onClose?.();
};
</script>
