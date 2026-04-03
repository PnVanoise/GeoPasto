<template>
  <CrudList2
    title="Productions"
    modelName="production"
    apiRouteName="production"
    itemLabel="une production"
    idField="id_production"
    :columns="columns"
    :formComponent="ProductionForm2"
    :bgColor="'#808080'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import ProductionForm2 from './ProductionForm2.vue';
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
];

const searchFields = [
  'description',
];

</script>