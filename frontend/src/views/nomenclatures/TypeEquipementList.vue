<template>
  <CrudListPage
    title="Types d'équipements"
    modelName="typeequipement"
    apiRouteName="typeEquipement"
    itemLabel="un type d'équipement"
    idField="id_type_equipement"
    :columns="columns"
    :bgColor="'#808080'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from '../../components/crud/CrudListPage.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
  { field: "categorie",   label: "Catégorie",   sortable: true },
];
const searchFields = ['description', 'categorie'];
</script>