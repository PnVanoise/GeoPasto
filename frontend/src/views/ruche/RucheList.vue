<template>
  <CrudListPage
    title="Ruches"
    modelName="ruche"
    apiRouteName="ruche"
    :geojsonMode="true"
    itemLabel="une ruche"
    idField="id"
    :columns="columns"
    :bgColor="'#9b2423'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from '../../components/crud/CrudListPage.vue';

const columns = [
  { field: "description",          label: "Description",    sortable: true },
  { field: "situation_exploitation", label: "Situation (id)", sortable: true },
];
const searchFields = ['description'];
</script>