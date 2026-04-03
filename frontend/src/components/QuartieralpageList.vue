<template>
    <div>
        <h1>Liste des quartiers d'alpage</h1>
        <button @click="goToAddPage">Ajouter un quartier d'alpage</button>
        <ul>
            <li v-for="quartieralpage in quartieralpages.features" :key="quartieralpage.id">
                {{ quartieralpage.properties.id }} - {{ quartieralpage.properties.quartier_code_court }} - {{ quartieralpage.properties.date_presence_troupeau }}
                <button @click="editQuartieralpage(quartieralpage.id)">Éditer</button>
                <button @click="deleteQuartieralpage(quartieralpage.id)">Supprimer</button>
            </li>
        </ul>
        <MapList geoObjectName="quartieralpage" :style=quartieralpageStyle popupRoute="QuartieralpageView" />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import MapList from './MapList.vue';

import config from '../../config';

const quartieralpages = ref([]);
const router = useRouter();

const quartieralpageStyle = ref({
    fillColor: 'green',
    weight: 2,
    opacity: 1,
    color: 'red',
    dashArray: '2, 10',
    fillOpacity: 0.3
});

const fetchQuartieralpages = () => {
    axios.get(`${config.API_BASE_URL}/api/quartierAlpage/`)
        .then(response => {
            quartieralpages.value = response.data;
            console.log("list response data:", response.data);
            console.log("quartieralpages.value:", quartieralpages.value);
        })
        .catch(error => {
            console.error('There was an error!', error);
        });
};

const goToAddPage = () => {
    router.push('/add');
};

const editQuartieralpage = (id) => {
    router.push(`/edit/${id}`);
};

const deleteQuartieralpage = (id) => {
    axios.delete(`${config.API_BASE_URL}/api/quartierAlpage/${id}/`)
        .then(response => {
            fetchQuartieralpages();
        })
        .catch(error => {
            console.error('There was an error!', error);
        });
};

onMounted(fetchQuartieralpages);
</script>

<style scoped>
/* Ajoutez vos styles ici */
</style>
