# Description fonctionnelle — GeoPasto

## Contexte

### Mission agro-environnement — Pôle connaissance et gestion

Le Parc National de la Vanoise (PNV) assure, via son pôle connaissance et gestion, un suivi des activités pastorales sur son territoire. L'élevage extensif en alpage est à la fois une composante essentielle du paysage et un levier de gestion des milieux ouverts. La mission agro-environnement accompagne les exploitants dans leurs pratiques, instruit les conventions d'exploitation et s'assure de la compatibilité des activités pastorales avec les objectifs de conservation du parc.

### Suivi des lieux des pratiques et des dispositifs spécifiques

Le suivi porte sur les **unités pastorales** — espaces délimités constituant le cadre géographique de référence — et sur les **quartiers d'alpage** qui les subdivisent opérationnellement. L'application permet de localiser et de décrire précisément les équipements (clôtures, abreuvoirs, bergeries…) et les logements pastoraux, et d'en suivre l'état dans le temps. Des **plans de suivi** définissent les mesures de gestion prescrites sur chaque UP, et leur taux de réalisation est tracé situation par situation.

### Acteurs

Plusieurs catégories d'acteurs interviennent dans la gestion des alpages :

- les **exploitants** (GIE, GAEC, ASA, éleveurs individuels) qui détiennent les conventions d'exploitation ;
- les **éleveurs**, personnes physiques membres d'un exploitant ou propriétaires d'un cheptel ;
- les **bergers**, salariés ou prestataires assurant la garde des troupeaux en alpage ;
- les **propriétaires fonciers**, dont les parcelles composent les unités pastorales ;
- les **agents du PNV**, utilisateurs de l'application, qui saisissent les observations et pilotent les plans de suivi.

### Centralisation des données

GeoPasto est l'outil unique de référence pour la gestion pastorale du PNV. Il centralise des données jusqu'alors dispersées : conventions et situations d'exploitation, compositions de troupeaux, parcours d'animaux sur les quartiers, état des équipements et des logements, avancement des mesures de gestion, compte-rendus de visites de terrain. Cette centralisation permet de produire des bilans annuels, d'assurer la traçabilité des interventions et de disposer d'une vue géographique cohérente des alpages.

---

## Vue d'ensemble

GeoPasto est une application de gestion pastorale destinée au Parc National de la Vanoise. Elle permet de suivre l'ensemble du cycle de vie des alpages : délimitation des unités pastorales, gestion des exploitants et de leurs troupeaux, suivi des plans de gestion (mesures, réalisations, événements), inventaire des équipements et des logements.

L'application est organisée autour d'une entité centrale : l'**unité pastorale** (UP), espace délimité sur lequel des exploitants exercent des activités d'élevage dans le cadre de situations d'exploitation. Chaque domaine fonctionnel gravite autour de cette entité.

Les données géographiques sont en projection Lambert 93 (SRID 2154) côté base, transformées en WGS84 (EPSG:4326) à l'API.

---

## Domaines fonctionnels

### 1. Territoire (`territoire.py`)

Ce domaine gère la description spatiale des alpages.

**UnitePastorale** — entité centrale de l'application. Identifiée par un code et un nom, rattachée à un secteur. Sa géométrie (`geom_active`, MultiPolygon) est un cache calculé automatiquement depuis l'historique des géométries valides. Le champ `active` indique si une géométrie est en vigueur à la date du jour.

**GeometrieUnitePastorale** — historique des contours d'une UP. Chaque enregistrement porte une date de début et une date de fin de validité (nulle si en cours). Un signal Django (`sync_geom_active`) maintient automatiquement le cache `geom_active` de l'UP à chaque ajout, modification ou suppression d'une entrée.

**ProprietaireFoncier** — personne physique ou morale propriétaire du foncier. Coordonnées de contact (nom, prénom, téléphone, mail, adresse).

**ProprietaireUnitePastorale** — liaison entre un propriétaire foncier et une unité pastorale (M2M explicite).

**QuartierPasto** — subdivision spatiale d'une UP au sein d'une situation d'exploitation. Un quartier porte un code, un nom et une géométrie Polygon. Il est lié à une `SituationDExploitation`. C'est l'unité de base du suivi des parcours de troupeaux.

---

### 2. Acteurs (`acteurs.py`)

Ce domaine gère les personnes et structures qui exploitent les alpages.

**Eleveur** — personne physique (éleveur individuel). Coordonnées de contact. Peut être président d'un exploitant ou membre d'une composition.

**TypeDExploitant** — nomenclature des types d'exploitants (GIE, GAEC, ASA, individuel…).

**Exploitant** — structure exploitante (groupement, association, individu). Rattachée à un type, avec un président (FK vers `Eleveur`).

**EtreCompose** — liaison M2M entre un `Exploitant` et ses membres, qui peuvent être soit des `Eleveur` individuels, soit des `Exploitant` membres (sous-groupements). Une contrainte garantit qu'un enregistrement pointe vers exactement un des deux types, sans auto-référence.

**Berger** — salarié ou prestataire de garde. Coordonnées de contact.

---

### 3. Exploitation (`exploitation.py`)

Ce domaine couvre les relations contractuelles et opérationnelles entre exploitants et unités pastorales.

**TypeConvention** — nomenclature des types de conventions d'exploitation (location, convention de pâturage…).

**ConventionDExploitation** — contrat formel liant un exploitant à une UP. Porte les surfaces (location, exploitable), les effectifs autorisés par espèce, la période d'exploitation contractuelle et une géométrie Polygon délimitant la zone concédée.

**SituationDExploitation** — occurrence concrète d'une exploitation : un exploitant sur une UP pour une période donnée. C'est le pivot de nombreuses autres entités (cheptels, quartiers, gardes, équipements, mesures, événements). Contrainte : `date_debut ≤ date_fin`.

**Exploiter (parcours)** — passage d'un cheptel sur un quartier. Lie un `Cheptel` à un `QuartierPasto` avec des dates et un nombre d'animaux. Le cheptel et le quartier doivent appartenir à la même situation. Une validation empêche de dépasser le nombre d'animaux du cheptel.

**GardeSituation** — affectation d'un berger à une situation d'exploitation pour une période. Permet de tracer les gardes successives sur un alpage.

**Ruche** — présence d'une ou plusieurs ruches sur une situation. Géométrie Point.

**SubventionPNV** — subvention accordée par le Parc National à un exploitant. Montant, statuts engagé/payé.

---

### 4. Troupeau (`troupeau.py`)

Ce domaine gère les référentiels zoologiques et la composition des cheptels.

**Production** — nomenclature du type de production (lait, viande, mixte…).

**CategoriePension** — nomenclature des catégories de pension (pension complète, demi-pension…).

**Espece** — nomenclature des espèces animales (bovins, ovins, caprins, équidés…).

**Race** — nomenclature des races, rattachée à une espèce.

**CategorieAnimaux** — catégorie d'animaux au sein d'une espèce (génisses, vaches allaitantes, agneaux…). Porte un coefficient UGB (Unité Gros Bétail, entre 0 et 1) utilisé pour les calculs de charge pastorale.

**Cheptel** — troupeau d'un éleveur (ou d'un exploitant) au sein d'une situation d'exploitation. Porte le nombre d'animaux, les dates de présence, la race, la catégorie, la production, la pension et le coefficient UGB. Un cheptel appartient soit à un éleveur individuel soit à un exploitant (contrainte mutuelle exclusive).

---

### 5. Suivi (`suivi.py`)

Ce domaine gère les plans de gestion, les mesures prescrites, leur réalisation, les événements observés et les visites de terrain.

**TypeDeSuivi** — nomenclature des types de suivi (pastorale, environnement, biodiversité…).

**PlanDeSuivi** — plan de gestion d'une UP pour une période donnée. Rattaché à un type de suivi et à une UP. Contient un ensemble de mesures.

**TypeDeMesure** — nomenclature des types de mesures (débroussaillage, entretien de point d'eau, mise en défens…).

**Enjeu** — enjeu écologique ou pastoral auquel une mesure répond (biodiversité, qualité paysagère, ressource en eau…). Lié aux mesures en M2M.

**MesureDePlan** — mesure prescrite dans un plan de suivi. Porte un code court (max 5 caractères), une description, une période de réalisation (champs `debut_periode_realisation`, `fin_periode_realisation` en format jj/mm), une période de validité, un caractère obligatoire ou non, des enjeux associés, et optionnellement une géométrie localisant la zone concernée.

**RealisationMesure** — état de réalisation d'une mesure pour une situation d'exploitation donnée. Pont entre `MesureDePlan` et `SituationDExploitation`. Statuts : *non réalisée*, *partiellement réalisée*, *réalisée*. Unique par couple (mesure, situation).

**TypeEvenement** — nomenclature des types d'événements observés.

**Evenement** — observation de terrain liée à une situation et/ou une mesure. Porte la date de l'événement, la date d'observation, l'observateur, la source, une description et optionnellement une géométrie.

**Visite** — visite de terrain sur une UP. Date, description courte, commentaire libre. Peut impliquer plusieurs éleveurs (contacts alpagistes) et plusieurs agents (observateurs, M2M vers `User`).

---

### 6. Équipements (`equipements.py`)

Ce domaine inventorie les équipements présents sur les alpages et ceux mis à disposition des exploitants.

**TypeEquipement** — nomenclature catégorisée des équipements (clôtures, abreuvoirs, bergeries, chemins…).

**EquipementAlpage** — équipement fixe appartenant à l'alpage (UP). Porte un état, un type et une géométrie (Point, Ligne ou Polygone selon le type).

**EquipementExploitant** — équipement mis à disposition d'un exploitant dans le cadre d'une situation d'exploitation. Peut être rattaché à un `BeneficierDe` (abri d'urgence). Même structure qu'`EquipementAlpage` mais lié à une situation plutôt qu'à une UP.

---

### 7. Logements (`logements.py`)

Ce domaine décrit les logements pastoraux (chalets, cabanes…) présents sur les unités pastorales et les abris d'urgence.

**Logement** — bâtiment de logement sur une UP. Très détaillé : statut, type, accès, propriété, état du bâtiment, surface, équipements sanitaires (WC, douche), alimentation électrique, alimentation et qualité de l'eau, assainissement, chauffage, stockage. Géométrie Point.

**Commodite** — nomenclature des commodités disponibles dans un abri d'urgence.

**AbriDUrgence** — abri d'urgence indépendant (non rattaché à une UP). Description, état.

**AbriDUrgenceCommodite** — liaison entre un abri d'urgence et ses commodités, avec état et quantité.

**BeneficierDe** — période pendant laquelle un exploitant bénéficie d'un abri d'urgence. Dates de début/fin, géométrie Point de localisation.

---

## Relations clés entre domaines

```
UnitePastorale
  ├── GeometrieUnitePastorale   (historique spatial)
  ├── ProprietaireUnitePastorale → ProprietaireFoncier
  ├── ConventionDExploitation → Exploitant, TypeConvention
  ├── SituationDExploitation → Exploitant
  │     ├── QuartierPasto       (zones spatiales)
  │     ├── Cheptel → Eleveur / Exploitant, Race, CategorieAnimaux…
  │     │     └── Exploiter → QuartierPasto  (parcours)
  │     ├── GardeSituation → Berger
  │     ├── Ruche
  │     ├── EquipementExploitant → TypeEquipement
  │     ├── RealisationMesure → MesureDePlan
  │     └── Evenement → MesureDePlan, TypeEvenement
  ├── PlanDeSuivi → TypeDeSuivi
  │     └── MesureDePlan → TypeDeMesure, Enjeu (M2M)
  ├── EquipementAlpage → TypeEquipement
  ├── Logement
  └── Visite → Eleveur (M2M), User (M2M)

Exploitant
  ├── EtreCompose → Eleveur / Exploitant  (composition)
  ├── SubventionPNV
  └── BeneficierDe → AbriDUrgence
        └── AbriDUrgenceCommodite → Commodite
```
