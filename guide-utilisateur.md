# Guide utilisateur — Geopasto

## Sommaire

1. [Navigation générale](#1-navigation-générale)
2. [Les listes](#2-les-listes)
3. [Les formulaires simples](#3-les-formulaires-simples)
4. [Les formulaires avec géométrie](#4-les-formulaires-avec-géométrie)

---

## 1. Navigation générale

L'application s'articule autour d'un **menu latéral** (masquable) qui donne accès aux différentes sections métier. L'application mémorise la dernière section visitée.

Le bandeau supérieur affiche le nom de l'utilisateur connecté et le bouton de déconnexion.

**Droits** : certaines actions (ajout, modification, suppression) peuvent être absentes selon votre profil. Si un bouton n'est pas visible, c'est que vous n'avez pas la permission correspondante.

---

## 2. Les listes

Chaque section affiche la liste des objets du type concerné sous forme de **tableau**. La liste est accompagnée, pour les objets géographiques, d'une **carte** positionnée à droite (ou en dessous sur écran étroit).

### 2.1 Barre d'outils de la liste

```
[ Recherche... 🔍 ]  [ Filtre 1 ]  [ Filtre 2 ]       [+]  [⬇]  [⬇]
```

| Élément | Rôle |
|---|---|
| Champ **Recherche** | Filtre instantané sur le texte visible — tapez n'importe quel mot |
| **Filtres** (switch, liste déroulante…) | Restreignent la liste selon un critère métier (ex. UP actives seulement) |
| Bouton **+** (bleu) | Crée un nouvel objet |
| Bouton **⬇** (vert, plein) | Exporte **tous** les enregistrements en CSV |
| Bouton **⬇** (vert, contour) | Exporte uniquement les enregistrements **visibles** (après filtrage) en CSV |

> Le bouton **+** n'apparaît que si vous avez le droit d'ajout sur ce type d'objet.

### 2.2 Tableau

Chaque ligne représente un objet. Les colonnes peuvent être **triées** en cliquant sur leur en-tête ; un deuxième clic inverse l'ordre.

En fin de ligne, trois icônes d'action sont disponibles selon vos droits :

| Icône | Action |
|---|---|
| 👁 Œil | **Consulter** l'objet (lecture seule) |
| ✏️ Crayon | **Modifier** l'objet |
| 🗑 Poubelle | **Supprimer** l'objet (demande confirmation) |

### 2.3 Interaction liste ↔ carte (objets géographiques)

Pour les sections dont les objets ont une géométrie (unités pastorales, quartiers, équipements…), la liste et la carte sont **synchronisées** :

- **Survoler** une ligne met en évidence le polygone / point correspondant sur la carte.
- **Cliquer** sur une ligne sélectionne l'objet : la carte zoome dessus et affiche une bulle d'information.
- **Cliquer** sur un objet de la carte sélectionne la ligne correspondante dans le tableau et la fait défiler à l'écran.

La bulle de la carte propose des liens **Consulter** / **Modifier** selon vos droits.

### 2.4 Export CSV

Le fichier exporté contient les colonnes affichées dans le tableau.

- **Export tout** : ignore la recherche et les filtres actifs.
- **Export visible** : n'exporte que ce qui est affiché après filtrage.

---

## 3. Les formulaires simples

Un clic sur **+**, **✏️** ou **👁** depuis une liste ouvre le formulaire de l'objet dans la **même page** (navigation par URL).

### 3.1 Modes du formulaire

| Mode | Comment y accéder | Comportement |
|---|---|---|
| **Consultation** (👁) | Clic sur l'icône œil | Tous les champs sont grisés, aucune modification possible |
| **Ajout** (+) | Bouton + de la liste | Formulaire vide à remplir |
| **Modification** (✏️) | Clic sur l'icône crayon | Formulaire pré-rempli, modifiable |

### 3.2 Structure d'un formulaire

```
         Titre de l'objet
┌────────────────────────────────────┐
│  Champ 1          Champ 2          │
│  Champ 3          Champ 4          │
│  …                                 │
└────────────────────────────────────┘
     [ ← Retour ]   [ 💾 Enregistrer ]
```

- Les champs obligatoires sont signalés par un astérisque `*` ou bloquent la soumission si vides.
- Les champs de type **date** acceptent la saisie directe (`JJ/MM/AAAA`) ou un sélecteur de date.
- Les champs de type **liste déroulante** proposent une valeur vide (effacable) en plus des choix métier.
- Les champs `description` sont limités à **150 caractères** ; un compteur s'affiche en temps réel.
- Les champs `commentaire` sont des zones de texte libre sans limite de longueur.

### 3.3 Actions du formulaire

| Bouton | Action |
|---|---|
| **← Retour** | Revient à la liste sans enregistrer |
| **💾 Enregistrer** | Soumet le formulaire ; revient à la liste si la sauvegarde réussit |

> Le bouton **Enregistrer** n'est visible qu'en mode Ajout ou Modification.

### 3.4 Messages d'erreur

En cas de problème (champ obligatoire manquant, valeur invalide, conflit serveur), un message en rouge s'affiche sous le champ concerné ou en haut du formulaire. Corrigez la valeur indiquée et soumettez à nouveau.

---

## 4. Les formulaires avec géométrie

Certains objets portent une géométrie (polygone, point…) : **unités pastorales**, **quartiers pastoraux**, **équipements**, **logements**, **ruches**, **conventions**…

Le formulaire de ces objets est divisé en deux parties côte à côte :

```
┌──────────────────────┬─────────────────────────────────────┐
│  Champs attributaires│  Carte / Éditeur de géométrie       │
│  Nom, code…          │                                     │
│                      │  [dessin / saisie de coordonnées]   │
└──────────────────────┴─────────────────────────────────────┘
     [ ← Retour ]   [ 💾 Enregistrer ]
```

Sur écran étroit (téléphone, petite tablette), les deux parties s'empilent verticalement.

### 4.1 Outils de la carte d'édition

La barre d'outils de la carte varie selon le type de géométrie attendu :

#### Polygone / Multipolygone (quartiers, unités pastorales…)

| Outil | Action |
|---|---|
| ✏️ Dessiner | Cliquez pour poser les sommets du polygone. **Double-clic** pour terminer le tracé. |
| ✎ Modifier | Déplacez les sommets existants par glisser-déposer. |
| 🗑 Effacer | Supprime la géométrie en cours. |

> **Tip dessin polygone :** chaque clic ajoute un sommet. Double-cliquez sur le dernier point pour fermer et valider le polygone. Pour un multipolygone, répétez l'opération — chaque tracé s'ajoute à la géométrie existante.

#### Point (équipements, logements, ruches…)

| Outil | Action |
|---|---|
| 📍 Placer | Cliquez une fois sur la carte pour placer le point. |
| ✎ Modifier | Faites glisser le point vers sa nouvelle position. |
| 🗑 Effacer | Supprime le point. |

### 4.2 Navigation sur la carte

| Geste | Action |
|---|---|
| Molette / pincement | Zoom avant / arrière |
| Clic + glisser | Déplacer la vue |
| Bouton **[  ]** (plein écran) | Agrandit la carte (si disponible) |
| Sélecteur de couches (coin supérieur droit) | Bascule entre fond de carte OSM et fond satellite, active/désactive les couches supplémentaires |

### 4.3 Mode consultation (lecture seule)

En mode consultation, la carte affiche la géométrie enregistrée mais les outils de dessin et de modification sont désactivés. Vous pouvez zoomer et déplacer la vue.

### 4.4 Enregistrement

La géométrie dessinée **ne sera sauvegardée que lorsque vous cliquez sur Enregistrer**. Si vous quittez le formulaire sans enregistrer (bouton Retour ou navigation arrière), les modifications de géométrie seront perdues.

Si aucune géométrie n'est dessinée alors qu'elle est obligatoire, un message d'erreur s'affiche sous la carte au moment de la soumission.

---

*Document généré depuis la base de code — à mettre à jour si l'interface évolue.*
