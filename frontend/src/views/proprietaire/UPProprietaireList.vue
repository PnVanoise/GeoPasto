<template>
  <CrudListPage
    title="UP / Propriétaires"
    modelName="upproprietaire"
    apiRouteName="proprietaireUP"
    itemLabel="un lien UP / Propriétaire"
    idField="id_proprietaire_up"
    :columns="columns"
    :bgColor="'#f7ba0b'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from '../../components/crud/CrudListPage.vue';

const columns = [
  { field: "up_nom",          label: "Unité pastorale", sortable: true },
  { field: "proprietaire_nom", label: "Propriétaire",   sortable: true },
];
const searchFields = ['up_nom', 'proprietaire_nom'];
</script>
