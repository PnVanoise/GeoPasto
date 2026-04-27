<template>
  <CrudListPage
    title="Quartiers pastoraux"
    modelName="quartierpasto"
    apiRouteName="quartierPasto"
    itemLabel="un quartier"
    idField="id_quartier"
    :geojsonMode="true"
    :columns="columns"
    :bgColor="'#4a7c59'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from '@/components/CrudListPage.vue';

const columns = [
  { field: "code_quartier", label: "Code", sortable: true },
  { field: "nom_quartier", label: "Nom", sortable: true },
];

const searchFields = ['code_quartier', 'nom_quartier'];
</script>
