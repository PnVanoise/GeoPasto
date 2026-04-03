<template>
  <CrudList2
    title="Mesures de plan"
    modelName="mesuredeplan"
    apiRouteName="mesurePlan"
    itemLabel="une mesure de plan"
    idField="id_mesure_plan"
    :columns="columns"
    :formComponent="MesureDePlanForm2"
    :bgColor="'#f7ba0b'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import MesureDePlanForm2 from './MesureDePlanForm2.vue';
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
  { field: "type_mesure_detail.description", label: "Type de mesure", sortable: true },
  { field: "unite_pastorale_detail.nom_up", label: "UP", sortable: true },
  { field: "debut_periode", label: "Début", sortable: true },
  { field: "fin_periode", label: "Fin", sortable: true },
];

const searchFields = [
  'description',
  'type_mesure_detail.description',
  'unite_pastorale_detail.nom_up'
];

</script>

