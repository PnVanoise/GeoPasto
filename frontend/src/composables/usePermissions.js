import { computed } from 'vue';
import { useMainStore } from '../store';

export function usePermissions(modelName) {
  const mainStore = useMainStore();

  // Vérification basique d’un droit
  const can = (action) => {
    return mainStore.hasPermission(modelName, action);
  };

  // Actions standardisées pour une GRID ou CRUD
  const actionsFor = () =>
    computed(() => ({
      add: can('add'),
      view: can('view'),
      edit: can('change'),
      delete: can('delete'),
    })).value;

  return { can, actionsFor };
}
