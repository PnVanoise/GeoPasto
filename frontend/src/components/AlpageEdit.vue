<template>
  <div>
    <h1>Éditer un alpage (quartierUP)</h1>
    <AlpageForm :initialForm="form" :isEdit="true" :onSubmit="submitForm" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import axios from "axios";
import AlpageForm from "./AlpageForm.vue";

import config from "../../config";

const form = ref({
  properties: {
    quartier_code: "",
    surface: "",
    up_code: "",
    up_nom_1: "",
    up_nom_2: "",
    quartier_code_court: "",
    quartier_nom: "",
  },
  geometry: {
    type: "MultiPolygon",
    coordinates: [],
  },
});

const route = useRoute();
const id = route.params.id;

const router = useRouter();

const fetchAlpage = () => {
  axios
    .get(`${config.API_BASE_URL}/api/quartierUP/${id}/`)
    .then((response) => {
      console.log("response data : ", response.data);
      form.value = response.data;
      console.log("form properties : ", form.value.properties);
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

const submitForm = (formData) => {
  console.warn("submitForm formData : ", formData);
  return axios.put(`${config.API_BASE_URL}/api/quartierUP/${id}/`, formData);
  // axios
  //   .put(`http://151.80.250.138/api/logement/${id}/`, formData)
  //   .then((response) => {
  //     router.push("/");
  //   })
  //   .catch((error) => {
  //     console.error("There was an error!", error);
  //   });
};

onMounted(fetchAlpage);
</script>

<style scoped>
/* Ajoutez vos styles ici */
</style>
