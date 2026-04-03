<template>
  <CrudList2
    title="Catégories d'animaux"
    modelName="categorie_animaux"
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
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
];

const searchFields = [
  'description',
];

</script>