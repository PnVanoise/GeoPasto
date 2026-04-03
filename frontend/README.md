# Installation geopasto_frontend

## Synchronisation avec le repo
Créer un dossier vide

Se positionner dans ce dossier

Initialiser le repo : ```git init```

Définir la source distante : ```git remote add origin https://github.com/PnVanoise/geopasto_front.git```

Récupérer les données : ```git pull origin main```

## Configuration locale

(Pré-requis : Installation Node.js / npm)

Dans le répertoire d'installation, installer les bibliothèques externes (leaflet, dayjs, pm2, ...) : ```npm update```

Dans le fichier <install_dir>/_config.js_, mettre à jour l'adresse du backend API.
```
export default {
    API_BASE_URL: 'http://<@ip_server>:8000'
  };
```

## Création du service
PM2 a été installé avec les dépendances du projet. C'est un gestionnaire de processus pour des applications Node.js. Il permet de maintenir les process actifs, les recharger et faciliter les tâches d'administration.
```
pm2 start "npm run dev -- --host=0.0.0.0 --port=9877" --name "geopasto_front"
```

- Listes / formulaires (4 fichiers)
- Différence json / geojson
- NextID
- Geometrie vide
- Grilles imbriquées
- Formulaires paramétrés 