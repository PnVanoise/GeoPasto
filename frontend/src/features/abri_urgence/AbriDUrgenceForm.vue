<template>
  <h4 class="w3-center w3-margin">{{ formTitle }}</h4>
  <v-form ref="formRef" class="abri-urgence-form" @submit.prevent="submitForm">
    <section class="layout-card">
      <div class="w3-row form-ligne">
        <div class="form-cell">
          <v-text-field
            v-model="form.description"
            label="Description"
            :disabled="props.mode === 'view'"
            class="required"
            density="compact"
            variant="underlined"
            hide-details="auto"
            :rules="[required, maxLen(150)]"
            :counter="150"
            clearable
          />
        </div>
      </div>
      <div class="w3-row form-ligne">
        <div class="form-cell">
          <v-text-field
            v-model="form.etat"
            label="État de l'abri"
            :disabled="props.mode === 'view'"
            class="required"
            density="compact"
            variant="underlined"
            hide-details="auto"
            :rules="[required]"
            clearable
          />
        </div>
      </div>
      <div class="w3-row form-ligne">
        <div class="form-cell">
          <v-textarea
            v-model="form.commentaire"
            label="Commentaire"
            :disabled="props.mode === 'view'"
            density="compact"
            variant="underlined"
            hide-details
            rows="2"
            auto-grow
            clearable
          />
        </div>
      </div>
    </section>

    <section class="layout-card" style="margin-top: 1rem">
      <h4 class="section-title">Commodités associées</h4>
      <template v-if="props.mode === 'add'">
        <div class="w3-panel w3-pale-yellow info-panel">
          Enregistrez l'abri d'urgence pour pouvoir ajouter des commodités.
        </div>
      </template>
      <template v-else>
        <CrudList
          title="Commodités"
          modelName="abridurgencecommodite"
          apiRouteName="abriDUrgenceCommodite"
          itemLabel="une commodité d'abri"
          idField="id_abri_urgence_commodite"
          :columns="commGridColumns"
          :formComponent="AbriDUrgenceCommoditeForm"
          :bgColor="'#904684'"
          :filters="commFilters"
          :showTitle="false"
          :showHeader="true"
          :showSearch="true"
          :showFilters="false"
          :forceAdd="false"
          :viewOnly="props.mode === 'view'"
          :initialNewItem="{ abri_urgence: form.id_abri_urgence }"
        />
      </template>
    </section>

    <div class="form-actions">
      <v-btn color="info" @click="closeModal" prepend-icon="mdi-arrow-left-circle">Retour</v-btn>
      <v-btn
        v-if="props.mode !== 'view'"
        color="success"
        type="submit"
        prepend-icon="mdi-content-save"
        :disabled="formRef?.isValid === false"
      >
        {{ btTitle }}
      </v-btn>
    </div>
  </v-form>
</template>

<script setup>
import { reactive, watch, ref, computed } from "vue";
import { usePermissions } from "../../composables/usePermissions";
import { maxLen, required } from "@/utils/validators";
import CrudList from "../../components/crud/CrudList.vue";
import AbriDUrgenceCommoditeForm from "./AbriDUrgenceCommoditeForm.vue";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" },
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
});

const { can } = usePermissions("abridurgence");

const formRef = ref(null);

const formTitle = computed(() => {
  if (props.mode === "add") return `Ajouter ${props.itemLabel}`;
  if (props.mode === "change") return `Modifier ${props.itemLabel}`;
  return `Voir les détails d'${props.itemLabel}`;
});

const btTitle = computed(() => (props.mode === "add" ? "Ajouter" : "Enregistrer"));

const form = reactive({
  description: "",
  etat: "",
  commentaire: "",
});

const commGridColumns = ref([
  { field: "commodite_desc", label: "Commodité", sortable: true },
  { field: "etat", label: "État", sortable: true },
  { field: "quantite", label: "Quantité", sortable: true },
]);

const commFilters = ref([
  {
    key: "abriFilter",
    type: "hidden",
    default: "",
    apply: (items, _value) => {
      if (!form.id_abri_urgence) return [];
      return (items || []).filter((i) => i.abri_urgence === form.id_abri_urgence);
    },
  },
]);

watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) Object.assign(form, newVal);
  },
  { immediate: true }
);

const submitForm = async () => {
  if (!props.onSubmit) return;
  const { valid } = await formRef.value.validate();
  if (!valid) return;
  props.onSubmit(form);
};

const closeModal = () => props.onClose?.();
</script>

<style scoped>
.section-title {
  margin: 0 0 0.5rem;
  font-size: 0.95rem;
  font-weight: 600;
}
.info-panel {
  padding: 12px;
  border: 1px solid #ddd;
}
</style>
