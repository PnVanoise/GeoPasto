<template>
  <div v-if="isLoading" class="w3-center">
    <img src="/spinner_2.gif" />
  </div>
  <div v-else class="main-container-one">
    <div class="main-item">
      <div class="w3-container">
        <h2 class="w3-center">Liste des subventions</h2>
      </div>
      <div v-if="subventions">
        <div class="header-actions">
          <form id="search" class="search-form">
            Rechercher <input name="query" v-model="searchQuery" />
          </form>
          <span class="w3-button add-up" @click="goToAddPage">
            <font-awesome-icon icon="plus" /> Ajouter une subvention
          </span>
        </div>
        <div class="grid-container">
          <Grid :data="subventionsWithExploitant" :columns="gridColumns" :filter-key="searchQuery" :bgColor="'#f7ba0b'"
            :columnLabels="columnLabels" @edit="onEdit" @view="onView" @delete="onDelete">
          </Grid>
        </div>
      </div>
      <div v-else>Aucune donnée disponible.</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";

import auth from "../../auth";
import Grid from "./Grid.vue";
import config from "../../config";
import { useMainStore } from "../store";

const subventions = ref([]);

const isLoading = ref(true);
const router = useRouter();
const mainStore = useMainStore();

const searchQuery = ref("");
const gridColumns = ref(["nom_exploitant", "description", "montant", "engage", "paye"]);
const columnLabels = ref({
  nom_exploitant: "Bénéficiaire",
  description: "Description",
  montant: "Montant",
  engage: "Engagé",
  paye: "Payé",
});

const subventionsWithExploitant = computed(() => {
  return subventions.value.map(exp => ({
    ...exp,
    nom_exploitant: exp.exploitant_detail?.nom_exploitant || "",
  }));
});

const fetchSubventions = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/subventionPNV/`)
    .then((response) => {
      subventions.value = response.data;
      console.log("list response data:", response.data);
      console.log("subventions.value:", subventions.value);
    })
    .catch((error) => {
      console.error("There was an error!", error);
    })
    .finally(() => {
      isLoading.value = false;
      console.log("fetchSubventions done");
    });
};

const goToAddPage = () => {
  console.log("Ajouter une subvention");
  router.push("/Subvention/add");
};

// Méthode pour gérer l'édition
function onEdit(entry) {
  console.log("Éditer:", entry.id_subvention);

  router.push(`/Subvention/edit/${entry.id_subvention}`);
}

function onView(entry) {
  console.log("View:", entry);
  router.push({
    path: `/Subvention/edit/${entry.id_subvention}`,
    query: { readonly: 'true' }
  });
}

// Méthode pour gérer la suppression
function onDelete(entry) {
  console.log("Supprimer:", entry.id_subvention);
  deleteSubvention(entry.id_subvention);
}

const deleteSubvention = (id) => {
  auth.axiosInstance
    .delete(`${config.API_BASE_URL}/api/subventionPNV/${id}/`)
    .then((response) => {
      fetchSubventions();
      mainStore.setSuccessMessage("Subvention supprimée!");
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

onMounted(fetchSubventions);
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
