<template>
  <CrudList2
    title="Types de convention"
    modelName="typeconvention"
    apiRouteName="typeConvention"
    itemLabel="un type de convention"
    idField="id_type_convention"
    :columns="columns"
    :formComponent="TypeDeConventionForm2"
    :bgColor="'#808080'"
  />
</template>

<script setup>
import TypeDeConventionForm2 from './TypeDeConventionForm2.vue';
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
];

</script>