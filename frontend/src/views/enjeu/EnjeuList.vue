<template>
  <CrudListPage
    title="Enjeux"
    modelName="enjeu"
    apiRouteName="enjeu"
    itemLabel="un enjeu"
    idField="id_enjeu"
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
