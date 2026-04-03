<template>
  <form @submit.prevent="submitForm">
    <!-- <div class="w3-row form-ligne"> -->
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
      <label for="commentaire">Commentaire:</label>
      <input
        class="w3-input w3-border"
        type="text"
        id="commentaire"
        v-model="form.commentaire"
        required
        :disabled="props.isReadOnly"
      />
    </div>
    <div class="w3-half form-cell">
      <label for="debut_periode">Date Début Période:</label>
      <input
        class="w3-input w3-border"
        type="date"
        id="debut_periode"
        v-model="form.debut_periode"
        @keydown.prevent
        @paste.prevent
        required
        :disabled="props.isReadOnly"
      />
    </div>
    <div class="w3-half form-cell">
      <label for="fin_periode">Date Fin Période:</label>
      <input
        class="w3-input w3-border"
        type="date"
        id="fin_periode"
        v-model="form.fin_periode"
        @keydown.prevent
        @paste.prevent
        required
        :disabled="props.isReadOnly"
      />
    </div>
    <div class="w3-half form-cell">
      <label for="typedemesure">Type de mesure:</label>
      <select
        class="w3-input w3-border"
        v-model="form.type_mesure"
        id="typedemesure"
        :disabled="props.isReadOnly"
      >
        <option
          v-for="typemesure in typemesures"
          :key="typemesure.id_type_mesure"
          :value="typemesure.id_type_mesure"
        >
          {{ typemesure.description }}
        </option>
      </select>
    </div>
    <div class="w3-half form-cell">
      <label for="plandesuivi">Plan de suivi:</label>
      <select
        class="w3-input w3-border"
        v-model="form.plan_suivi"
        id="plandesuivi"
        :disabled="props.isReadOnly"
      >
        <option
          v-for="plansuivi in plansuivis"
          :key="plansuivi.id_plan_suivi"
          :value="plansuivi.id_plan_suivi"
        >
          {{ plansuivi.description }}
        </option>
      </select>
    </div>

    <!-- next id pour debug -->
    <div v-if="!isEdit" class="form-cell">
      (Next ID:
      {{ nextId }}
      )
    </div>
    <!-- </div> -->
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

const typemesures = ref([]);
const plansuivis = ref([]);

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
  console.log("MesurePlanForm component mounted");

  if (!props.isEdit) {
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/mesurePlan/getNextId/`)
      .then((response) => {
        nextId.value = response.data.next_id;
        form.value.id_mesure_plan = nextId.value; // Optionnel: lier cet ID au formulaire si besoin
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération du Next ID", error);
      });
  }

  // Récupère les types de mesure
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/typeMesure/`)
    .then((response) => {
      typemesures.value = response.data;
    })
    .catch((error) => {
      console.error(
        "Erreur lors de la récupération de la liste des types de mesure",
        error
      );
    });

  // Récupère les plans de suivi
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/planSuivi/`)
    .then((response) => {
      plansuivis.value = response.data;
    })
    .catch((error) => {
      console.error(
        "Erreur lors de la récupération de la liste des plans de suivi",
        error
      );
    });
});

onBeforeUnmount(() => {
  console.log("MesurePlanForm component before unmount");
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
