<template>
  <CrudListPage
    title="Types de suivi"
    modelName="typedesuivi"
    apiRouteName="typeSuivi"
    itemLabel="un type de suivi"
    idField="id_type_suivi"
    :columns="columns"
    :bgColor="'#808080'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from '../../components/crud/CrudListPage.vue';

const columns    = [{ field: "description", label: "Description", sortable: true }];
const searchFields = ['description'];
</script>