<template>
  <CrudListPage
    title="Subventions"
    modelName="subventionpnv"
    apiRouteName="subventionPNV"
    itemLabel="une subvention"
    idField="id_subvention"
    :columns="columns"
    :bgColor="'#d4652f'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from '../../components/crud/CrudListPage.vue';

const columns = [
  { field: "exploitant_detail.nom_exploitant", label: "Bénéficiaire", sortable: true },
  { field: "description",                      label: "Description",  sortable: true },
  { field: "montant",                          label: "Montant",      sortable: true },
  { field: "engage",                           label: "Engagé",       sortable: true },
  { field: "paye",                             label: "Payé",         sortable: true },
];
const searchFields = ['description', 'exploitant_detail.nom_exploitant'];
</script>
