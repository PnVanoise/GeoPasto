# Tests (pytest) — configuration et usage

Ce fichier décrit la configuration et les bonnes pratiques pour exécuter les tests du backend (`pytest`) localement et via l'interface Testing de VS Code.

## 1. Environnement virtuel (venv)
- Le venv du projet se trouve dans `backend/venv`.
- Pour l'activer depuis la racine du repo :

```bash
source backend/venv/bin/activate
```

- Installer les dépendances (si nécessaire) :

```bash
pip install -r backend/requirements-dev.txt
```

## 2. Variables d'environnement / .env
- Les settings Django lisent un fichier `.env` situé à la racine de `backend/` (voir `backend/geoagri/settings.py`).
- Minimum requis pour lancer les tests : définir `DJANGO_SECRET_KEY`

Exemple minimal `backend/.env` :

```
DJANGO_SECRET_KEY="test_secret"
```

Ajoutez les variables DATABASE_*, DATABASE_URL.

## 3. pytest — configuration
- Le fichier de configuration pytest est `backend/pytest.ini` et contient déjà :

```
[pytest]
DJANGO_SETTINGS_MODULE = geoagri.settings
python_files = test_*.py
python_classes = Test* *Tests *Test
python_functions = test_*
```

- Important : lancer pytest depuis `backend/` permet de prendre automatiquement en compte `backend/pytest.ini`.

## 4. Arborescence des fichiers de tests
- Tests organisés actuellement par application du projet Django :
  - `backend/alpages/tests/` → fichiers `test_*.py` pour l'application _alpages_
  - `backend/accounts/tests/` → fichiers `test_*.py` pour l'application _accounts_

## 5. Commandes utiles (ligne de commande)
- Depuis la racine du repo (méthode explicite) :

```bash
# activer venv
source backend/venv/bin/activate

# se placer dans backend (où est pytest.ini)
cd backend

# (optionnel, si pas de fichier .env)
# s'assurer que la clé est définie
export DJANGO_SECRET_KEY="test_secret"

# lister les tests collectés (arbre détaillé)
pytest --collect-only -v

# lancer tous les tests
pytest -q

# lancer un fichier précis
pytest alpages/tests/test_serializers.py -q

# lancer un test précis
pytest alpages/tests/test_serializers.py::UPProprietaireSerializerTest::test_up_nom_and_proprietaire_nom_populated -q
```

- Depuis la racine sans `cd` :

```bash
export DJANGO_SECRET_KEY="test_secret"
export PYTHONPATH=$PWD/backend
pytest -c backend/pytest.ini backend --collect-only -v
```

## 6. Intégration avec VS Code (Testing UI)
1. Installer l'extension officielle `Python` (ms-python.python).
2. Sélectionner l'interpréteur Python du venv : palette → `Python: Select Interpreter` → choisir `/home/.../geopasto/backend/venv/bin/python`.
3. Créer (ou modifier) `.vscode/settings.json` à la racine du workspace avec ces paramètres (exemple) :

```json
{
  "python.testing.unittestEnabled": false,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["-c", "backend/pytest.ini", "backend"],
  "python.testing.autoTestDiscoverOnOpenEnabled": true,
  "python.envFile": "${workspaceFolder}/backend/.env"
}
```

- Explication : `-c backend/pytest.ini` force pytest à utiliser la config dans `backend/` lorsqu'on démarre depuis la racine du workspace.
- `python.envFile` pointe sur `backend/.env` pour charger `DJANGO_SECRET_KEY` et autres variables.

4. Après avoir enregistré `settings.json`, recharger la fenêtre VS Code (`Developer: Reload Window`) si les tests ne sont pas découverts automatiquement.
5. Ouvrez la vue Testing (barre latérale) — la découverte des tests doit afficher les tests par fichier/classe.

## 7. Debugger un test depuis VS Code
- Exemple de configuration `launch.json` à ajouter dans `.vscode/` :

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug pytest (fichier courant)",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-c", "backend/pytest.ini", "${file}", "-q"],
      "cwd": "${workspaceFolder}/backend",
      "envFile": "${workspaceFolder}/backend/.env",
      "console": "integratedTerminal",
      "justMyCode": true
    }
  ]
}
```

- Placez un breakpoint, ouvrez le fichier de test, lancez la configuration `Debug pytest (fichier courant)`.

