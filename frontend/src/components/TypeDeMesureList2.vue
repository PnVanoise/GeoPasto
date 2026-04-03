<template>
  <CrudList2
    title="Types de mesure"
    modelName="typedemesure"
    apiRouteName="typeMesure"
    itemLabel="un type de mesure"
    idField="id_type_mesure"
    :columns="columns"
    :formComponent="TypeDeMesureForm2"
    :bgColor="'#808080'"
  />
</template>

<script setup>
import TypeDeMesureForm2 from './TypeDeMesureForm2.vue';
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
];

</script>
