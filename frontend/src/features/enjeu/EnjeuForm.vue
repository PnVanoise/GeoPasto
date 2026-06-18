<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <v-form ref="formRef" class="enjeu-form" @submit.prevent="submitForm">
    <section class="layout-card">
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <v-text-field
            v-model="form.description"
            :disabled="props.mode === 'view'"
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
      </div>
    </section>

    <div class="form-actions">
      <v-btn color="info" @click="closeModal" prepend-icon="mdi-arrow-left-circle">Retour</v-btn>
      <v-btn
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
import { maxLen, required } from "@/utils/validators";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" },
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("enjeu");

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
  id_enjeu: null,
  description: "",
});

watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) {
      form.id_enjeu = newVal.id_enjeu ?? null;
      form.description = newVal.description ?? "";
    }
  },
  { immediate: true }
);

const submitForm = async () => {
  if (!props.onSubmit) return;
  const { valid } = await formRef.value.validate();
  if (!valid) return;
  const payload = { description: form.description };
  if (props.mode === "change") payload.id_enjeu = form.id_enjeu;
  props.onSubmit(payload);
};

const closeModal = () => {
  props.onClose?.();
};
</script>
