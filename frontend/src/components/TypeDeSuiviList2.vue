<template>
  <CrudList2
    title="Types de suivi"
    modelName="typedesuivi"
    apiRouteName="typeSuivi"
    itemLabel="un type de suivi"
    idField="id_type_suivi"
    :columns="columns"
    :formComponent="TypeDeSuiviForm2"
    :bgColor="'#808080'"
  />
</template>

<script setup>
import TypeDeSuiviForm2 from './TypeDeSuiviForm2.vue';
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
];

</script>
