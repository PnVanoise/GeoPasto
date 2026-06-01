# Installation — geopasto_frontend

## Prérequis système

Node.js 18 et npm sont les versions validées sur ce serveur (Debian 12).

```bash
sudo apt-get install -y nodejs npm
```

> **Versions validées :** Node.js 18.19, npm 9.2.

---

## Synchronisation avec le dépôt

```bash
git init
git remote add origin https://github.com/PnVanoise/GeoPasto.git
git pull origin main
```

---

## Quickstart (dev)

```bash
cd frontend

# installer les dépendances
npm install

# configurer l'URL du backend (voir section Configuration)
# éditer frontend/config.js

# lancer le serveur de développement
npm run dev
```

Le serveur écoute par défaut sur `http://localhost:5173`.

---

## Configuration

Éditer `frontend/config.js` pour pointer vers le backend :

```js
export default {
  API_BASE_URL: 'http://<@ip_server>:8000'
};
```

Ce fichier n'est pas versionné — il doit être créé/adapté à chaque instance.

---

## Scripts disponibles

| Commande | Rôle |
|---|---|
| `npm run dev` | Serveur de développement Vite (hot-reload) |
| `npm run build` | Build de production dans `dist/` |
| `npm run preview` | Prévisualisation locale du build `dist/` |
| `npm run test` | Tests unitaires avec Vitest |
| `npm run format` | Formatage du code avec Prettier |
| `npm run format:check` | Vérification du formatage sans modification |
| `npm run docs:dev` | Serveur de documentation VuePress |
| `npm run docs:build` | Build de la documentation |

---

## Tests

Les tests unitaires utilisent **Vitest** + **jsdom** + **@testing-library/vue**.

```bash
npm run test
```

La configuration est dans `vitest.config.js`. Le fichier `test/setupTests.js` initialise l'environnement de test.

---

## Déploiement en production

En production, le frontend est buildé statiquement et servi par nginx.

### 1. Builder le frontend

```bash
cd frontend
npm install
npm run build
```

Les fichiers sont générés dans `frontend/dist/`.

### 2. Configurer nginx

Ajouter un bloc `location` dans la config nginx pour servir `dist/` :

```nginx
location / {
    root <install_dir>/frontend/dist;
    try_files $uri $uri/ /index.html;
}
```

Le `try_files` est indispensable pour que le routeur Vue (mode history) fonctionne correctement — toutes les routes inconnues sont renvoyées vers `index.html`.

### 3. Service PM2 (alternative dev/staging)

Pour maintenir un serveur Vite actif (utile en staging, déconseillé en prod), PM2 est disponible via les dépendances du projet :

```bash
pm2 start "npm run dev -- --host=0.0.0.0 --port=9877" --name "geopasto_front"
pm2 save
pm2 startup   # pour relancer au démarrage du serveur
```

> En production préférer le build statique + nginx plutôt que PM2 + `npm run dev`.

---

## Stack

| Lib | Rôle |
|---|---|
| Vue 3 | Framework UI |
| Vuetify 3 | Composants Material Design |
| Vue Router 4 | Routage SPA |
| Pinia | State management |
| Axios | Requêtes HTTP vers l'API Django |
| OpenLayers 10 | Cartographie (standard actuel) |
| Leaflet / Leaflet-Draw | Cartographie legacy (ne pas introduire de nouveau code) |
| proj4 | Reprojection EPSG:4326 ↔ EPSG:3857 ↔ SRID:2154 |
| dayjs | Formatage des dates |
| Vite 5 | Bundler / serveur de dev |
| Vitest | Tests unitaires |
| Prettier | Formatage du code |
