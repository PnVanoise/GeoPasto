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
  />
</template>

<script setup>
import RaceForm2 from './RaceForm2.vue';
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
];

const searchFields = [
  'description',
];

</script>