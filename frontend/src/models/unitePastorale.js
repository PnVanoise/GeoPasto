export function emptyUnitePastorale() {
  return {
    properties: {
      code_up: "",
      nom_up: "",
      annee_version: new Date().getFullYear(),
      version_active: false,
      secteur: "",
      proprios: [],
    },
    geometry: null,
  };
}
