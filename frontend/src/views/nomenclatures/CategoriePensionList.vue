<template>
  <CrudListPage
    title="Catégories de pension"
    modelName="categoriepension"
    apiRouteName="categorie_pension"
    itemLabel="une catégorie de pension"
    idField="id_categorie_pension"
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
