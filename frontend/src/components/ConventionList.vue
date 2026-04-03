<template>
  <div v-if="isLoading" class="w3-center">
    <img src="/spinner_2.gif" />
  </div>
  <div v-else class="main-container-one">
    <div class="main-item">
      <div class="w3-container">
        <h2 class="w3-center">Liste des Conventions d'exploitation</h2>
      </div>
      <div v-if="conventions">
        <div class="header-actions">
          <form id="search" class="search-form">
            Rechercher <input name="query" v-model="searchQuery" />
          </form>
          <span class="w3-button add-up" @click="goToAddPage">
            <font-awesome-icon icon="plus" /> Ajouter une convention
          </span>
        </div>
        <div class="grid-container">
          <Grid
            :data="conventionsSorted"
            :columns="gridColumns"
            :filter-key="searchQuery"
            :bgColor="'#f7ba0b'"
            :columnLabels="columnLabels"
            @edit="onEdit"
            @delete="onDelete"
          >
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

const features = ref([]); // features Array plour la grille

const conventions = ref([]); // features Object

const isLoading = ref(true);
const router = useRouter();
const mainStore = useMainStore();

const searchQuery = ref("");

const conventionsWithTypeDesc = computed(() => {
  return features.value.map(exp => ({
    ...exp,
    type_description: exp.type_convention_detail?.description || "",
  }));
});

const conventionsSorted = computed(() => {
  return [...conventionsWithTypeDesc.value].sort((a, b) => {
    const upA = a.up_nom?.toLowerCase() || "";
    const upB = b.up_nom?.toLowerCase() || "";
    const expA = a.exploitant_nom.toLowerCase();
    const expB = b.exploitant_nom.toLowerCase();

    if (expA < expB) return -1;
    if (expA > expB) return 1;

    // Si type égaux, trie sur le nom
    if (upA < upB) return -1;
    if (upA > upB) return 1;
    return 0; // égaux
  });
});

const gridColumns = ref(["exploitant_nom", "up_nom", "type_description"]);
const columnLabels = ref({
  exploitant_nom: "Exploitant",
  up_nom: "UP",
  type_description: "Type de convention",
});

const fetchConventions = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/conventionExploitation/`)
    .then((response) => {
      conventions.value = response.data;
      console.log("list response data:", response.data);
      console.log("Conventions.value:", conventions.value);
      if (conventions.value.type === "FeatureCollection") {
        // Transformer les features en tableau
        features.value = conventions.value.features.map((feature) => {
          return {
            ...feature.properties, // Ajoute toutes les propriétés
            id: feature.id, // Ajoute l'id
          };
        });
      }
    })
    .catch((error) => {
      console.error("There was an error!", error);
    })
    .finally(() => {
      isLoading.value = false;
      console.log("fetchConventions done");
    });
};

const goToAddPage = () => {
  console.log("add convention");
  router.push("/Convention/add");
};

// Méthode pour gérer l'édition
function onEdit(entry) {
  console.log("Éditer:", entry.id);
  router.push(`/Convention/edit/${entry.id}`);
}

// Méthode pour gérer la suppression
function onDelete(entry) {
  console.log("Supprimer:", entry.id_convention);
  deleteConvention(entry.id_convention);
}

const deleteConvention = (id) => {
  auth.axiosInstance
    .delete(`${config.API_BASE_URL}/api/conventionExploitation/${id}/`)
    .then((response) => {
      fetchConventions();
      mainStore.setSuccessMessage("Convention supprimée!");
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

onMounted(fetchConventions);
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
  border-radius: 5px; /* Arrondi des coins de la grille */
  overflow: hidden; /* Assure que le contenu s'adapte à l'arrondi */
}
/* Ajoutez vos styles ici */
</style>
