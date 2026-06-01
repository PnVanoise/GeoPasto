# GeoPasto

Application de gestion pastorale développée pour le **Parc National de la Vanoise**.

## Présentation fonctionnelle

GeoPasto permet de gérer l'ensemble du suivi pastoral d'un territoire :

- **Territoire** — unités pastorales (UP) avec historique de leurs géométries, quartiers de pâturage, propriétaires fonciers
- **Acteurs** — exploitants (groupements, éleveurs individuels), éleveurs membres, bergers salariés
- **Exploitation** — conventions d'exploitation, situations d'exploitation annuelles, passages de cheptels sur les quartiers (parcours), ruches, gardes
- **Troupeaux** — cheptels par espèce/race/catégorie, effectifs, dates de montée/descente
- **Suivi** — plans de suivi par UP, mesures de plan, réalisations, événements géolocalisés
- **Équipements & logements** — équipements d'alpage et d'exploitant, logements, abris d'urgence, commodités
- **Subventions** — suivi des subventions PNV par exploitant

Les objets géographiques sont saisis et visualisés sur carte (géométries en Lambert 93 / SRID 2154). L'accès est contrôlé par un système de permissions par groupes d'utilisateurs.

---

## Stack technique

- **Backend** : Django 5 + Django REST Framework + GeoDjango
- **Frontend** : Vue 3 + Vuetify + OpenLayers
- **Base de données** : PostgreSQL 15 + PostGIS 3 (schéma `geopasto`)

---

## Structure du dépôt

```
geopasto/
├── backend/          # Django — API REST, modèles, migrations
├── frontend/         # Vue 3 — SPA
├── doc/              # Documentation technique (MkDocs)
├── conf_nginx/       # Exemple de configuration nginx
├── conf_systemd/     # Fichier de service systemd gunicorn
└── geopasto_nginx.example  # Template nginx complet
```

---

## Prérequis système (Debian 12)

```bash
# PostgreSQL + PostGIS
sudo apt-get install -y postgresql-15 postgresql-client-15 \
    postgresql-15-postgis-3 postgresql-15-postgis-3-scripts

# Bibliothèques géospatiales
sudo apt-get install -y gdal-bin libgdal-dev python3-gdal \
    libgeos-dev libproj-dev proj-bin

# Python 3.11
sudo apt-get install -y python3.11 python3.11-dev python3.11-venv \
    python3-pip build-essential libpq-dev postgresql-server-dev-all

# Node.js 18 + npm
sudo apt-get install -y nodejs npm

# Serveur web
sudo apt-get install -y nginx
```

> **Versions validées :** PostgreSQL 15.7, PostGIS 3.3.2, GDAL 3.6.2, Python 3.11.2, Node.js 18.19.

---

## Installation rapide (dev)

### Base de données

```sql
CREATE DATABASE geopasto;
\c geopasto
CREATE EXTENSION postgis SCHEMA postgis;
CREATE SCHEMA geopasto;
CREATE USER geopasto_user WITH PASSWORD '...';
GRANT CONNECT ON DATABASE geopasto TO geopasto_user;
GRANT USAGE, CREATE ON SCHEMA geopasto TO geopasto_user;
GRANT USAGE ON SCHEMA postgis TO geopasto_user;
```

### Backend

```bash
cd backend
make install      # crée le venv + installe les dépendances dev
# éditer backend/.env (voir backend/.env.example)
make migrate
make runserver    # écoute sur http://127.0.0.1:8000
```

### Frontend

```bash
cd frontend
npm install
# éditer frontend/config.js — renseigner API_BASE_URL
npm run dev       # écoute sur http://localhost:5173
```

---

## Déploiement en production

### 1. Backend — gunicorn + systemd

Copier et adapter le fichier de service :

```bash
sudo cp conf_systemd/geopasto_backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now geopasto_backend
```

Le service lance gunicorn sur `0.0.0.0:8000` avec 3 workers.

### 2. Frontend — build statique

```bash
cd frontend
npm install
npm run build     # génère frontend/dist/
```

### 3. nginx

Copier et adapter le template :

```bash
sudo cp geopasto_nginx.example /etc/nginx/sites-available/geopasto
sudo ln -s /etc/nginx/sites-available/geopasto /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

Le template nginx route :
- `/` → frontend Vue (build statique ou proxy Vite)
- `/api/` → gunicorn Django
- `/admin/` → gunicorn Django
- `/static/` → fichiers statiques Django (`collectstatic`)

---

## Commandes utiles

### Backend

| Commande | Rôle |
|---|---|
| `make install` | Crée le venv et installe les dépendances |
| `make migrate` | Applique les migrations Django |
| `make runserver` | Lance le serveur de développement |
| `make test` | Lance les tests avec pytest |
| `make shell` | Shell Django interactif |
| `make clean` | Supprime le venv |

### Frontend

| Commande | Rôle |
|---|---|
| `npm run dev` | Serveur de développement (hot-reload) |
| `npm run build` | Build de production dans `dist/` |
| `npm run test` | Tests unitaires avec Vitest |
| `npm run format` | Formatage avec Prettier |

