<template>
  <CrudListPage
    title="Types de cheptel"
    modelName="typecheptel"
    apiRouteName="type_cheptel"
    itemLabel="un type de cheptel"
    idField="id_type_cheptel"
    :columns="columns"
    :bgColor="'#808080'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from '@/components/CrudListPage.vue';

const columns = [
  { field: "description",     label: "Description",  sortable: true },
  { field: "coefficient_UGB", label: "Coeff. UGB",   sortable: true },
];

const searchFields = ['description', 'coefficient_UGB'];
</script>
