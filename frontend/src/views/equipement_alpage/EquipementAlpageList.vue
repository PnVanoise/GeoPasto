<template>
  <CrudListPage
    title="Équipements alpage"
    modelName="equipementalpage"
    apiRouteName="equipementAlpage"
    itemLabel="un équipement alpage"
    idField="id_equipement_alpage"
    :geojsonMode="true"
    :columns="columns"
    :bgColor="'#9b2423'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from '../../components/crud/CrudListPage.vue';

const columns = [
  { field: "description",                    label: "Description", sortable: true },
  { field: "etat",                           label: "État",        sortable: true },
  { field: "type_equipement_detail.description", label: "Type",   sortable: true },
];

const searchFields = ['description', 'etat'];
</script>
