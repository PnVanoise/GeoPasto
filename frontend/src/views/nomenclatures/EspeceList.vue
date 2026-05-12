<template>
  <CrudListPage
    title="Espèces"
    modelName="espece"
    apiRouteName="espece"
    itemLabel="une espèce"
    idField="id_espece"
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
