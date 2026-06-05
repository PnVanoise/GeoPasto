<template>
  <CrudListPage
    title="Mesures de plan"
    modelName="mesuredeplan"
    apiRouteName="mesurePlan"
    itemLabel="une mesure de plan"
    idField="id_mesure_plan"
    :columns="columns"
    :bgColor="'#f7ba0b'"
    :geojsonMode="true"
    :searchFields="searchFields"
    :filters="filters"
  />
</template>

<script setup>
import { ref, onMounted } from "vue";
import CrudListPage from "../../components/crud/CrudListPage.vue";
import auth from "@/services/axios";

const columns = [
  { field: "description", label: "Description", sortable: true },
  { field: "type_mesure_detail.description", label: "Type de mesure", sortable: true },
  { field: "unite_pastorale_detail.nom_up", label: "UP", sortable: true },
  { field: "obligation", label: "Obligation", sortable: true },
  { field: "date_debut_validite", label: "Début validité", sortable: true },
  { field: "date_fin_validite", label: "Fin validité", sortable: true },
];
const searchFields = [
  "description",
  "type_mesure_detail.description",
  "unite_pastorale_detail.nom_up",
];

const upOptions = ref([]);
const enjeuxOptions = ref([]);

const filters = ref([
  {
    key: "up",
    type: "select",
    label: "UP",
    options: upOptions,
    default: "",
    apply: (rows, value) =>
      !value
        ? rows
        : rows.filter((r) => r.unite_pastorale_detail?.id_unite_pastorale == Number(value)),
  },
  {
    key: "enjeux",
    type: "multiselect",
    label: "Enjeux",
    options: enjeuxOptions,
    default: [],
    apply: (rows, values) =>
      !values?.length
        ? rows
        : rows.filter((r) => values.some((v) => r.enjeux?.some((e) => e.id === Number(v)))),
  },
  {
    key: "date",
    type: "date",
    label: "Date dans la période",
    default: null,
    apply: (rows, value) => {
      if (!value) return rows;
      const d = new Date(value);
      return rows.filter((r) => {
        const debut = r.date_debut_validite ? new Date(r.date_debut_validite) : null;
        const fin = r.date_fin_validite ? new Date(r.date_fin_validite) : null;
        if (debut && d < debut) return false;
        if (fin && d > fin) return false;
        return true;
      });
    },
  },
]);

onMounted(async () => {
  const [upRes, enjeuRes] = await Promise.all([
    auth.axiosInstance.get("/unitePastorale/light/"),
    auth.axiosInstance.get("/enjeu/"),
  ]);
  upOptions.value = upRes.data.map((u) => ({
    label: u.nom_up,
    value: u.id_unite_pastorale,
  }));
  enjeuxOptions.value = enjeuRes.data.map((e) => ({
    label: e.description,
    value: e.id_enjeu,
  }));
});
</script>
