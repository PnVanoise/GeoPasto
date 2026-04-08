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

          
          <div v-if="filter.type === 'text'" style="margin: 0 10px;">
            <v-text-field
              v-model="activeFilters[filter.key]"
              :label="filter.label"
              dense
              hide-details
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

    <!-- Pagination controls (compact) -->
    <div class="pagination-controls pagination-compact" v-if="hasPagination">
      <div class="pagination-right centered">
        <v-btn small icon @click="goToPage(1)" :disabled="currentPage === 1" aria-label="premiere">
          <v-icon small>mdi-page-first</v-icon>
        </v-btn>

        <v-btn small icon @click="goToPage(currentPage - 1)" :disabled="!hasPrev" aria-label="precedent">
          <v-icon small>mdi-chevron-left</v-icon>
        </v-btn>

        <span class="page-indicator">{{ currentPage }} / {{ totalPages || '–' }}</span>

        <v-btn small icon @click="goToPage(currentPage + 1)" :disabled="!hasNext" aria-label="suivant">
          <v-icon small>mdi-chevron-right</v-icon>
        </v-btn>

        <v-btn small icon @click="goToPage(totalPages)" :disabled="currentPage === totalPages" aria-label="derniere">
          <v-icon small>mdi-page-last</v-icon>
        </v-btn>
      </div>
    </div>

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
import { ref, unref, computed, onMounted, watch } from "vue";
import Grid3 from "./Grid3.vue";
import Modal from "./Modal.vue";
import { useCrud } from "../composables/useCrud";
import auth from "../../auth";
import config from "../../config";

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

props.filters.forEach(f => {
  activeFilters.value[f.key] = f.default ?? "";
});

const currentPage = ref(1);
const inputPage = ref(1);

function parsePageFromUrl(url) {
  if (!url) return null;
  try {
    const u = new URL(url);
    return u.searchParams.get("page") ? Number(u.searchParams.get("page")) : null;
  } catch (e) {
    return null;
  }
}

function updateCurrentPageFromPagination() {
  // Try to deduce current page from next/previous links
  const next = crud.pagination.value.next;
  const prev = crud.pagination.value.previous;
  if (next) {
    const p = parsePageFromUrl(next);
    if (p !== null) {
      currentPage.value = Math.max(1, p - 1);
      inputPage.value = currentPage.value;
      return;
    }
  }
  if (prev) {
    const p = parsePageFromUrl(prev);
    if (p !== null) {
      currentPage.value = p + 1;
      inputPage.value = currentPage.value;
      return;
    }
  }
  // default to 1 when no hints
  currentPage.value = 1;
  inputPage.value = 1;
}

const hasPagination = computed(() => crud.pagination.value.count !== null);

const pageSizeGuess = computed(() => {
  const len = crud.items.value?.length || 0;
  return len > 0 ? len : null;
});

const totalPages = computed(() => {
  const count = crud.pagination.value.count;
  if (!count) return null;
  const pageSize = crud.pagination.value.page_size || pageSizeGuess.value;
  if (!pageSize) return null;
  return Math.max(1, Math.ceil(count / pageSize));
});

const hasNext = computed(() => !!crud.pagination.value.next);
const hasPrev = computed(() => !!crud.pagination.value.previous);

onMounted(async () => {
  await crud.fetchAll(1);
  updateCurrentPageFromPagination();
});

watch(() => crud.pagination.value, () => updateCurrentPageFromPagination(), { deep: true });

function goToPage(p) {
  let target = Number(p) || 1;
  if (target < 1) target = 1;
  if (totalPages.value && target > totalPages.value) target = totalPages.value;
  inputPage.value = target;
  currentPage.value = target;
  crud.fetchAll(target);
}

// Computed pour filtrer les données (appliqué sur la page courante)
const filteredEntries = computed(() => {
  let items = crud.items.value || [];

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

watch([searchQuery, activeFilters], () => {
  // When search/filters change we keep the server page but reset to page 1
  goToPage(1);
});

const handleSubmit = async (formData) => {
  if (crud.mode.value === "add") {
    await crud.createItem(formData);
  } else if (crud.mode.value === "edit" || crud.mode.value === "change") {
    await crud.updateItem(formData);
  }
  crud.closeModal();
  try {
    window.dispatchEvent(new CustomEvent("geo-data-changed", { detail: { modelName: props.modelName } }));
  } catch (e) {
    console.warn("Could not dispatch geo-data-changed event", e);
  }
  // Refresh current page after change
  await crud.fetchAll(currentPage.value);
};

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

// Export all pages by iterating over paginated API
async function handleExportAll() {
  try {
    const allRows = [];
    let page = 1;
    let keep = true;
    while (keep) {
      const resp = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/${props.apiRouteName}/`, { params: { page } });
      const data = resp.data;
      let payload = data;
      if (data && Array.isArray(data.results)) payload = data.results;

      if (payload && payload.type === 'FeatureCollection' && Array.isArray(payload.features)) {
        payload.features.forEach((f) => allRows.push({ ...(f.properties || {}), id: f.id || f.properties?.id, geometry: f.geometry }));
      } else if (props.geojsonMode && Array.isArray(payload)) {
        payload.forEach((f) => allRows.push((f && f.type === 'Feature') ? ({ ...(f.properties || {}), id: f.id || f.properties?.id, geometry: f.geometry }) : f));
      } else if (Array.isArray(payload)) {
        payload.forEach((r) => allRows.push(r));
      } else if (payload) {
        allRows.push(payload);
      }

      // If API uses paginated structure, stop when next is falsy
      if (data && Array.isArray(data.results)) {
        if (!data.next) keep = false;
        else page += 1;
      } else {
        keep = false;
      }
    }

    // Build CSV from allRows
    const headerFields = (props.columns || []).map((c) => c.label || c.field);
    const fields = (props.columns || []).map((c) => c.field);
    const escape = (value) => {
      if (value == null) return "";
      const s = String(value).replace(/"/g, '""');
      return `"${s}"`;
    };
    const lines = [];
    lines.push(headerFields.map((h) => escape(h)).join(","));
    for (const r of allRows) {
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
  } catch (err) {
    console.error("Erreur export all", err);
  }
}

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
  if (props.viewOnly) return;
  (async () => {
    try {
      await crud.deleteItem(item);
      try {
        window.dispatchEvent(new CustomEvent("geo-data-changed", { detail: { modelName: props.modelName } }));
      } catch (e) {
        console.warn("Could not dispatch geo-data-changed event after delete", e);
      }
      // If deleting left the page empty, try to go back one page
      if ((crud.items.value || []).length === 0 && currentPage.value > 1) {
        goToPage(currentPage.value - 1);
      } else {
        await crud.fetchAll(currentPage.value);
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

.grid-footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
}

.grid-footer-actions .export-btn.export-rect {
  border-radius: 4px;
  padding: 6px 12px;
  height: 36px;
  text-transform: none;
}

.grid-footer-actions .export-btn .v-icon {
  font-size: 18px;
}

.pagination-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  gap: 8px;
}

.pagination-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination-right.centered {
  margin: 0 auto;
}

.pagination-compact {
  font-size: 0.9rem;
  color: #60636a;
  gap: 6px;
  padding: 6px 0;
}

.pagination-compact .page-indicator {
  color: #6b6f74;
  font-weight: 600;
  margin-right: 6px;
}

.pagination-compact .v-btn {
  min-width: 26px;
  height: 26px;
  padding: 0 4px;
  background: transparent;
  color: #6b6f74;
}

.pagination-compact .v-btn[disabled] {
  opacity: 0.35;
}

.pagination-compact .page-input .v-field__control,
.pagination-compact .page-input .v-input__control {
  padding-top: 2px;
  padding-bottom: 2px;
}

.pagination-compact .v-icon {
  font-size: 16px;
}

@media (max-width: 600px) {
  .grid-footer-actions {
    justify-content: flex-start;
  }
}
</style>
