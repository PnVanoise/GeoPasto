# Installation — geopasto_backend

Prérequis : Python 3.11 (recommandé). Ce README décrit l'installation pour développement, CI et production.

## Synchronisation avec le dépôt

1. Créer un dossier vide et se placer dedans
2. Initialiser le repo et ajouter la remote :

```bash
git init
git remote add origin https://github.com/PnVanoise/GeoPasto.git
git pull origin main
```

## Quickstart (dev)

Exécutez ces commandes pour préparer un environnement de développement local :

```bash
# créer et activer le venv
python3 -m venv venv
source venv/bin/activate

# installer dépendances (utilise psycopg2-binary pour éviter compilation native)
pip install -r backend/requirements-dev.txt

# configurer les variables d'environnement (voir backend/.env.example)
cp backend/.env.example backend/.env
# éditez .env pour renseigner DJANGO_SECRET_KEY et DATABASE_URL

# appliquer migrations et lancer le serveur
python backend/manage.py migrate
python backend/manage.py runserver
```

Récupérez un fichier `settings.py` approprié si nécessaire (il n'est pas versionné).

## Création du service
```
sudo vim /etc/systemd/system/geopasto_back.service
```

```
[Unit]
Description=gunicorn daemon for Geopasto
After=network.target

[Service]
User=geoagri
Group=geoagri
WorkingDirectory=<install_dir>
ExecStart=<install_dir>/venv/bin/gunicorn --access-logfile <install_dir>/gunicorn-access.log --error-logfile=<install_dir>/gunicorn-error.log --workers 3 --bind 0.0.0.0:8000 geoagri.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target

```

## Configuration nginx (proxy web)
```
sudo vim /etc/nginx/sites-available/geoagri_backend
```

```
server {
    listen 80;
    server_name <@ip_server>;

    location /static/ {
            alias <install_dir>/geoagri/static/;
            #autoindex on;
    }

    location /media/ {
            alias <install_dir>/geoagri/media/;
    }

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        rewrite ^/back/(.*)$ /$1 break;

        add_header "Cross-Origin-Opener-Policy" "";

        # CORS headers
        # add_header 'Access-Control-Allow-Origin' '*' always;
        # add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE' always;
        # add_header 'Access-Control-Allow-Headers' 'Origin, Authorization, X-requested-With, Accept, Content-Type';


        # Ajout des headers de sécurité
        add_header Cross-Origin-Opener-Policy same-origin;
        add_header Cross-Origin-Embedder-Policy require-corp;
    }
}

```

# Lancer les tests

Les tests utilisent Django TestCase avec une base PostgreSQL+PostGIS. Le fichier `geoagri/settings.py` doit exister localement (non versionné) ou vous pouvez définir `DATABASE_URL` pointant vers une base de test.

## Prérequis pour tests et CI

- Installer les dépendances de développement :

```bash
pip install -r backend/requirements-dev.txt
```

### Dépendances système (production)

Avant d'installer `requirements.txt` en production, installez les paquets système nécessaires pour compiler des extensions natives :

```bash
sudo apt-get update
sudo apt-get install -y build-essential libpq-dev postgresql-server-dev-all
```

Ces paquets fournissent `pg_config` et les en-têtes nécessaires pour compiler `psycopg2` (source). Conservez `psycopg2` dans `requirements.txt` pour la production.

### CI / développement

Pour CI et dev nous utilisons `psycopg2-binary` (précompilé) afin d'éviter la compilation native. Le workflow CI se trouve dans `.github/workflows/pytest.yml` et installe `backend/requirements-dev.txt`.

Remarque : `psycopg2-binary` est pratique en CI/dev mais n'est pas recommandé pour services long-running en production ; préférez `psycopg2` en prod.
## Option 1 — `manage.py test` (Django natif)

```bash
python manage.py test alpages.tests --verbosity=2
```

## Option 2 — `pytest` (recommandé pour VS Code)

```bash
pytest
```

Ou pour un fichier précis :

```bash
pytest alpages/tests/test_serializers.py -v
```

L'extension **Python** (ms-python.python) de VS Code détecte automatiquement les tests via `pytest` une fois `pytest-django` installé.  
Le fichier `pytest.ini` à la racine du projet configure le module de settings Django.

---

## Création d'une nouvelle instance (prod)

### Prérequis système (paquets Debian/Ubuntu)

```bash
# PostgreSQL 15 + PostGIS
sudo apt-get install -y postgresql-15 postgresql-client-15 \
    postgresql-15-postgis-3 postgresql-15-postgis-3-scripts

# Bibliothèques géospatiales (GDAL, GEOS, PROJ) — requises par GeoDjango / psycopg2
sudo apt-get install -y gdal-bin libgdal-dev python3-gdal \
    libgeos-dev libproj-dev proj-bin

# Python 3.11 + outils de build (pour compiler psycopg2 en prod)
sudo apt-get install -y python3.11 python3.11-dev python3.11-venv \
    python3-pip build-essential libpq-dev postgresql-server-dev-all

# Node.js 18 + npm (frontend — Vite 5 / Vue 3)
sudo apt-get install -y nodejs npm

# Serveur web
sudo apt-get install -y nginx
```

> **Versions validées sur ce serveur (Debian 12) :** PostgreSQL 15.7, PostGIS 3.3.2, GDAL 3.6.2, GEOS 3.11.1, PROJ 9.1.1, Python 3.11.2, Node.js 18.19, npm 9.2.

---

1. Créer la base de données PostgreSQL et activer l'extension PostGIS :

```sql
CREATE DATABASE geopasto;
\c geopasto
CREATE EXTENSION postgis SCHEMA postgis;
CREATE SCHEMA geopasto;
```

2. Créer un utilisateur et lui donner les droits :

```sql
CREATE USER geopasto_user WITH PASSWORD '...';
GRANT CONNECT ON DATABASE geopasto TO geopasto_user;
GRANT USAGE, CREATE ON SCHEMA geopasto TO geopasto_user;
GRANT USAGE ON SCHEMA postgis TO geopasto_user;
```

   Django utilise `search_path=geopasto,postgis,public` — toutes les tables applicatives atterrissent dans le schéma `geopasto`. Ce schéma doit exister avant tout `migrate`.

3. Récupérer les sources, créer le venv et installer les dépendances de production :

```bash
python3 -m venv venv
source venv/bin/activate
sudo apt-get update
sudo apt-get install -y build-essential libpq-dev postgresql-server-dev-all
pip install -r backend/requirements.txt
```

4. Récupérer/éditer `backend/geoagri/settings.py` ou définir `DATABASE_URL` et `DJANGO_SECRET_KEY`.
5. Appliquer les migrations :

```bash
python backend/manage.py migrate
python backend/manage.py collectstatic --noinput
```

6. Configurer systemd/nginx comme indiqué plus haut, puis démarrer le service.

La base doit être à jour.

## Variables d'environnement

Créez un fichier `backend/.env` (ex : copier `backend/.env.example`) et définissez au minimum :

- `DJANGO_SECRET_KEY`
- `DATABASE_URL` (ex: `postgres://user:pass@host:5432/dbname`)
- `DEBUG` (True/False)

Voir `backend/.env.example` fourni.

## Raccourcis Makefile (dev)

Un `Makefile` est fourni dans `backend/` pour simplifier les tâches fréquentes (création venv, installation, tests, migration, runserver).


