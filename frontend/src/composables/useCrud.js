import { ref } from "vue";
import auth from "../../auth";
import config from "../../config";
import { useMainStore } from "../store";
import { usePermissions } from "./usePermissions";

export function useCrud(modelName, apiRouteName, idField = "id", options = {}) {
  const mainStore = useMainStore();
  const { can, actionsFor } = usePermissions(modelName);

  const geojsonMode = !!options.geojson;

  const hasValidId = (value) => value !== null && value !== undefined && value !== "";

  const items = ref([]);
  const isLoading = ref(false);
  const pagination = ref({ count: null, next: null, previous: null, page_size: null });
  const showModal = ref(false);
  const selectedItem = ref(null);
  const mode = ref("view"); // add | change | view

  const fetchAll = async (page = null, extraQueryParams = null) => {
    isLoading.value = true;
    try {
      const mergedParams = {
        ...(extraQueryParams || {}),
        ...(page ? { page } : {}),
      };
      const params = Object.keys(mergedParams).length > 0 ? { params: mergedParams } : {};
      const response = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/${apiRouteName}/`, params);
      const data = response.data;
      // Support DRF paginated responses: { count, next, previous, results }
      let payload = data;
      if (data && Array.isArray(data.results)) {
        pagination.value = { count: data.count ?? null, next: data.next ?? null, previous: data.previous ?? null, page_size: data.page_size ?? null };
        payload = data.results;
      } else {
        pagination.value = { count: null, next: null, previous: null, page_size: null };
      }

      // Si l'API renvoie un FeatureCollection (GeoJSON), le convertir en tableau d'items
      if (payload && payload.type === 'FeatureCollection' && Array.isArray(payload.features)) {
        items.value = payload.features.map((f) => ({ ...(f.properties || {}), id: f.id || f.properties?.id, geometry: f.geometry }));
      } else if (geojsonMode && Array.isArray(payload)) {
        // Certains endpoints peuvent renvoyer un tableau de Feature
        items.value = payload.map((f) => (f && f.type === 'Feature') ? ({ ...(f.properties || {}), id: f.id || f.properties?.id, geometry: f.geometry }) : f);
      } else if (Array.isArray(payload)) {
        items.value = payload;
      } else {
        // Fallback: single object -> wrap into array
        items.value = payload ? [payload] : [];
      }
    } catch (err) {
      mainStore.setErrorMessage("Erreur lors du chargement.");
      console.error(err);
    } finally {
      isLoading.value = false;
    }
  };

  const resolveItemId = (payload) => {
    if (!payload) return null;
    return (
      payload[idField]
      ?? payload.id
      ?? payload.properties?.[idField]
      ?? payload.properties?.id
      ?? null
    );
  };

  const getNextId = async () => {
    try {
      const response = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/${apiRouteName}/getNextId/`);
      return response.data.next_id;
    } catch (err) {
      console.error("Erreur next ID", err);
      return null;
    }
  };

  const createItem = async (payload, extraQueryParams = null) => {
    console.log("create / payload :", payload);
    console.log("create / idField :", idField);
    let body = payload;
    if (geojsonMode) {
      console.log("Creating in GeoJSON mode");
      if (payload && payload.properties) {
        body = { type: "Feature", properties: payload.properties };
        if (payload.geometry) body.geometry = payload.geometry;
        if (payload.id) body.id = payload.id;
      } else {
        const { geometry, id, ...props } = payload || {};
        body = { type: "Feature", properties: props };
        if (geometry) body.geometry = geometry;
        if (id) body.id = id;
      }
    }

    // defensive: don't send client-side id on create
    const sendBody = JSON.parse(JSON.stringify(body));
    // if (!geojsonMode) {
    //   delete sendBody[idField];
    // } else {
    //   if (sendBody.properties) delete sendBody.properties[idField];
    //   delete sendBody.id;
    // }

    await auth.axiosInstance.post(`${config.API_BASE_URL}/api/${apiRouteName}/`, sendBody);
    mainStore.setSuccessMessage("Créé avec succès !");
    await fetchAll(null, extraQueryParams);
  };

  const updateItem = async (payload, extraQueryParams = null) => {
    console.log("update / payload :", payload);
    console.log("update / idField :", idField);
    const id = resolveItemId(payload);
    if (!hasValidId(id)) throw new Error(`ID introuvable pour ${idField}`);
    let body = payload;
    if (geojsonMode) {
      if (payload && payload.properties) {
        body = { type: "Feature", properties: payload.properties };
        if (payload.geometry) body.geometry = payload.geometry;
        //body.id = payload.id || payload.properties?.[idField] || payload[idField];
      } else {
        const { geometry, id: rootId, ...props } = payload || {};
        body = { type: "Feature", properties: props };
        if (geometry) body.geometry = geometry;
        //body.id = payload[idField] || rootId;
      }
    }
    // defensive copy and debug log
    const sendBody = JSON.parse(JSON.stringify(body));
    // Ensure we send a proper GeoJSON Feature: { type, properties, geometry }
    // Do NOT duplicate properties at root level; backend expects them inside `properties`.
    console.log("update / sendBody :", sendBody);
    await auth.axiosInstance.put(`${config.API_BASE_URL}/api/${apiRouteName}/${id}/`, sendBody);
    mainStore.setSuccessMessage("Modifié avec succès !");
    await fetchAll(null, extraQueryParams);
  };

  const deleteItem = async (payload, extraQueryParams = null) => {
    const id = resolveItemId(payload);
    if (!hasValidId(id)) throw new Error(`ID introuvable pour ${idField}`);
    await auth.axiosInstance.delete(`${config.API_BASE_URL}/api/${apiRouteName}/${id}/`);
    mainStore.setSuccessMessage("Supprimé !");
    await fetchAll(null, extraQueryParams);
  };

  // Open add modal, optionally with an initial item to prefill the form
  const openAdd = async (initialItem = null) => {
    mode.value = "add";
    if (initialItem) {
      selectedItem.value = initialItem;
    } else {
      selectedItem.value = geojsonMode ? { properties: {} } : {};
    }
    showModal.value = true;
  };

  const openEdit = (item) => {
    mode.value = "change";
    const it = { ...item };
    if (geojsonMode) {
      // Ensure selectedItem is a Feature-like object: root id + properties + geometry
      const props = it.properties ? { ...it.properties } : {};
      // if properties missing, collect non-meta keys into properties
      if (!it.properties) {
        Object.keys(it).forEach((k) => {
          if (k === "id" || k === "geometry") return;
          props[k] = it[k];
        });
      }
      const feature = { properties: props };
      if (it.geometry) feature.geometry = it.geometry;
      feature.id = it[idField] ?? it.id ?? props[idField] ?? null;
      selectedItem.value = feature;
    } else {
      if (!hasValidId(it[idField]) && hasValidId(it.id)) it[idField] = it.id;
      selectedItem.value = it;
    }
    showModal.value = true;
  };

  const openView = (item) => {
    mode.value = "view";
    const it = { ...item };
    if (geojsonMode) {
      const props = it.properties ? { ...it.properties } : {};
      if (!it.properties) {
        Object.keys(it).forEach((k) => {
          if (k === "id" || k === "geometry") return;
          props[k] = it[k];
        });
      }
      const feature = { properties: props };
      if (it.geometry) feature.geometry = it.geometry;
      feature.id = it[idField] ?? it.id ?? props[idField] ?? null;
      selectedItem.value = feature;
    } else {
      if (!hasValidId(it[idField]) && hasValidId(it.id)) it[idField] = it.id;
      selectedItem.value = it;
    }
    showModal.value = true;
  };

  const closeModal = () => {
    console.log("Closing modal");
    showModal.value = false;
    selectedItem.value = null;
    mode.value = "view";
  };

  return {
    items,
    isLoading,
    pagination,
    showModal,
    selectedItem,
    mode,
    can,
    actions: actionsFor(),

    fetchAll,
    createItem,
    updateItem,
    deleteItem,
    getNextId,

    openAdd,
    openEdit,
    openView,
    closeModal,
  };
}
