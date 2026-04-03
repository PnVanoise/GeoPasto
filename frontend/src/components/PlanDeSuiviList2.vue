<template>
  <CrudList2
    title="Plans de suivi"
    modelName="plandesuivi"
    apiRouteName="planSuivi"
    itemLabel="un plan de suivi"
    idField="id_plan_suivi"
    :columns="columns"
    :formComponent="PlanDeSuiviForm2"
    :bgColor="'#f7ba0b'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import PlanDeSuiviForm2 from './PlanDeSuiviForm2.vue';
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
  { field: "unite_pastorale_detail.nom_up", label: "UP", sortable: true },
  { field: "date_debut", label: "Début", sortable: true },
  { field: "date_fin", label: "Fin", sortable: true },
];

const searchFields = [
  'description',  
];

</script>


