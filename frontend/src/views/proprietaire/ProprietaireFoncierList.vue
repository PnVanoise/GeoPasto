<template>
  <CrudListPage
    title="Propriétaires fonciers"
    modelName="proprietairefoncier"
    apiRouteName="proprietaireFoncier"
    itemLabel="un propriétaire foncier"
    idField="id_proprietaire"
    :columns="columns"
    :bgColor="'#808080'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from '../../components/crud/CrudListPage.vue';

const columns = [
  { field: "nom_propr",    label: "Nom",    sortable: true },
  { field: "prenom_propr", label: "Prénom", sortable: true },
];

const searchFields = ['nom_propr', 'prenom_propr'];
</script>
