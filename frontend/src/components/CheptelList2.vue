<template>
  <CrudList2
    title="Cheptels"
    modelName="cheptel"
    apiRouteName="cheptel"
    itemLabel="un cheptel"
    idField="id_cheptel"
    :columns="columns"
    :formComponent="CheptelForm2"
    :bgColor="'#d4652f'"
    :searchFields="searchFields"
    :filters="cheptelFilters"
  />
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import auth from '../../auth';
import CheptelForm2 from './CheptelForm2.vue';
import CrudList2 from './CrudList2.vue';

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
  'annee'
];

const upOptions = ref([]);

// Filtres : année courante et UP
const cheptelFilters = ref([
  {
    key: "annee_courante",
    type: "checkbox",
    label: `Année courante (${new Date().getFullYear()})`,
    default: false,
    apply: (rows, value) => !value ? rows : rows.filter(r => r.annee === new Date().getFullYear())
  },
  {
    key: "up",
    type: "select",
    label: "Unité pastorale",
    options: upOptions,
    default: "",
    apply: (rows, value) => !value ? rows : rows.filter(r =>
      r.situation_detail?.unite_pastorale_detail?.id_unite_pastorale == Number(value)
    )
  }
]);

// Chargement des unités pastorales depuis l'API
onMounted(async () => {
  const r = await auth.axiosInstance.get("/unitePastorale/light/");
  upOptions.value = r.data.map(f => ({
    label: f.nom_up,
    value: f.id_unite_pastorale
  }));
});

// Watch : dès que upOptions est chargé, initialise la valeur du filtre UP
watch(upOptions, (newVal) => {
  if (newVal.length && cheptelFilters.value.find(f => f.key === 'up')) {
    cheptelFilters.value.find(f => f.key === 'up').default = "";
  }
});
</script>
