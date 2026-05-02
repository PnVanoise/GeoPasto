<template>
  <CrudList2
    title="Ruches"
    modelName="ruche"
    apiRouteName="ruche"
    :geojsonMode="true"
    itemLabel="une ruche"
    idField="id"
    :columns="columns"
    :formComponent="RucheForm2"
    :bgColor="'#9b2423'"
  />
</template>

<script setup>
import RucheForm2 from './RucheForm2.vue';
import CrudList2 from '../../components/crud/CrudList2.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
  { field: "situation_exploitation", label: "Situation (id)", sortable: true },
];
</script>
