<template>
  <div v-if="isLoading" class="w3-center">
    <img src="/spinner_2.gif" />
  </div>
  <div v-else class="main-container-one">
    <div class="main-item">
      <div class="w3-container">
        <h2 class="w3-center">Liste des abris d'urgence</h2>
      </div>
      <div v-if="abris">
        <div class="header-actions">
          <form id="search" class="search-form">
            Rechercher <input name="query" v-model="searchQuery" />
          </form>
          <span class="w3-button add-up" @click="goToAddPage">
            <font-awesome-icon icon="plus" /> Ajouter un abri d'urgence
          </span>
        </div>
        <div class="grid-container">
          <Grid :data="abris" :columns="gridColumns" :filter-key="searchQuery" :bgColor="'#005187'"
            :columnLabels="columnLabels" @edit="onEdit" @view="onView" @delete="onDelete">
          </Grid>
        </div>
      </div>
      <div v-else>Aucune donnée disponible.</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

import auth from "../../auth";
import Grid from "./Grid.vue";
import config from "../../config";
import { useMainStore } from "../store";

const abris = ref([]);

const isLoading = ref(true);
const router = useRouter();
const mainStore = useMainStore();

const searchQuery = ref("");
const gridColumns = ref(["description", "etat"]);
const columnLabels = ref({
  description: "Description",
  etat: "Etat",
});

const fetchAbris = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/abriDUrgence/`)
    .then((response) => {
      abris.value = response.data;
      console.log("list response data:", response.data);
      console.log("abris.value:", abris.value);
    })
    .catch((error) => {
      console.error("There was an error!", error);
    })
    .finally(() => {
      isLoading.value = false;
      console.log("fetchAbris done");
    });
};

const goToAddPage = () => {
  console.log("Ajouter un abri");
  router.push("/AbriUrgence/add");
};

// Méthode pour gérer l'édition
function onEdit(entry) {
  console.log("Éditer:", entry.id_abri_urgence);

  router.push(`/AbriUrgence/edit/${entry.id_abri_urgence}`);
}

function onView(entry) {
  console.log("View:", entry);
  router.push({
    path: `/AbriUrgence/edit/${entry.id_abri_urgence}`,
    query: { readonly: 'true' }
  });
}

// Méthode pour gérer la suppression
function onDelete(entry) {
  console.log("Supprimer:", entry.id_abri_urgence);
  deleteAbri(entry.id_abri_urgence);
}

const deleteAbri = (id) => {
  auth.axiosInstance
    .delete(`${config.API_BASE_URL}/api/abriDUrgence/${id}/`)
    .then((response) => {
      fetchAbris();
      mainStore.setSuccessMessage("Abri supprimé!");
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

onMounted(fetchAbris);
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
