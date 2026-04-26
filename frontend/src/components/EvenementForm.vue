<template>
  <form @submit.prevent="submitForm">
    <div
      style="
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        align-items: stretch;
      "
    >
    <div style="">
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <label for="description">Description</label>
          <input
            class="w3-input w3-border"
            type="text"
            id="description"
            v-model="form.properties.description"
            required
          />
        </div>
        <div class="w3-half form-cell">
          <label for="source">Source</label>
          <input
            class="w3-input w3-border"
            type="text"
            id="source"
            v-model="form.properties.source"
            required
          />
        </div>
      </div>
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <label for="date_evenement">Date évènement</label>
          <input
            class="w3-input w3-border"
            type="date"
            id="source"
            v-model="form.properties.date_evenement"
            required
          />
        </div>
        <div class="w3-half form-cell">
          <label for="date_observation">Date observation</label>
          <input
            class="w3-input w3-border"
            type="date"
            id="source"
            v-model="form.properties.date_observation"
            required
          />
        </div>
      </div>
      <div class="w3-row form-ligne">
        <div class="w3-half form-cell">
          <label for="observateur">Observateur</label>
          <input
            class="w3-input w3-border"
            type="text"
            id="source"
            v-model="form.properties.observateur"
            required
          />
        </div>
      </div>
    </div>
    <div style="">
      <div class="form-cell">
        Géométrie:
        <MapEditMultipolygon2
          :key="form.geometry.coordinates"
          v-model="form.geometry"
          :geometryType="'Point'"
        />
      </div>
    </div>

    <button type="submit">Enregistrer</button>
    </div>
  </form>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from "vue";

import config from "../../config";
import auth from "../../auth";

import MapEditMultipolygon2 from "./MapEditMultipolygon2.vue";  

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

// Hooks de cycle de vie pour déboguer
onMounted(() => {
  console.log("EvenementForm component mounted");

});

onBeforeUnmount(() => {
  console.log("EvenementForm component before unmount");
});
</script>

<style scoped>
.form-ligne {
  padding: 8px;
}

.form-cell {
  padding: 8px;
}
</style>
