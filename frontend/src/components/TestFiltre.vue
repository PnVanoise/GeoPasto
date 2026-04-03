<!-- EquipementList.vue -->
<template>
  <div>
    <label for="type-filter">Filtrer par type :</label>
    <select id="type-filter" v-model="selectedType" @change="fetchEquipements">
      <option value="">Tous</option>
      <option v-for="type in types" :key="type.id" :value="type.id">
        {{ type.nom }}
      </option>
    </select>

    <ul>
      <li v-for="equipement in equipements" :key="equipement.id">
        {{ equipement.properties.information_complementaire }} - Etat :{{ equipement.properties.etat }} -
        <span v-if="equipement.geometry">
          Yes 1 ({{ equipement.geometry.coordinates.join(", ") }})
        </span>
        <span v-else> Pas de quartier associé </span>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

import config from "../../config";

const equipements = ref([]);
const types = ref([]);
const selectedType = ref("");

const fetchTypes = async () => {
  try {
    const response = await axios.get(`${config.API_BASE_URL}/api/typeqptAA/`);
    types.value = response.data;
  } catch (error) {
    console.error(error);
  }
};

const fetchEquipements = async () => {
  try {
    let url = `${config.API_BASE_URL}/api/eqptAA/`;
    if (selectedType.value) {
      url += `filter_by_type/?type_id=${selectedType.value}`;
    }
    const response = await axios.get(url);
    equipements.value = response.data.features;
    console.log(equipements.value);
  } catch (error) {
    console.error(error);
  }
};

onMounted(() => {
  fetchTypes();
  fetchEquipements();
});
</script>

<style scoped>
/* Ajoutez votre style ici si nécessaire */
</style>
