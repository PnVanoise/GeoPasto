export const maxLen = (n) => (v) => !v || v.length <= n || `${n} caractères maximum.`;
export const required = (v) => !!v?.toString().trim() || "Champ obligatoire.";
