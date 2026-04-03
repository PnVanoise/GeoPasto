<template>
  <div>
    <ul>
      <li v-for="alpage in alpages" :key="alpage.id" @click="selectAlpage(alpage)">
        {{ alpage.name }}
      </li>
    </ul>
    <div id="map-container">
      <div id="map">
      </div>
    </div>
    <button @click="addAlpage">Ajouter un alpage</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';

// Déclarer les composants
const components = {
};

// Déclarer les variables réactives
const alpages = ref([]);
const geojson = ref(null);
const router = useRouter();

// Fonction pour récupérer les alpages depuis l'API
const fetchAlpages = () => {
  axios.get('http://151.80.250.138/api/quartierUP/')
    .then(response => {
      alpages.value = response.data;
      geojson.value = response.data;
    });
};

// Appeler fetchAlpages lorsque le composant est monté
onMounted(() => {
  fetchAlpages();
});

// Fonction pour sélectionner un alpage
const selectAlpage = (alpage) => {
  router.push({ name: 'edit-alpage', params: { id: alpage.id } });
};

// Fonction pour ajouter un alpage
const addAlpage = () => {
  router.push({ name: 'add-alpage' });
};
</script>