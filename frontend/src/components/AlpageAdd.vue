<template>
    <div>
        <h1>Ajouter un alpage (quartierUP)</h1>
        <AlpageForm :initialForm="form" :isEdit="false" :onSubmit="submitForm" />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
// import { useRouter } from 'vue-router';
import axios from 'axios';
import AlpageForm from './AlpageForm.vue';
import config from '../../config';

const form = ref({
    quartier_code: '',
    surface: '',
    up_code: '',
    up_nom_1: '',
    up_nom_2: '',
    quartier_code_court: '',
    quartier_nom: '',
});

const submitForm = (formData) => {
    return axios.post(`${config.API_BASE_URL}/api/quartierUP/`, formData);
};



</script>

<style scoped>
/* Ajoutez vos styles ici */
</style>