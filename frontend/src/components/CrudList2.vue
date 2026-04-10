<template>
  <div>
    <h2 v-if="props.showTitle" class="w3-center">{{ title }}</h2>

    <div v-if="props.showHeader" class="header-actions">
      <div class="header-left">
        <v-text-field
          density="compact"
          v-if="props.showSearch"
          class="search-field"
          v-model="searchQuery"
          label="Recherche"
          dense
          hide-details
          clearable
          append-inner-icon="mdi-magnify"
        />

        <!-- Rendu automatique des filtres -->
        <template v-if="props.showFilters" v-for="filter in props.filters" :key="filter.key">
          <!-- Checkbox -->
          <div v-if="filter.type === 'checkbox'" style="margin: 0 10px;">
            <v-switch
              v-model="activeFilters[filter.key]"
              :label="filter.label"
              dense
              hide-details
              density="compact"
            />
          </div>

          <!-- Select -->
          <div v-if="filter.type === 'select'" style="margin: 0 10px; min-width:200px;">
            <v-select
              :items="[{ value: '', label: '-- Tous --' }].concat(unref(filter.options) || [])"
              item-title="label"
              item-value="value"
              v-model="activeFilters[filter.key]"
              :label="filter.label"
              dense
              hide-details
              clearable
              density="compact"
            />
          </div>
        </template>
      </div>

      <div class="header-right">

        <v-btn
          v-if="props.showAddButton && !props.viewOnly && (crud.can('add') || props.forceAdd)"
          color="info"
          @click="() => crud.openAdd(props.initialNewItem ? { ...props.initialNewItem } : null)"
          prepend-icon="mdi-plus-circle"
          class="add-btn"
        >
          Ajouter
        </v-btn>
        
        
      </div>
    </div>

    <Grid3
      :data="filteredEntries"
      :showActions="false"
      @export-all="handleExportAll"
      :columns="columns"
      :actions="computedActions"
      :idField="idField"
      :bgColor="bgColor"
      @view="crud.openView"
      @edit="handleEdit"
      @delete="handleDelete"
    />

    <div class="grid-footer-actions">
      <v-btn color="success" class="export-btn export-rect" @click="handleExportAll">
        <v-icon left>mdi-file-delimited</v-icon>
        Exporter — Toutes les données
      </v-btn>

      <v-btn color="success" class="export-btn export-rect" @click="exportVisible">
        <v-icon left>mdi-file-delimited-outline</v-icon>
        Exporter — Visibles
      </v-btn>
    </div>

    <Modal :show="crud.showModal.value" @close="crud.closeModal" :close-on-overlay="false">
      <component
        :is="formComponent"
        :initialForm="crud.selectedItem.value"
        :itemLabel="itemLabel"
        :mode="crud.mode.value"
        :onClose="crud.closeModal"
        :onSubmit="handleSubmit"
      />
    </Modal>
  </div>
</template>

<script setup>
import { ref, unref, computed, onMounted, onBeforeUnmount, watch } from "vue";
import Grid3 from "./Grid3.vue";
import Modal from "./Modal.vue";
import { useCrud } from "../composables/useCrud";

const props = defineProps({
  modelName: String,
  apiRouteName: String,
  title: String,
  itemLabel: { type: String, default: "élément" },
  columns: Array,
  idField: { type: String, default: "id" },
  formComponent: Object,
  bgColor: { type: String, default: "#808080" },
  geojsonMode: { type: Boolean, default: false },
  showYearFilter : { type : Boolean, default: false },
  searchFields: {
    type: Array,
    default: () => []
  },
  filters: {
    type: Array,
    default: () => []
  },
  // UI control when embedded
  showTitle: { type: Boolean, default: true },
  showHeader: { type: Boolean, default: true },
  showSearch: { type: Boolean, default: true },
  showFilters: { type: Boolean, default: true },
  showAddButton: { type: Boolean, default: true },
  forceAdd: { type: Boolean, default: false },
  initialNewItem: { type: Object, default: null },
  viewOnly: { type: Boolean, default: false },
});
const crud = useCrud(props.modelName, props.apiRouteName, props.idField, { geojson: props.geojsonMode });
const searchQuery = ref("");
const activeFilters = ref({});

// Initialise les filtres avec leurs valeurs par défaut
props.filters.forEach(f => {
  activeFilters.value[f.key] = f.default ?? "";
});

// Gestion manuelle des changements
function onSelectChange(event, key) {
  activeFilters.value = {
    ...activeFilters.value,
    [key]: event.target.value
  };
}

function onCheckboxChange(event, key) {
  activeFilters.value = {
    ...activeFilters.value,
    [key]: event.target.checked
  };
}

// Computed pour filtrer les données
const filteredEntries = computed(() => {
  let items = crud.items.value;

  // Recherche
  if(searchQuery.value && searchQuery.value.trim() !== "") {
    const q = searchQuery.value.toLowerCase();
    items = items.filter(item => {
      if (props.searchFields.length === 0) {
        return JSON.stringify(item).toLowerCase().includes(q);
      }
      return props.searchFields.some(field => {
        const value = getNestedValue(item, field);
        return value?.toString().toLowerCase().includes(q);
      });
    });
  }

  // Application des filtres
  props.filters.forEach(f => {
    const value = activeFilters.value[f.key];
    items = f.apply(items, value);
  });

  return items;
});

function getNestedValue(obj, path) {
  return path.split(".").reduce((acc, key) => acc?.[key], obj);
}

const findItemById = (id) => {
  const expected = String(id);
  return (crud.items.value || []).find((item) => {
    const candidate =
      item?.[props.idField] ??
      item?.id ??
      item?.properties?.[props.idField] ??
      item?.properties?.id;
    return String(candidate) === expected;
  });
};

const onCrudOpenView = async (event) => {
  try {
    const detail = event?.detail || {};
    if (!detail.modelName || detail.modelName !== props.modelName) return;
    if (detail.id === undefined || detail.id === null) return;

    let target = findItemById(detail.id);
    if (!target) {
      await crud.fetchAll();
      target = findItemById(detail.id);
    }

    if (target) {
      crud.openView(target);
    }
  } catch (err) {
    console.warn("Could not open view from crud-open-view event", err);
  }
};

onMounted(() => {
  crud.fetchAll();
  window.addEventListener("crud-open-view", onCrudOpenView);
});

onBeforeUnmount(() => {
  window.removeEventListener("crud-open-view", onCrudOpenView);
});

// If initialNewItem is provided, prefill selectedItem when entering add mode
watch(() => crud.mode.value, (m) => {
  if (m === 'add' && props.initialNewItem) {
    crud.selectedItem.value = { ...props.initialNewItem };
  }
});

const handleSubmit = async (formData) => {
  console.log("Submitting form data:", formData);
  if (crud.mode.value === "add") {
    await crud.createItem(formData);
  } else if (crud.mode.value === "edit" || crud.mode.value === "change") {
    await crud.updateItem(formData);
  }
  crud.closeModal();
  // notify other parts of the app that data changed (modelName provided)
  try {
    window.dispatchEvent(new CustomEvent("geo-data-changed", { detail: { modelName: props.modelName } }));
  } catch (e) {
    console.warn("Could not dispatch geo-data-changed event", e);
  }
};

// Export visible rows as CSV
function exportVisible() {
  const rows = filteredEntries.value || [];
  const headerFields = (props.columns || []).map((c) => c.label || c.field);
  const fields = (props.columns || []).map((c) => c.field);

  const escape = (value) => {
    if (value == null) return "";
    const s = String(value).replace(/"/g, '""');
    return `"${s}"`;
  };

  const lines = [];
  lines.push(headerFields.map((h) => escape(h)).join(","));

  for (const r of rows) {
    const row = fields.map((f) => {
      const v = getNestedValue(r, f);
      return escape(v);
    });
    lines.push(row.join(","));
  }

  const csv = lines.join("\r\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "export_visible.csv";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

// CSV export helper used by parent when Grid3 requests full export
function handleExportAll() {
  const rows = crud.items.value || [];
  const headerFields = (props.columns || []).map((c) => c.label || c.field);
  const fields = (props.columns || []).map((c) => c.field);

  const escape = (value) => {
    if (value == null) return "";
    const s = String(value).replace(/"/g, '""');
    return `"${s}"`;
  };

  const lines = [];
  lines.push(headerFields.map((h) => escape(h)).join(","));

  for (const r of rows) {
    const row = fields.map((f) => {
      const v = getNestedValue(r, f);
      return escape(v);
    });
    lines.push(row.join(","));
  }

  const csv = lines.join("\r\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "export_all.csv";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

// If viewOnly is set, restrict actions to view-only in the grid
const computedActions = computed(() => {
  if (props.viewOnly) {
    return { add: false, view: true, edit: false, delete: false };
  }
  return crud.actions;
});

function handleEdit(item) {
  if (props.viewOnly) {
    crud.openView(item);
  } else {
    crud.openEdit(item);
  }
}

function handleDelete(item) {
  if (props.viewOnly) {
    // no-op when in viewOnly
    return;
  }
  // perform delete and notify listeners so maps/lists can refresh
  (async () => {
    try {
      await crud.deleteItem(item);
      try {
        window.dispatchEvent(new CustomEvent("geo-data-changed", { detail: { modelName: props.modelName } }));
      } catch (e) {
        console.warn("Could not dispatch geo-data-changed event after delete", e);
      }
    } catch (err) {
      console.error("Error deleting item", err);
    }
  })();
}
</script>


<style scoped>

.form-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  margin-bottom: 1rem;
}

/* Search occupies one third on the left; Add button aligned to the right */
.header-actions .search-field {
  flex: 0 0 33%;
  min-width: 240px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1 1 auto;
}

.header-right {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-left: 16px;
}

.header-right .export-btn {
  height: 28px;
  min-width: 28px;
  padding: 4px 6px;
}

.header-right .export-btn .v-icon {
  font-size: 16px;
}

.header-actions .add-btn {
  margin-left: auto !important;
  flex: 0 0 auto;
  min-width: 140px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 40px;
}

/* Make sure Vuetify field height aligns with the button */
.header-actions .search-field .v-field,
.header-actions .search-field .v-text-field {
  height: 40px;
}

/* Responsive: stack on small screens */
@media (max-width: 600px) {
  .header-actions {
    flex-direction: column;
    align-items: stretch;
  }
  .header-actions .search-field,
  .header-actions .add-btn {
    flex: 1 1 auto;
    margin-left: 0;
  }
}

/* Footer export buttons under the grid */
.grid-footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
}

.grid-footer-actions .export-btn.export-rect {
  border-radius: 4px; /* moins arrondi */
  padding: 6px 12px;
  height: 36px;
  text-transform: none;
}

.grid-footer-actions .export-btn .v-icon {
  font-size: 18px;
}

@media (max-width: 600px) {
  .grid-footer-actions {
    justify-content: flex-start;
  }
}
</style>