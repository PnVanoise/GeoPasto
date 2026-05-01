<template>
  <form @submit.prevent="submitForm">
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <label for="information_complementaire">Description:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="information_complementaire"
          v-model="form.information_complementaire"
          required
        />
      </div>
      <div class="w3-half form-cell">
        <label for="etat">Etat:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="etat"
          v-model="form.etat"
          required
        />
      </div>
    </div>
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <label for="quartier_up">QuartierUP:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="quartier_up"
          v-model="form.quartier_up"
          required
        />
      </div>
      <div class="w3-half form-cell">
        <label for="etat">Type équipement:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="type_eqpt_aa"
          v-model="form.type_eqpt_aa"
          required
        />
      </div>
    </div>
    <button type="submit">Enregistrer</button>
  </form>
</template>

<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  initialForm: Object,
  isEdit: Boolean,
  onSubmit: Function,
});

const form = ref({ ...props.initialForm });

const submitForm = () => {
  console.log("Form submitted with:", form.value);
  props
    .onSubmit(form.value)
    .then(() => {
      console.log("Form submission then block executed");
    })
    .catch((error) => {
      console.error("There was an error in form submission!", error);
    });
};

watch(
  () => props.initialForm,
  (newForm) => {
    form.value = { ...newForm };
  },
  { deep: true }
);
</script>

<style scoped>
.form-ligne {
  padding: 8px;
}

.form-cell {
  padding: 8px;
}
</style>
