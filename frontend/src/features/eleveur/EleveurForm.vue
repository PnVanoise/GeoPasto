<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>

  <v-form ref="formRef" class="eleveur-form" @submit.prevent="submitForm">
    <section class="layout-card">
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-text-field
            id="nom"
            v-model="form.nom_eleveur"
            :disabled="props.mode === 'view' || !can('change')"
            class="required"
            label="Nom"
            density="compact"
            variant="underlined"
            hide-details="auto"
            :rules="[required]"
            clearable
          />
        </div>
        <div class="w3-half form-cell">
          <v-text-field
            id="prenom"
            v-model="form.prenom_eleveur"
            :disabled="props.mode === 'view' || !can('change')"
            label="Prénom"
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
            id="tel"
            v-model="form.tel_eleveur"
            :disabled="props.mode === 'view' || !can('change')"
            label="Téléphone"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
        <div class="w3-half form-cell">
          <v-text-field
            id="mail"
            v-model="form.mail_eleveur"
            :disabled="props.mode === 'view' || !can('change')"
            label="Email"
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
            id="adresse"
            v-model="form.adresse_eleveur"
            :disabled="props.mode === 'view' || !can('change')"
            label="Adresse"
            density="compact"
            variant="underlined"
            hide-details
            clearable
          />
        </div>
        <div class="w3-half form-cell">
          <v-text-field
            id="commentaire"
            v-model="form.commentaire"
            :disabled="props.mode === 'view' || !can('change')"
            label="Commentaire"
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
import { reactive, watch, ref, computed } from "vue";
import { usePermissions } from "../../composables/usePermissions";
import { required } from "@/utils/validators";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" },
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("eleveur");

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
  id_eleveur: null,
  nom_eleveur: "",
  prenom_eleveur: "",
  tel_eleveur: "",
  mail_eleveur: "",
  adresse_eleveur: "",
  commentaire: "",
});

watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) {
      Object.assign(form, newVal);
      if (newVal.id_eleveur !== undefined && newVal.id_eleveur !== null) {
        form.id_eleveur = newVal.id_eleveur;
      } else if (newVal.id !== undefined && newVal.id !== null) {
        form.id_eleveur = newVal.id;
      }
    }
  },
  { immediate: true }
);

const submitForm = async () => {
  if (!props.onSubmit) return;
  const { valid } = await formRef.value.validate();
  if (!valid) return;
  const payload = JSON.parse(JSON.stringify(form));
  if (props.mode === "add") delete payload.id_eleveur;
  props.onSubmit(payload);
};

const closeModal = () => {
  props.onClose?.();
};
</script>
