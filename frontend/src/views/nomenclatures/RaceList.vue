<template>
  <CrudListPage
    title="Races"
    modelName="race"
    apiRouteName="race"
    itemLabel="une race"
    idField="id_race"
    :columns="columns"
    :bgColor="'#808080'"
    :searchFields="searchFields"
    :filters="raceFilters"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue';
import CrudListPage from '../../components/crud/CrudListPage.vue';
import auth from '@/services/axios';
import config from '@/../config';

const columns    = [
  { field: "description",       label: "Race",   sortable: true },
  { field: "espece_description", label: "Espèce", sortable: true },
];
const searchFields = ['description', 'espece_description'];

const especeOptions = ref([]);

const raceFilters = ref([
  {
    key: 'espece',
    type: 'select',
    label: 'Espèce',
    options: especeOptions,
    default: '',
    apply: (rows, value) => !value ? rows : rows.filter((r) => Number(r.espece) === Number(value)),
  },
]);

onMounted(async () => {
  try {
    const response = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/espece/`);
    especeOptions.value = (response.data || []).map((e) => ({
      label: e.description,
      value: e.id_espece,
    }));
  } catch (e) {
    console.error('Erreur lors du chargement des espèces pour le filtre', e);
  }
});
</script>