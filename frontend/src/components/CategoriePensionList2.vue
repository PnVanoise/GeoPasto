<template>
  <CrudList2
    title="Catégories de pension"
    modelName="categorie_pension"
    apiRouteName="categorie_pension"
    itemLabel="une catégorie de pension"
    idField="id_categorie_pension"
    :columns="columns"
    :formComponent="CategoriePensionForm2"
    :bgColor="'#808080'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CategoriePensionForm2 from './CategoriePensionForm2.vue';
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
];

const searchFields = [
  'description',
];

</script>