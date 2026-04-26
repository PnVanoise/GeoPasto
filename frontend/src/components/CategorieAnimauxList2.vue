<template>
  <CrudListPaginated
    title="Catégories d'animaux"
    modelName="categorieanimaux"
    apiRouteName="categorie_animaux"
    itemLabel="une catégorie d'animaux"
    idField="id_categorie_animaux"
    :columns="columns"
    :formComponent="CategorieAnimauxForm2"
    :bgColor="'#808080'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CategorieAnimauxForm2 from './CategorieAnimauxForm2.vue';
import CrudListPaginated from './CrudListPaginated.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
];

const searchFields = [
  'description',
];

</script>