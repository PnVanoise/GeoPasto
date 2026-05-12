<template>
  <CrudListPage
    title="Types de convention"
    modelName="typeconvention"
    apiRouteName="typeConvention"
    itemLabel="un type de convention"
    idField="id_type_convention"
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
