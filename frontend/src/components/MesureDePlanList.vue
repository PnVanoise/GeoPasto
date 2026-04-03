<template>
  <div v-if="isLoading" class="w3-center">
    <img src="/spinner_2.gif" />
  </div>
  <div v-else class="main-container-one">
    <div class="main-item">
      <div class="w3-container">
        <h2 class="w3-center">Liste des mesures de plan</h2>
      </div>
      <div v-if="mesuredeplans">
        <div class="header-actions">
          <form id="search" class="search-form">
            Rechercher <input name="query" v-model="searchQuery" />
          </form>
          <span class="w3-button add-up" @click="goToAddPage">
            <font-awesome-icon icon="plus" /> Ajouter une mesure de plan
          </span>
        </div>
        <div class="grid-container">
          <Grid :data="mesuredeplansWithDesc" :columns="gridColumns" :filter-key="searchQuery" :bgColor="'#f7ba0b'"
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

const mesuredeplans = ref([]);

const isLoading = ref(true);
const router = useRouter();
const mainStore = useMainStore();

const searchQuery = ref("");
const gridColumns = ref(["description", "description_type", "nom_up", "debut_periode", "fin_periode"]);
const columnLabels = ref({
  description: "Description",
  description_type: "Type de mesure",
  nom_up: "UP",
  debut_periode: "Début",
  fin_periode: "Fin"
});

const mesuredeplansWithDesc = computed(() => {
  return mesuredeplans.value.map(exp => ({
    ...exp,
    description_type: exp.type_mesure_detail?.description || "",
    nom_up: exp.plan_suivi_detail?.unite_pastorale_detail?.nom_up || "",
  }));

});

const fetchMesurePlans = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/mesurePlan/`)
    .then((response) => {
      mesuredeplans.value = response.data;
      console.log("list response data:", response.data);
      console.log("mesureplans.value:", mesuredeplans.value);
    })
    .catch((error) => {
      console.error("There was an error!", error);
    })
    .finally(() => {
      isLoading.value = false;
      console.log("fetchMesurePlans done");
    });
};

const goToAddPage = () => {
  console.log("add mesurePlan");
  router.push("/MesurePlan/add");
};

// Méthode pour gérer l'édition
function onEdit(entry) {
  console.log("Éditer:", entry.id_mesure_plan);
  router.push(`/MesurePlan/edit/${entry.id_mesure_plan}`);
}

function onView(entry) {
  console.log("View:", entry);
  router.push({
    path: `/MesurePlan/edit/${entry.id_mesure_plan}`,
    query: { readonly: 'true' }
  });
}

// Méthode pour gérer la suppression
function onDelete(entry) {
  console.log("Supprimer:", entry.id_mesure_plan);
  deleteMesurePlan(entry.id_mesure_plan);
}

const deleteMesurePlan = (id) => {
  auth.axiosInstance
    .delete(`${config.API_BASE_URL}/api/mesurePlan/${id}/`)
    .then((response) => {
      fetchMesurePlans();
      mainStore.setSuccessMessage("Mesure de plan supprimée!");
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

onMounted(fetchMesurePlans);
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
