<template>
  <div v-if="isLoading" class="w3-center">
    <img src="/spinner_2.gif" />
  </div>
  <div v-else class="main-container-one">
    <div class="main-item">
      <div class="w3-container">
        <h2 class="w3-center">Liste des types d'équipement</h2>
      </div>
      <!-- <div class="w3-container">
        <h2 class="w3-left">Types d'équipement d'alpage</h2>
        <span class="w3-button w3-right" @click="goToAddPage">Ajouter un type</span>
      </div> -->
      <div v-if="typeEqpts">
        <div class="header-actions">
          <form id="search" class="search-form">
            Rechercher <input name="query" v-model="searchQuery" />
          </form>
          <span class="w3-button add-up" @click="goToAddPage">
            <font-awesome-icon icon="plus" /> Ajouter un type
          </span>
        </div>
        <div class="grid-container">
          <Grid :data="typeEqpts" :columns="gridColumns" :filter-key="searchQuery" :bgColor="'#d05d28'"
            :columnLabels="columnLabels" @edit="onEdit" @delete="onDelete">
          </Grid>
        </div>
        <!-- <ul class="w3-ul w3-card-4 liste-d-items">
          <li v-for="typeEqpt in typeEqpts" :key="typeEqpt.id">
            <span
              class="w3-bar-item w3-button w3-white w3-right"
              @click="deleteTypeEqpt(typeEqpt.id)"
              >Supprimer</span
            >
            <span
              class="w3-bar-item w3-button w3-white w3-right"
              @click="editTypeEqpt(typeEqpt.id)"
              >Détails</span
            >
            <div class="w3-bar-item">
              <span class="w3-large">{{ typeEqpt.id }} - {{ typeEqpt.nom }}</span
              ><br />
              <span>{{ typeEqpt.description }}</span>
            </div>
          </li>
        </ul> -->
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

const typeEqpts = ref([]);

const isLoading = ref(true);
const router = useRouter();
const mainStore = useMainStore();

const searchQuery = ref("");
const gridColumns = ref(["nom", "description"]);
const columnLabels = ref({
  nom: "Nom",
  description: "Description",
});
const features = ref([]);

const fetchTypeEqpts = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/typeqptAA/`)
    .then((response) => {
      typeEqpts.value = response.data;
      console.log("list response data:", response.data);
      console.log("typeEqpts.value:", typeEqpts.value);
      // if (typeEqpts.value.type === "FeatureCollection") {
      // Transformer les features en tableau
      // features.value = typeEqpts.value.features.map((feature) => {
      //   return {
      //     ...feature.properties, // Ajoute toutes les propriétés
      //     id: feature.id, // Ajoute l'id
      //   };
      // });
      // }
    })
    .catch((error) => {
      console.error("There was an error!", error);
    })
    .finally(() => {
      isLoading.value = false;
      console.log("fetchTypeEqpts done");
    });
};

const goToAddPage = () => {
  router.push("/TypeEquipementAlpage/add");
};

// Méthode pour gérer l'édition
function onEdit(entry) {
  console.log("Éditer:", entry.id);

  router.push(`/TypeEquipementAlpage/edit/${entry.id}`);
}

// Méthode pour gérer la suppression
function onDelete(entry) {
  console.log("Supprimer:", entry.id);
  deleteTypeEqpt(entry.id);
}

// const editTypeEqpt = (id) => {
//   router.push(`/TypeEquipementAlpage/edit/${id}`);
// };

const deleteTypeEqpt = (id) => {
  auth.axiosInstance
    .delete(`${config.API_BASE_URL}/api/typeqptAA/${id}/`)
    .then((response) => {
      fetchTypeEqpts();
      mainStore.setSuccessMessage("Type d'équipement supprimé!");
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

onMounted(fetchTypeEqpts);
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
