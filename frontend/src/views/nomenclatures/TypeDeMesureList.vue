<template>
  <CrudListPage
    title="Types de mesure"
    modelName="typedemesure"
    apiRouteName="typeMesure"
    itemLabel="un type de mesure"
    idField="id_type_mesure"
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
