<template>
  <CrudListPage
    title="Abris d'urgence"
    modelName="abriurgence"
    apiRouteName="abriDUrgence"
    itemLabel="un abri d'urgence"
    idField="id_abri_urgence"
    :columns="columns"
    :bgColor="'#154889'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from '../../components/crud/CrudListPage.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
  { field: "etat",        label: "État",         sortable: true },
];
const searchFields = ['description', 'etat'];
</script>
