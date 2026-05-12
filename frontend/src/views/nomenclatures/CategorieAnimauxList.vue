<template>
  <CrudListPage
    title="Catégories d'animaux"
    modelName="categorieanimaux"
    apiRouteName="categorie_animaux"
    itemLabel="une catégorie d'animaux"
    idField="id_categorie_animaux"
    :columns="columns"
    :bgColor="'#808080'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from "../../components/crud/CrudListPage.vue";

const columns = [{ field: "description", label: "Description", sortable: true }];
const searchFields = ["description"];
</script>
