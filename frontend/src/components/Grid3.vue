<script setup>
import { ref, computed } from "vue";

const props = defineProps({
  data: {
    type: Array,
    default: () => [],
  },
  columns: {
    type: Array,
    required: true,
  },
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
  bgColor: String,
  showActions: {
    type: Boolean,
    default: true,
  },
});

const emit = defineEmits(["edit", "delete", "view", "export-all"]);

// Sorting state (unifié)
const sortField = ref(null);
const sortDirection = ref("asc");

// Computed that applies filter (search) then sorting, used by the template
const displayedData = computed(() => {
  let data = (props.data || []).slice();

  // Tri des données
  if (sortField.value) {
    const field = sortField.value;
    data.sort((a, b) => {
      const valA = nestedValue(a, field);
      const valB = nestedValue(b, field);

      if (valA == null) return 1;
      if (valB == null) return -1;

      if (typeof valA === "number" && typeof valB === "number") {
        return sortDirection.value === "asc" ? valA - valB : valB - valA;
      }

      return sortDirection.value === "asc"
        ? String(valA).localeCompare(String(valB))
        : String(valB).localeCompare(String(valA));
    });
  }

  return data;
});

function nestedValue(obj, path) {
  return String(path || "").split('.').reduce((o, key) => (o ? o[key] : null), obj);
}

function isDateField(fieldPath) {
  return /(^|\.)date(_|$)/i.test(String(fieldPath || ""));
}

function toFrDate(value) {
  if (value == null || value === "") return "";

  if (value instanceof Date && !Number.isNaN(value.getTime())) {
    const dd = String(value.getDate()).padStart(2, "0");
    const mm = String(value.getMonth() + 1).padStart(2, "0");
    const yyyy = String(value.getFullYear());
    return `${dd}/${mm}/${yyyy}`;
  }

  const raw = String(value);
  const isoDateMatch = raw.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (isoDateMatch) {
    return `${isoDateMatch[3]}/${isoDateMatch[2]}/${isoDateMatch[1]}`;
  }

  const isoDateTimeMatch = raw.match(/^(\d{4})-(\d{2})-(\d{2})T/);
  if (isoDateTimeMatch) {
    return `${isoDateTimeMatch[3]}/${isoDateTimeMatch[2]}/${isoDateTimeMatch[1]}`;
  }

  return raw;
}

function isBooleanCell(entry, col) {
  return typeof nestedValue(entry, col.field) === "boolean";
}

function formatCellValue(entry, col) {
  const value = nestedValue(entry, col.field);
  if (value == null) return "";

  if (col?.format === "date" || col?.type === "date" || isDateField(col?.field)) {
    return toFrDate(value);
  }

  return value;
}

function toggleSort(col) {
  if (!col || !col.sortable) return;

  if (sortField.value === col.field) {
    sortDirection.value = sortDirection.value === "asc" ? "desc" : "asc";
  } else {
    sortField.value = col.field;
    sortDirection.value = "asc";
  }
}

// Renvoie la vraie valeur de l'id
const getItemId = (item) => item[props.idField];

// Export CSV helper
function exportToCsv(rows, filename = "export.csv") {
  if (!rows || !rows.length) {
    const blob = new Blob([""], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    return;
  }

  const headerFields = (props.columns || []).map((c) => c.label || c.field);
  const fields = (props.columns || []).map((c) => c.field);

  const escape = (value) => {
    if (value == null) return "";
    const s = String(value).replace(/\"/g, '\"\"');
    return `\"${s}\"`;
  };

  const lines = [];
  lines.push(headerFields.map((h) => escape(h)).join(","));

  for (const r of rows) {
    const row = fields.map((f) => {
      const v = nestedValue(r, f);
      return escape(v);
    });
    lines.push(row.join(","));
  }

  const csv = lines.join("\r\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function exportAll() {
  // Let the parent perform the full export using its authoritative source
  emit("export-all");
}

function exportVisible() {
  exportToCsv(displayedData.value || [], "export_visible.csv");
}

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
  if (entryToDelete.value) {
    emit("delete", entryToDelete.value);
    cancelDelete();
  }
}
</script>

<template>
  <div v-if="props.showActions" class="grid-actions">
    <v-btn
      class="ma-2 compact"
        color="success"
        icon="mdi-file"
        @click="exportAll"
        v-tooltip="'Export csv de toutes les données'"></v-btn>
    <v-btn
      class="ma-2 compact"
        color="success"
        icon="mdi-file-outline"
        @click="exportVisible"
        v-tooltip="'Export csv des données visibles'"></v-btn>
    <!-- <button type="button" class="export-btn" @click="exportAll">Exporter — Toutes les données</button>
    <button type="button" class="export-btn" @click="exportVisible">Exporter — Données visibles</button> -->
  </div>

  <div class="liste-container">
    <table
      v-if="displayedData.length"
      :style="{ borderColor: bgColor }"
      class="table-with-fixed-header"
    >
      <thead>
        <tr>
          <th
            v-for="col in columns"
            :key="col.field"
            @click="toggleSort(col)"
            @keydown.enter="toggleSort(col)"
            @keydown.space.prevent="toggleSort(col)"
            role="button"
            tabindex="0"
            :aria-sort="sortField === col.field ? (sortDirection === 'asc' ? 'ascending' : 'descending') : 'none'"
            :class="{ sortable: col.sortable, active: sortField === col.field }"
            :style="{ backgroundColor: bgColor }"
          >
            {{ col.label }}
            <span class="arrow" :class="sortField === col.field ? (sortDirection === 'asc' ? 'asc' : 'dsc') : ''"></span>
          </th>
          <th class="actions-col" :style="{ backgroundColor: bgColor }">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="entry in displayedData" :key="getItemId(entry)">
          <td v-for="col in columns" :key="col.field">
            <template v-if="isBooleanCell(entry, col)">
              <input type="checkbox" :checked="nestedValue(entry, col.field)" disabled />
            </template>
            <template v-else>
              {{ formatCellValue(entry, col) }}
            </template>
          </td>
          <td class="actions-col">
            <div class="actions-cell-inner">
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
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-else>Aucun résultat.</p>
  </div>

  <!-- Modal suppression -->
  <Teleport to="body">
    <div v-if="showDeleteModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Confirmer la suppression</h3>
        <p>Êtes-vous sûr de vouloir supprimer cet enregistrement ?</p>
        <div class="modal-actions">
          <button type="button" @click="performDelete" class="modal-confirm">Oui, supprimer</button>
          <button type="button" @click="cancelDelete" class="modal-cancel">Annuler</button>
        </div>
      </div>
    </div>
  </Teleport>
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
  padding: 3px 8px;
  text-align: left;
}

.table-with-fixed-header th.actions-col,
.table-with-fixed-header td.actions-col {
  width: 1%;
  min-width: 1%;
  white-space: nowrap;
  text-align: right;
}

.table-with-fixed-header td.actions-col {
  padding-right: 0;
}

.table-with-fixed-header td.actions-col .actions-cell-inner {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
}

.table-with-fixed-header td.actions-col .icon-view,
.table-with-fixed-header td.actions-col .icon-edit,
.table-with-fixed-header td.actions-col .icon-delete {
  margin-right: 0;
}

th.active {
  color: #fff;
  background-color: rgba(0,0,0,0.08);
  font-weight: 700;
}

.table-with-fixed-header th:focus {
  outline: 2px solid rgba(66,185,131,0.6);
  outline-offset: 2px;
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
  /* Must be above parent CRUD modal overlays (Modal.vue uses 2000). */
  z-index: 3100;
}

.modal-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  min-width: 300px;
  text-align: center;
  box-shadow: 0 18px 44px rgba(15, 23, 42, 0.28);
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

.grid-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  width: 100%;
}

/* Réduire la taille des boutons d'export */
.grid-actions ::v-deep(.v-btn) {
  height: 28px;
  min-width: 28px;
  padding: 4px 6px;
  font-size: 0.85rem;
  border-radius: 4px;
}

.grid-actions ::v-deep(.v-btn .v-icon),
.grid-actions ::v-deep(.v-btn svg) {
  width: 16px;
  height: 16px;
  font-size: 16px;
}

.export-btn {
  background-color: #2d8fef;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.export-btn:hover {
  background-color: #1a6fd8;
}
</style>
