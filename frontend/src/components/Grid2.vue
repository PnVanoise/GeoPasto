<script setup>
import { ref, computed } from "vue";

const props = defineProps({
  data: {
    type: Array,
    default: () => [],
  },
  columns: Array,
  columnLabels: Object,
  actions: {
    type: Object,
    default: () => ({
      view: true,
      edit: true,
      delete: true,
    }),
  },
  idField: {
    type: String,
    default: "id",
  },
  filterKey: String,
  bgColor: String,
});

const emit = defineEmits(["edit", "delete", "view"]);

const sortKey = ref("");
const sortOrders = ref(
  props.columns.reduce((o, key) => ((o[key] = 1), o), {})
);

const filteredData = computed(() => {
  let { data, filterKey } = props;
  if (filterKey) {
    const q = filterKey.toLowerCase();
    data = data.filter((row) =>
      Object.keys(row).some((key) =>
        String(row[key]).toLowerCase().includes(q)
      )
    );
  }
  if (sortKey.value) {
    const order = sortOrders.value[sortKey.value];
    data = [...data].sort((a, b) => {
      a = a[sortKey.value];
      b = b[sortKey.value];
      return (a === b ? 0 : a > b ? 1 : -1) * order;
    });
  }
  return data;
});

function sortBy(key) {
  sortKey.value = key;
  sortOrders.value[key] *= -1;
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// Renvoie la vraie valeur de l'id
const getItemId = (item) => item[props.idField];

const showDeleteModal = ref(false);
const entryToDelete = ref(null);

function confirmDelete(entry) {
  entryToDelete.value = entry;
  showDeleteModal.value = true;
}

function cancelDelete() {
  entryToDelete.value = null;
  showDeleteModal.value = false;
}

function performDelete() {
  console.log("performdelete entry : ", entryToDelete.value);
  if (entryToDelete.value) {
    emit("delete", entryToDelete.value);
    cancelDelete();
  }
}
</script>

<template>
  <div class="liste-container">
    <table
      v-if="filteredData.length"
      :style="{ borderColor: bgColor }"
      class="table-with-fixed-header"
    >
      <thead>
        <tr>
          <th
            v-for="key in columns"
            :key="key"
            @click="sortBy(key)"
            :class="{ active: sortKey === key }"
            :style="{ backgroundColor: bgColor }"
          >
            {{ columnLabels[key] || capitalize(key) }}
            <span class="arrow" :class="sortOrders[key] > 0 ? 'asc' : 'dsc'"></span>
          </th>
          <th :style="{ backgroundColor: bgColor }">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="entry in filteredData" :key="getItemId(entry)">
          <td v-for="key in columns" :key="key">
            <template v-if="typeof entry[key] === 'boolean'">
              <input type="checkbox" :checked="entry[key]" disabled />
            </template>
            <template v-else>{{ entry[key] }}</template>
          </td>
          <td>
            <template v-if="actions.view">
              <font-awesome-icon
                icon="eye"
                class="icon-view"
                title="Voir les détails"
                @click="$emit('view', entry)"
              />
            </template>

            <template v-if="actions.edit">
              <font-awesome-icon
                icon="edit"
                class="icon-edit"
                title="Modifier"
                @click="$emit('edit', entry)"
              />
            </template>

            <template v-if="actions.delete">
              <font-awesome-icon
                icon="trash"
                class="icon-delete"
                title="Supprimer"
                @click="confirmDelete(entry)"
              />
            </template>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-else>Aucun résultat.</p>
  </div>

  <!-- Modal suppression -->
  <div v-if="showDeleteModal" class="modal-overlay">
    <div class="modal-content">
      <h3>Confirmer la suppression</h3>
      <p>Êtes-vous sûr de vouloir supprimer cet enregistrement ?</p>
      <div class="modal-actions">
        <button @click="performDelete" class="modal-confirm">Oui, supprimer</button>
        <button @click="cancelDelete" class="modal-cancel">Annuler</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.icon-view {
  cursor: pointer;
  margin-right: 10px;
  font-size: 1.2em;
  color: #2ecc71;
}
.icon-view:hover {
  color: #27ae60;
}
.icon-edit {
  cursor: pointer;
  margin-right: 10px;
  font-size: 1.2em;
  color: #3498db;
}
.icon-edit:hover {
  color: #2980b9;
}
.icon-delete {
  cursor: pointer;
  margin-right: 10px;
  font-size: 1.2em;
  color: #e74c3c;
}
.icon-delete:hover {
  color: #c0392b;
}

.liste-container {
  max-height: 550px;
  overflow-y: auto;
  border: 1px solid #ccc;
}

.table-with-fixed-header {
  width: 100%;
  border-collapse: collapse;
}

.table-with-fixed-header thead {
  position: sticky;
  top: 0;
  z-index: 2;
  background-color: #42b983;
}

.table-with-fixed-header th,
.table-with-fixed-header td {
  min-width: 120px;
  padding: 10px 20px;
  text-align: left;
}

th.active {
  color: #fff;
}

.arrow {
  display: inline-block;
  vertical-align: middle;
  width: 0;
  height: 0;
  margin-left: 5px;
  opacity: 0.66;
}
.arrow.asc {
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-bottom: 4px solid #fff;
}
.arrow.dsc {
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 4px solid #fff;
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  min-width: 300px;
  text-align: center;
}

.modal-actions {
  margin-top: 20px;
  display: flex;
  justify-content: space-around;
}

.modal-confirm {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 8px 16px;
  cursor: pointer;
}

.modal-cancel {
  background-color: #bdc3c7;
  border: none;
  padding: 8px 16px;
  cursor: pointer;
}
</style>
