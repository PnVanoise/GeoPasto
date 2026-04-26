import { useRouter } from "vue-router";
import { useCrud } from "./useCrud";

/**
 * useCrudPage — extension de useCrud pour les vues avec navigation par routes dédiées.
 *
 * Différences avec useCrud :
 *  - openAdd / openEdit / openView  → router.push() au lieu d'ouvrir une modale
 *  - createItem / updateItem        → redirigent vers la liste après succès
 *  - deleteItem                     → reste sur la liste (pas de redirection)
 *  - showModal / selectedItem / mode → absents (inutiles en mode page)
 *
 * Convention de nommage des routes (obligatoire) :
 *  - `${modelName}-list`
 *  - `${modelName}-add`
 *  - `${modelName}-edit`  (param :id)
 *  - `${modelName}-view`  (param :id)
 *
 * Usage :
 *   const crud = useCrudPage('type_cheptel', 'type_cheptel', 'id_type_cheptel')
 */
export function useCrudPage(modelName, apiRouteName, idField = "id", options = {}) {
  const router = useRouter();

  // Récupère tout useCrud intact
  const crud = useCrud(modelName, apiRouteName, idField, options);

  // Résolution d'ID locale (useCrud ne l'exporte pas)
  const resolveId = (item) =>
    item?.[idField] ?? item?.id ?? item?.properties?.[idField] ?? item?.properties?.id ?? null;

  // ── Navigation ──────────────────────────────────────────────────────────────

  const openAdd = (_initialItem = null, queryParams = {}) => {
    const hasQuery = queryParams && Object.keys(queryParams).length > 0;
    router.push({ name: `${modelName}-add`, ...(hasQuery ? { query: queryParams } : {}) });
  };

  const openEdit = (item) => {
    router.push({ name: `${modelName}-edit`, params: { id: resolveId(item) } });
  };

  const openView = (item) => {
    router.push({ name: `${modelName}-view`, params: { id: resolveId(item) } });
  };

  // ── Mutations avec redirection ───────────────────────────────────────────────

  const createItem = async (payload, extraQueryParams = null) => {
    await crud.createItem(payload, extraQueryParams);
    router.push({ name: `${modelName}-list` });
  };

  const updateItem = async (payload, extraQueryParams = null) => {
    await crud.updateItem(payload, extraQueryParams);
    router.push({ name: `${modelName}-list` });
  };

  // deleteItem : pas de redirection, on reste sur la liste
  // On le retransmet tel quel depuis crud

  return {
    // ── Tout useCrud ──
    ...crud,

    // ── Écrasements ──
    openAdd,
    openEdit,
    openView,
    createItem,
    updateItem,
  };
}
