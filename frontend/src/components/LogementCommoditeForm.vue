<template>
  <form @submit.prevent="submitForm">
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <label for="logement">Logement:</label>
        <select class="w3-input w3-border" v-model="form.logement" id="logement">
          <option v-for="logement in logements" :key="logement.id" :value="logement.id">
            {{ logement.properties.logement_code }}
          </option>
        </select>
      </div>
      <div class="w3-half form-cell">
        <label for="commodite">Commodité:</label>
        <select class="w3-input w3-border" v-model="form.commodite" id="commodite">
          <option
            v-for="commodite in commodites"
            :key="commodite.id_commodite"
            :value="commodite.id_commodite"
          >
            {{ commodite.description }}
          </option>
        </select>
      </div>
    </div>
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <label for="etat">Etat:</label>
        <input class="w3-input w3-border" type="text" id="etat" v-model="form.etat" />
      </div>
      <div class="w3-half form-cell">
        <label for="quantite">Quantité:</label>
        <input
          class="w3-input w3-border"
          type="numeric"
          id="quantite"
          v-model="form.quantite"
        />
      </div>
    </div>
    <div class="w3-row form-ligne">
      <div class="form-cell">
        <label for="commentaire">Commentaire:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="commentaire"
          v-model="form.commentaire"
        />
      </div>
    </div>
    <div class="w3-row form-ligne">
      <!-- next id pour debug -->
      <div v-if="!isEdit" class="form-cell">
        (Next ID:
        {{ nextId }}
        )
      </div>
      <button type="submit">Enregistrer</button>
    </div>
  </form>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from "vue";

import config from "../../config";
import auth from "../../auth";

const props = defineProps({
  initialForm: Object,
  isEdit: Boolean,
  onSubmit: Function,
  logementId: String,
});

const logements = ref([]);
const commodites = ref([]);

const form = ref({ ...props.initialForm });

// Variable pour stocker le nextId
const nextId = ref(null);

const submitForm = () => {
  console.log("Form submitted with:", form.value);

  if (!props.isEdit) {
    form.value.id = nextId.value;
  }

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
    if (props.logementId) {
      form.value.logement = props.logementId;
    }
  },
  { deep: true, immediate: true }
);

// Hooks de cycle de vie pour déboguer
onMounted(() => {
  console.log("GardeTroupeauForm component mounted");

  if (!props.isEdit) {
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/logementCommodite/getNextId/`)
      .then((response) => {
        nextId.value = response.data.next_id;
        form.value.id_logement_commodite = nextId.value; // Optionnel: lier cet ID au formulaire si besoin
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération du Next ID", error);
      });
  }

  // Récupère les logements
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/logement/`)
    .then((response) => {
      logements.value = response.data.features;
      console.log("logements:", logements.value);
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération de la liste des logements.", error);
    });

  // Récupère les commodités
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/commodite/`)
    .then((response) => {
      commodites.value = response.data;
      console.log("commodites:", commodites.value);
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération de la liste des commodites.", error);
    });
});

onBeforeUnmount(() => {
  console.log("LogementCommodites component before unmount");
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
