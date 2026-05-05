<template>
  <CrudListPage
    title="Eleveurs"
    modelName="eleveur"
    apiRouteName="eleveur"
    itemLabel="un eleveur"
    idField="id_eleveur"
    :columns="columns"
    :bgColor="'#d5642f'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from '../../components/crud/CrudListPage.vue';

const columns = [
  { field: "nom_eleveur",    label: "Nom",    sortable: true },
  { field: "prenom_eleveur", label: "Prénom", sortable: true },
];

const searchFields = ['nom_eleveur', 'prenom_eleveur'];
</script>
