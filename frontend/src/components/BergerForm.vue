<template>
  <form @submit.prevent="submitForm">
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <label for="nom">Nom:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="nom"
          v-model="form.nom_berger"
          required
          :disabled="props.isReadOnly"
        />
      </div>
      <div class="w3-half form-cell">
        <label for="prenom">Prénom:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="prenom"
          v-model="form.prenom_berger"
          :disabled="props.isReadOnly"
        />
      </div>
      <div class="w3-half form-cell">
        <label for="tel">Téléphone:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="tel"
          v-model="form.tel_berger"
          :disabled="props.isReadOnly"
        />
      </div>
      <div class="w3-half form-cell">
        <label for="adresse">Adresse:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="adresse"
          v-model="form.adresse_berger"
          :disabled="props.isReadOnly"
        />
      </div>
      <div class="w3-half form-cell">
        <label for="comm">Commentaire:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="comm"
          v-model="form.commentaire"
          :disabled="props.isReadOnly"
        />
      </div>
      <!-- next id pour debug -->
      <div v-if="!isEdit" class="form-cell">
        (Next ID:
        {{ nextId }}
        )
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

const form = ref({ ...props.initialForm });

// Variable pour stocker le nextId
const nextId = ref(null);

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
  console.log("BergerForm component mounted");

  if (!props.isEdit) {
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/berger/getNextId/`)
      .then((response) => {
        nextId.value = response.data.next_id;
        form.value.id_berger = nextId.value; // Optionnel: lier cet ID au formulaire si besoin
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération du Next ID", error);
      });
  }
});

onBeforeUnmount(() => {
  console.log("BergerForm component before unmount");
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
