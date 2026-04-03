<template>
  <CrudList2
    title="Commodités"
    modelName="commodite"
    apiRouteName="commodite"
    itemLabel="une commodité"
    idField="id_commodite"
    :columns="columns"
    :formComponent="CommoditeForm2"
    :bgColor="'#154889'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CommoditeForm2 from './CommoditeForm2.vue';
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
];

const searchFields = [
  'description'
];

</script>
