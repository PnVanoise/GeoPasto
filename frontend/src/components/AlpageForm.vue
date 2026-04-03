<template>
  <form @submit="submitForm">
    <!-- Add your form fields here -->
    <div
      style="
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        align-items: stretch;
      "
    >
      <div style="">
        <div class="form-cell">
          <label for="quartier_code">Code quartier:</label>
          <input
            class="w3-input w3-border"
            type="text"
            id="quartier_code"
            v-model="form.properties.quartier_code"
            required
          />
        </div>
        <div class="form-cell">
          <label for="surface">Surface:</label>
          <input
            class="w3-input w3-border"
            type="text"
            id="surface"
            v-model="form.properties.surface"
            required
          />
        </div>
        <div class="form-cell">
          <label for="up_code">Code UP:</label>
          <input
            class="w3-input w3-border"
            type="text"
            id="up_code"
            v-model="form.properties.up_code"
            required
          />
        </div>
        <div class="form-cell">
          <label for="up_nom_1">Nom UP:</label>
          <input
            class="w3-input w3-border"
            type="text"
            id="up_nom_1"
            v-model="form.properties.up_nom_1"
            required
          />
        </div>

        <div class="form-cell">
          <label for="up_nom_2">Nom UP (2):</label>
          <input
            class="w3-input w3-border"
            type="text"
            id="up_nom_2"
            v-model="form.properties.up_nom_2"
            required
          />
        </div>
        <div class="form-cell">
          <label for="quartier_code_court">Code court quartier:</label>
          <input
            class="w3-input w3-border"
            type="text"
            id="quartier_code_court"
            v-model="form.properties.quartier_code_court"
            required
          />
        </div>
        <div class="form-cell">
          <label for="quartier_nom">Nom quartier:</label>
          <input
            class="w3-input w3-border"
            type="text"
            id="quartier_nom"
            v-model="form.properties.quartier_nom"
            required
          />
        </div>
      </div>
      <div style="">
        <div class="form-cell">
          <label>Géométrie:</label>
          <MapEditMultipolygon2 v-model="form.geometry" />
        </div>
      </div>
    </div>

    <!-- <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <label for="quartier_code">Code quartier:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="quartier_code"
          v-model="form.properties.quartier_code"
          required
        />
      </div>
      <div class="w3-half form-cell">
        <label for="surface">Surface:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="surface"
          v-model="form.properties.surface"
          required
        />
      </div>
    </div>
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <label for="up_code">Code UP:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="up_code"
          v-model="form.properties.up_code"
          required
        />
      </div>
      <div class="w3-half form-cell">
        <label for="up_nom_1">Nom UP:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="up_nom_1"
          v-model="form.properties.up_nom_1"
          required
        />
      </div>
    </div>
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <label for="up_nom_2">Nom UP (2):</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="up_nom_2"
          v-model="form.properties.up_nom_2"
          required
        />
      </div>
      <div class="w3-half form-cell">
        <label for="quartier_code_court">Code court quartier:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="quartier_code_court"
          v-model="form.properties.quartier_code_court"
          required
        />
      </div>
    </div>
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <label for="quartier_nom">Nom quartier:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="quartier_nom"
          v-model="form.properties.quartier_nom"
          required
        />
      </div>
    </div> -->
    <!-- <div>
      <h3>Géométrie :</h3>
      {{ form.geometry }} {{ form.geometry.coordinates.length }}
    </div> -->

    <!-- <div>
      <MapEditMultipolygon2 v-model:geom="form.geometry" />
    </div> -->
    <button type="submit">Enregistrer</button>
  </form>
</template>

<script setup>
import { ref, watch } from "vue";
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
</script>

<style scoped>
.form-ligne {
  padding: 8px;
}

.form-cell {
  padding: 8px;
}
</style>
