<template>
  <CrudList2
    title="Subventions"
    modelName="subventionpnv"
    apiRouteName="subventionPNV"
    itemLabel="une subvention"
    idField="id_subvention"
    :columns="columns"
    :formComponent="SubventionForm2"
    :bgColor="'#d4652f'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import SubventionForm2 from './SubventionForm2.vue';
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "exploitant_detail.nom_exploitant", label: "Bénéficiaire", sortable: true },
  { field: "description", label: "Description", sortable: true },
  { field: "montant", label: "Montant", sortable: true },
  { field: "engage", label: "Engagé", sortable: true },
  { field: "paye", label: "Payé", sortable: true },
];

const searchFields = [
  'description',
  'exploitant_detail.nom_exploitant',
];

</script>
