<template>
  <CrudList2
    title="Races"
    modelName="race"
    apiRouteName="race"
    itemLabel="une race"
    idField="id_race"
    :columns="columns"
    :formComponent="RaceForm2"
    :bgColor="'#808080'"
    :searchFields="searchFields"
    :filters="raceFilters"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue';
import auth from '../../auth';
import config from '../../config';
import RaceForm2 from './RaceForm2.vue';
import CrudListPaginated from './CrudListPaginated.vue';
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "description", label: "Race", sortable: true },
  { field: "espece_description", label: "Espèce", sortable: true },
];

const searchFields = [
  'description',
  'espece_description',
];

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
  } catch (error) {
    console.error('Erreur lors du chargement des espèces pour le filtre', error);
  }
});

</script>