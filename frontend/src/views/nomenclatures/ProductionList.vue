<template>
  <CrudListPage
    title="Productions"
    modelName="production"
    apiRouteName="production"
    itemLabel="une production"
    idField="id_production"
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