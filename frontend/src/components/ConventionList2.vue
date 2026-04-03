<template>
  <CrudList2
    title="Conventions d'exploitation"
    modelName="conventiondexploitation"
    apiRouteName="conventionExploitation"
    :geojsonMode="true"
    itemLabel="une convention"
    idField="id"
    :columns="columns"
    :formComponent="ConventionForm2"
    :bgColor="'#154889'"
  />
</template>

<script setup>
import ConventionForm2 from './ConventionForm2.vue';
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "exploitant_nom", label: "Exploitant", sortable: true },
  { field: "up_nom", label: "UP", sortable: true },
  { field: "type_convention_detail.description", label: "Type de convention", sortable: true },
];

</script>