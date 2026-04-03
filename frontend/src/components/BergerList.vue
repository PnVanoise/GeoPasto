<template>
  <div v-if="isLoading" class="w3-center">
    <img src="/spinner_2.gif" />
  </div>
  <div v-else class="main-container-one">
    <div v-if="canView">
      <div class="main-item">
        <div class="w3-container">
          <h2 class="w3-center">Liste des bergers</h2>
        </div>
        <div v-if="bergers">
          <div class="header-actions">
            <form id="search" class="search-form">
              Rechercher <input name="query" v-model="searchQuery" />
            </form>
            <span v-if="canAdd" class="w3-button add-up" @click="goToAddPage">
              <font-awesome-icon icon="plus" /> Ajouter un berger
            </span>
          </div>
          <div class="grid-container">
            <Grid :data="bergers" :columns="gridColumns" :filter-key="searchQuery" :bgColor="'#f7ba0b'"
              :columnLabels="columnLabels" @edit="onEdit" @view="onView" @delete="onDelete">
            </Grid>
          </div>
        </div>
        <div v-else>Aucune donnée disponible.</div>
      </div>
    </div>
    <p v-else>
      Vous n'avez pas la permission de voir cette page.
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

import auth from "../../auth";
import Grid from "./Grid.vue";
import config from "../../config";
import { useMainStore } from "../store";

const bergers = ref([]);

const isLoading = ref(true);
const router = useRouter();
const mainStore = useMainStore();

const searchQuery = ref("");
const gridColumns = ref(["nom_berger", "prenom_berger"]);
const columnLabels = ref({
  nom_berger: "Nom",
  prenom_berger: "Prénom",
});

// droits
console.log(mainStore);
const canView = mainStore.hasPermission('berger', 'view');
const canAdd = mainStore.hasPermission('berger', 'add');

const fetchBergers = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/berger/`)
    .then((response) => {
      bergers.value = response.data;
      console.log("list response data:", response.data);
      console.log("bergers.value:", bergers.value);
    })
    .catch((error) => {
      console.error("There was an error!", error);
    })
    .finally(() => {
      isLoading.value = false;
      console.log("fetchBergers done");
    });
};

const goToAddPage = () => {
  console.log("Ajouter un berger");
  router.push("/Berger/add");
};

// Méthode pour gérer l'édition
function onEdit(entry) {
  console.log("Éditer:", entry.id_berger);

  router.push(`/Berger/edit/${entry.id_berger}`);
}

function onView(entry) {
  console.log("View:", entry);
  router.push({
    path: `/Berger/edit/${entry.id_berger}`,
    query: { readonly: 'true' }
  });
}

// Méthode pour gérer la suppression
function onDelete(entry) {
  console.log("Supprimer:", entry.id_berger);
  deleteBerger(entry.id_berger);
}

const deleteBerger = (id) => {
  auth.axiosInstance
    .delete(`${config.API_BASE_URL}/api/berger/${id}/`)
    .then((response) => {
      fetchBergers();
      mainStore.setSuccessMessage("Berger supprimé!");
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

onMounted(fetchBergers);
</script>

<style scoped>
.title-container {
  display: flex;
  align-items: center;
}

.loading-image {
  margin-right: 10px;
}

.main-container-one {
  display: grid;
  grid-template-columns: 100%;
}

.main-container {
  display: grid;
  grid-template-columns: 50% 50%;
}

.main-item {
  padding: 20px;
  margin: 10px;
  text-align: center;
}

/* Style pour aligner le formulaire de recherche et le bouton d'ajout */
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  margin-bottom: 10px;
  max-height: 30px;
}

/* Style pour le formulaire de recherche */
.search-form {
  display: inline-block;
}

/* Style pour le bouton d'ajout */
.add-up {
  background-color: #bdc3c7;
  color: 2c3e50;
  padding: 10px 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  border-radius: 5px;
}

.add-up:hover {
  background-color: #aab2b7;
}

/* Style pour l'input de recherche */
#search input {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.grid-container {
  border-radius: 5px;
  /* Arrondi des coins de la grille */
  overflow: hidden;
  /* Assure que le contenu s'adapte à l'arrondi */
}

/* Ajoutez vos styles ici */
</style>
