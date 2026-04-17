<template>
  <CrudList2
    title="Types de cheptel"
    modelName="type_cheptel"
    apiRouteName="type_cheptel"
    itemLabel="un type de cheptel"
    idField="id_type_cheptel"
    :columns="columns"
    :formComponent="TypeCheptelForm2"
    :bgColor="'#808080'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import TypeCheptelForm2 from './TypeCheptelForm2.vue';
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
  { field: "coefficient_UGB", label: "Coeff. UGB", sortable: true },
];

const searchFields = [
  'description',
  'coefficient_UGB'
];

</script>
