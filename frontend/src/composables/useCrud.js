import { ref } from "vue";
import auth from "@/services/axios";
import config from "../../config";
import { usePermissions } from "./usePermissions";
import { useNotification } from "./useNotification";

const { notify } = useNotification();

const extractErrorMessage = (err, fallback) =>
  err?.response?.data?.detail ||
  err?.response?.data?.message ||
  (typeof err?.response?.data === "string" ? err.response.data : null) ||
  err?.message ||
  fallback;

export function useCrud(modelName, apiRouteName, idField = "id", options = {}) {
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
      const response = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/${apiRouteName}/`,
        params
      );
      const data = response.data;
      let payload = data;
      if (data && Array.isArray(data.results)) {
        pagination.value = {
          count: data.count ?? null,
          next: data.next ?? null,
          previous: data.previous ?? null,
          page_size: data.page_size ?? null,
        };
        payload = data.results;
      } else {
        pagination.value = { count: null, next: null, previous: null, page_size: null };
      }

      if (payload && payload.type === "FeatureCollection" && Array.isArray(payload.features)) {
        items.value = payload.features.map((f) => ({
          ...(f.properties || {}),
          id: f.id || f.properties?.id,
          geometry: f.geometry,
        }));
      } else if (geojsonMode && Array.isArray(payload)) {
        items.value = payload.map((f) =>
          f && f.type === "Feature"
            ? { ...(f.properties || {}), id: f.id || f.properties?.id, geometry: f.geometry }
            : f
        );
      } else if (Array.isArray(payload)) {
        items.value = payload;
      } else {
        items.value = payload ? [payload] : [];
      }
    } catch (err) {
      notify({ message: extractErrorMessage(err, "Erreur lors du chargement."), type: "error" });
    } finally {
      isLoading.value = false;
    }
  };

  const resolveItemId = (payload) => {
    if (!payload) return null;
    return (
      payload[idField] ??
      payload.id ??
      payload.properties?.[idField] ??
      payload.properties?.id ??
      null
    );
  };

  const createItem = async (payload, extraQueryParams = null) => {
    let body = payload;
    if (geojsonMode) {
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
    const sendBody = JSON.parse(JSON.stringify(body));
    try {
      await auth.axiosInstance.post(`${config.API_BASE_URL}/api/${apiRouteName}/`, sendBody);
      notify({ message: "Créé avec succès !", type: "success" });
      await fetchAll(null, extraQueryParams);
    } catch (err) {
      notify({ message: extractErrorMessage(err, "Erreur lors de la création."), type: "error" });
      throw err;
    }
  };

  const updateItem = async (payload, extraQueryParams = null) => {
    const id = resolveItemId(payload);
    if (!hasValidId(id)) throw new Error(`ID introuvable pour ${idField}`);
    let body = payload;
    if (geojsonMode) {
      if (payload && payload.properties) {
        body = { type: "Feature", properties: payload.properties };
        if (payload.geometry) body.geometry = payload.geometry;
      } else {
        const { geometry, id: rootId, ...props } = payload || {};
        body = { type: "Feature", properties: props };
        if (geometry) body.geometry = geometry;
      }
    }
    const sendBody = JSON.parse(JSON.stringify(body));
    try {
      await auth.axiosInstance.put(`${config.API_BASE_URL}/api/${apiRouteName}/${id}/`, sendBody);
      notify({ message: "Modifié avec succès !", type: "success" });
      await fetchAll(null, extraQueryParams);
    } catch (err) {
      notify({
        message: extractErrorMessage(err, "Erreur lors de la modification."),
        type: "error",
      });
      throw err;
    }
  };

  const deleteItem = async (payload, extraQueryParams = null) => {
    const id = resolveItemId(payload);
    if (!hasValidId(id)) throw new Error(`ID introuvable pour ${idField}`);
    try {
      await auth.axiosInstance.delete(`${config.API_BASE_URL}/api/${apiRouteName}/${id}/`);
      notify({ message: "Supprimé !", type: "success" });
      await fetchAll(null, extraQueryParams);
    } catch (err) {
      notify({
        message: extractErrorMessage(err, "Erreur lors de la suppression."),
        type: "error",
      });
      throw err;
    }
  };

  const openAdd = async (initialItem = null) => {
    mode.value = "add";
    selectedItem.value = initialItem ?? (geojsonMode ? { properties: {} } : {});
    showModal.value = true;
  };

  const openEdit = (item) => {
    mode.value = "change";
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

    openAdd,
    openEdit,
    openView,
    closeModal,
  };
}
