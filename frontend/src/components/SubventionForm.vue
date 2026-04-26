<template>
  <p>Mode lecture seule : {{ isReadOnly }}</p>
  <form @submit.prevent="submitForm">
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <label for="description">Description:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="description"
          v-model="form.description"
          required
          :disabled="props.isReadOnly"
        />
      </div>
      <div class="w3-half form-cell">
        <label for="montant">Montant:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="nom"
          v-model="form.montant"
          :disabled="props.isReadOnly"
        />
      </div>
      <div class="w3-half form-cell">
        <label for="engage">Engagé:</label>
        <input
          type="checkbox"
          id="active"
          v-model="form.engage"
          :disabled="props.isReadOnly"
        />
      </div>
      <div class="w3-half form-cell">
        <label for="paye">Payé:</label>
        <input
          type="checkbox"
          id="active"
          v-model="form.paye"
          :disabled="props.isReadOnly"
        />
      </div>
      <div class="w3-half form-cell">
        <label for="exploitant">Exploitant:</label>
        <select
          class="w3-input w3-border"
          id="exploitant"
          v-model="form.exploitant"
          :disabled="props.isReadOnly"
        >
          <option
            v-for="exploitant in exploitants"
            :key="exploitant.id_exploitant"
            :value="exploitant.id_exploitant"
          >
            {{ exploitant.nom_exploitant }}
          </option>
        </select>
      </div>

    </div>
    <button v-if="!isReadOnly" type="submit">Enregistrer</button>
  </form>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from "vue";
import config from "../../config";
import auth from "../../auth";

const props = defineProps({
  initialForm: Object,
  isEdit: Boolean,
  isReadOnly: {
    type: Boolean,
    default: false,
  },
  onSubmit: Function,
});

const exploitants = ref([]);

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

onMounted(() => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/exploitant/`)
    .then((response) => {
      exploitants.value = response.data;
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération de la liste des exploitants", error);
    });
});

onBeforeUnmount(() => {
  console.log("EleveurForm component before unmount");
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
