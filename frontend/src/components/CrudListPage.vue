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
          variant="underlined"
          dense
          hide-details
          clearable
          append-inner-icon="mdi-magnify"
        />

        <template v-if="props.showFilters" v-for="filter in props.filters" :key="filter.key">
          <div v-if="filter.type === 'checkbox'" style="margin: 0 10px;">
            <v-switch
              v-model="activeFilters[filter.key]"
              :label="filter.label"
              dense
              flat
              color="primary"
              hide-details
              density="compact"
            />
          </div>

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
          @click="() => crud.openAdd(null, props.addQueryParams)"
          icon="mdi-plus"
          class="icon-round-btn add-btn"
          :title="`Ajouter ${props.itemLabel || 'élément'}`"
          aria-label="Ajouter"
        />

        <v-btn
          v-if="props.showExportButtons"
          color="success"
          icon="mdi-file-delimited"
          class="icon-round-btn export-btn"
          @click="handleExportAll"
          title="Exporter tout"
          aria-label="Exporter tout"
        />

        <v-btn
          v-if="props.showExportButtons"
          color="success"
          icon="mdi-file-delimited-outline"
          class="icon-round-btn export-btn"
          @click="exportVisible"
          title="Exporter visible"
          aria-label="Exporter visible"
        />
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
  </div>
</template>

<script setup>
import { ref, unref, computed, onMounted, watch } from "vue";
import Grid3 from "./Grid3.vue";
import { useCrudPage } from "../composables/useCrudPage";

const props = defineProps({
  modelName:        String,
  apiRouteName:     String,
  title:            String,
  itemLabel:        { type: String,   default: "élément" },
  columns:          Array,
  idField:          { type: String,   default: "id" },
  bgColor:          { type: String,   default: "#808080" },
  geojsonMode:      { type: Boolean,  default: false },
  searchFields:     { type: Array,    default: () => [] },
  filters:          { type: Array,    default: () => [] },
  showTitle:        { type: Boolean,  default: true },
  showHeader:       { type: Boolean,  default: true },
  showSearch:       { type: Boolean,  default: true },
  showFilters:      { type: Boolean,  default: true },
  showAddButton:    { type: Boolean,  default: true },
  showExportButtons:{ type: Boolean,  default: true },
  forceAdd:         { type: Boolean,  default: false },
  viewOnly:         { type: Boolean,  default: false },
  requestParams:    { type: Object,   default: null },
  addQueryParams:   { type: Object,   default: () => ({}) },
});

// ── useCrudPage à la place de useCrud ────────────────────────────────────────
const crud = useCrudPage(props.modelName, props.apiRouteName, props.idField, { geojson: props.geojsonMode });

const searchQuery  = ref("");
const activeFilters = ref({});

props.filters.forEach(f => {
  activeFilters.value[f.key] = f.default ?? "";
});

// ── Filtrage ─────────────────────────────────────────────────────────────────

function getNestedValue(obj, path) {
  return path.split(".").reduce((acc, key) => acc?.[key], obj);
}

const filteredEntries = computed(() => {
  let items = crud.items.value;

  if (searchQuery.value && searchQuery.value.trim() !== "") {
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

  props.filters.forEach(f => {
    const value = activeFilters.value[f.key];
    items = f.apply(items, value);
  });

  return items;
});

// ── Cycle de vie ─────────────────────────────────────────────────────────────

onMounted(() => {
  crud.fetchAll(null, props.requestParams);
});

watch(
  () => props.requestParams,
  (newParams, oldParams) => {
    if (JSON.stringify(newParams || {}) === JSON.stringify(oldParams || {})) return;
    crud.fetchAll(null, newParams);
  },
  { deep: true }
);

// ── Export CSV ───────────────────────────────────────────────────────────────

function exportCsv(rows, filename) {
  const headerFields = (props.columns || []).map((c) => c.label || c.field);
  const fields       = (props.columns || []).map((c) => c.field);
  const escape = (value) => {
    if (value == null) return "";
    return `"${String(value).replace(/"/g, '""')}"`;
  };
  const lines = [headerFields.map(escape).join(",")];
  for (const r of rows) {
    lines.push(fields.map((f) => escape(getNestedValue(r, f))).join(","));
  }
  const blob = new Blob([lines.join("\r\n")], { type: "text/csv;charset=utf-8;" });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement("a");
  a.href     = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function exportVisible()    { exportCsv(filteredEntries.value,  "export_visible.csv"); }
function handleExportAll()  { exportCsv(crud.items.value,       "export_all.csv"); }

// ── Actions grille ───────────────────────────────────────────────────────────

const computedActions = computed(() => {
  if (props.viewOnly) return { add: false, view: true, edit: false, delete: false };
  return crud.actions;
});

function handleEdit(item) {
  props.viewOnly ? crud.openView(item) : crud.openEdit(item);
}

function handleDelete(item) {
  if (props.viewOnly) return;
  (async () => {
    try {
      await crud.deleteItem(item, props.requestParams);
      window.dispatchEvent(new CustomEvent("geo-data-changed", { detail: { modelName: props.modelName } }));
    } catch (err) {
      console.error("Error deleting item", err);
    }
  })();
}
</script>

<style scoped>
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

.header-right .icon-round-btn {
  width: 32px;
  min-width: 32px;
  height: 32px;
  border-radius: 999px;
  padding: 0;
}

.header-actions .add-btn {
  margin-left: auto !important;
}

.header-actions .search-field .v-field,
.header-actions .search-field .v-text-field {
  height: 40px;
}

@media (max-width: 900px) {
  .header-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }

  .header-left {
    width: 100%;
    flex-direction: row;
    flex-wrap: wrap;
    align-items: flex-end;
    gap: 0.5rem;
  }

  .header-actions .search-field {
    flex: 1 1 100%;
    min-width: 0;
    width: 100%;
    margin: 0;
  }

  .header-left > div:not(.search-field) {
    flex: 0 0 auto;
    margin: 0 !important;
  }

  .header-right {
    width: 100%;
    margin-left: 0;
    justify-content: flex-start;
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-actions .add-btn {
    margin-left: 0 !important;
  }
}
</style>
