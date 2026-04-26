<template>
  <p>Mode lecture seule : {{ isReadOnly }}</p>
  <form @submit.prevent="submitForm">
    <div class="w3-row form-ligne">
      <div class="w3-half form-cell">
        <label for="desc">Description:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="desc"
          v-model="form.description"
          required
          :disabled="props.isReadOnly"
        />
      </div>
      <div class="w3-half form-cell">
        <label for="etat">Etat:</label>
        <input
          class="w3-input w3-border"
          type="text"
          id="etat"
          v-model="form.etat"
          :disabled="props.isReadOnly"
        />
      </div>
    </div>
    <button v-if="!props.isReadOnly" @click="submitForm">Enregistrer</button>

    <div class="grid-container" style="margin-top:1rem;">
      <label>Commodités associées :</label>
      <Grid
        :data="abriCommodites"
        :columns="commGridColumns"
        :bgColor="'#f7ba0b'"
        :columnLabels="commColumnLabels"
        @edit="commOnEdit"
        @delete="commOnDelete"
      />
      <div class="form-cell">
        <button type="button" class="w3-button w3-blue" @click="openAddCommodite">Ajouter une commodité</button>
      </div>
    </div>

    <Modal v-model:show="showCommoditeModal">
      <AbriDUrgenceCommoditeForm
        :initialForm="selectedCommodite"
        :isEdit="isEditCommodite"
        :abriId="form.id_abri_urgence"
        :onSubmit="handleCommoditeSubmit"
      />
    </Modal>
  </form>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from "vue";

import config from "../../config";
import auth from "../../auth";
import Grid from './Grid.vue';
import Modal from './Modal.vue';
import AbriDUrgenceCommoditeForm from './AbriDUrgenceCommoditeForm.vue';
import { useMainStore } from '../store';

import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";

dayjs.extend(utc);

const props = defineProps({
  initialForm: Object,
  isEdit: Boolean,
  isReadOnly: {
    type: Boolean,
    default: false
  },
  onSubmit: Function,
});

const form = ref({ ...props.initialForm });

const abriCommodites = ref([]);
const commGridColumns = ref(['abri_urgence_description', 'commodite_desc', 'etat', 'quantite']);
const commColumnLabels = ref({ abri_urgence_description: 'Abri', commodite_desc: 'Commodité', etat: 'État', quantite: 'Quantité' });

const showCommoditeModal = ref(false);
const isEditCommodite = ref(false);
const selectedCommodite = ref({});

const mainStore = useMainStore();

const fetchAbriCommodites = () => {
  if (!form.value.id_abri_urgence) {
    abriCommodites.value = [];
    return;
  }
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/abriDUrgenceCommodite/?abriId=${form.value.id_abri_urgence}`)
    .then((response) => {
      abriCommodites.value = response.data;
    })
    .catch((error) => {
      console.error('Erreur récupération abri commodites', error);
    });
};

const submitForm = () => {
  const userData = localStorage.getItem("user");
  if (userData) {
    const user = JSON.parse(userData);
    if (!props.isEdit) {
      form.value.created_by = user.username;
      form.value.created_on = dayjs().utc().format();
    } else {
      form.value.modified_by = user.username;
      form.value.modified_on = dayjs().utc().format();
    }
  }

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
  console.log("AbriForm component mounted");

});

onBeforeUnmount(() => {
  console.log("AbriForm component before unmount");
});

watch(
  () => props.initialForm,
  (newForm) => {
    form.value = { ...newForm };
    // refresh list of commodites for this abri
    fetchAbriCommodites();
  },
  { deep: true }
);

function openAddCommodite() {
  selectedCommodite.value = { abri_urgence: form.value.id_abri_urgence, commodite: '', etat: '', quantite: 0, commentaire: '' };
  isEditCommodite.value = false;
  showCommoditeModal.value = true;
}

function commOnEdit(entry) {
  selectedCommodite.value = { ...entry };
  isEditCommodite.value = true;
  showCommoditeModal.value = true;
}

function commOnDelete(entry) {
  if (!entry || !entry.id_abri_urgence_commodite) return;
  auth.axiosInstance
    .delete(`${config.API_BASE_URL}/api/abriDUrgenceCommodite/${entry.id_abri_urgence_commodite}/`)
    .then(() => {
      fetchAbriCommodites();
      mainStore.setSuccessMessage('Abri / commodité supprimé !');
    })
    .catch((err) => {
      console.error('Erreur suppression abri commodite', err);
    });
}

const handleCommoditeSubmit = async (payload) => {
  try {
    if (isEditCommodite.value && payload.id_abri_urgence_commodite) {
      await auth.axiosInstance.put(`${config.API_BASE_URL}/api/abriDUrgenceCommodite/${payload.id_abri_urgence_commodite}/`, payload);
      mainStore.setSuccessMessage('Abri / commodité modifiée !');
    } else {
      await auth.axiosInstance.post(`${config.API_BASE_URL}/api/abriDUrgenceCommodite/`, payload);
      mainStore.setSuccessMessage('Abri / commodité ajoutée !');
    }
    showCommoditeModal.value = false;
    fetchAbriCommodites();
  } catch (e) {
    console.error('Erreur sauvegarde abri commodite', e);
  }
};
</script>

<style scoped>
.form-ligne {
  padding: 8px;
}

.form-cell {
  padding: 8px;
}
</style>
