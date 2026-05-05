<template>
  <CrudListPage
    title="Cheptels"
    modelName="cheptel"
    apiRouteName="cheptel"
    itemLabel="un cheptel"
    idField="id_cheptel"
    :columns="columns"
    :bgColor="'#d4652f'"
    :searchFields="searchFields"
    :filters="cheptelFilters"
  />
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import CrudListPage from '../../components/crud/CrudListPage.vue';
import auth from '@/services/axios';

const columns = [
  { field: "eleveur_detail.nom_complet", label: "Éleveur", sortable: true },
  { field: "situation_detail.unite_pastorale_detail.nom_up", label: "UP", sortable: true },
  { field: "annee", label: "Année", sortable: true },
  { field: "type_cheptel_detail.description", label: "Type cheptel", sortable: true },
  { field: "nombre_animaux", label: "Nombre d'animaux", sortable: true },
];

const searchFields = [
  'eleveur_detail.nom_complet',
  'situation_detail.unite_pastorale_detail.nom_up',
  'type_cheptel_detail.description',
  'nombre_animaux',
  'annee',
];

const upOptions = ref([]);

const cheptelFilters = ref([
  {
    key: "annee_courante",
    type: "checkbox",
    label: `Année courante (${new Date().getFullYear()})`,
    default: false,
    apply: (rows, value) => !value ? rows : rows.filter(r => r.annee === new Date().getFullYear()),
  },
  {
    key: "up",
    type: "select",
    label: "Unité pastorale",
    options: upOptions,
    default: "",
    apply: (rows, value) => !value ? rows : rows.filter(r =>
      r.situation_detail?.unite_pastorale_detail?.id_unite_pastorale == Number(value)
    ),
  },
]);

onMounted(async () => {
  const r = await auth.axiosInstance.get("/unitePastorale/light/");
  upOptions.value = r.data.map(f => ({ label: f.nom_up, value: f.id_unite_pastorale }));
});
</script>
