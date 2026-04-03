<script setup>
import { computed, ref, onMounted } from "vue";
import { RouterLink, RouterView, useRoute, useRouter } from "vue-router";

import Notification from "./components/Notification.vue";
import Login from "./components/Login.vue";
import Logout from "./components/Logout.vue";

import { useMainStore } from "./store";
import auth from "../auth";

const mainStore = useMainStore();
const isAuthenticated = computed(() => mainStore.isAuthenticated);

const successMessage = computed(() => mainStore.successMessage);
const errorMessage = computed(() => mainStore.errorMessage);

const initializeUserData = async () => {
  try {
    await mainStore.fetchUserPermissions();
    console.log("✅ Permissions chargées :", mainStore.userPermissions);
  } catch (error) {
    console.error("❌ Erreur lors du chargement des permissions :", error);
  }
};

const handleAuthenticated = async () => {
  await initializeUserData();
  router.push("/");
};

const route = useRoute();
const router = useRouter();
const accRef = ref(null);
const accAdmi = ref(null);
const accExpl = ref(null);
const accPlan = ref(null);
const accEve = ref(null);
const accEquip = ref(null);

const activeAcc = ref(null);

const clearSuccessMessage = () => {
  mainStore.setSuccessMessage("");
};

const clearErrorMessage = () => {
  mainStore.setErrorMessage("");
};

function accRefFunc() {
  var x = accRef.value;
  if (activeAcc.value && activeAcc.value !== accRef.value) {
    activeAcc.value.className = activeAcc.value.className.replace(" w3-show", "");
  }
  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show";
    activeAcc.value = x; // Mettez à jour l'accordéon actif
  } else {
    x.className = x.className.replace(" w3-show", "");
    activeAcc.value = null; // Réinitialiser l'accordéon actif
  }
}


function accAdmiFunc() {
  var x = accAdmi.value;
  if (activeAcc.value && activeAcc.value !== accAdmi.value) {
    activeAcc.value.className = activeAcc.value.className.replace(" w3-show", "");
  }
  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show";
    activeAcc.value = x; // Mettez à jour l'accordéon actif
  } else {
    x.className = x.className.replace(" w3-show", "");
    activeAcc.value = null; // Réinitialiser l'accordéon actif
  }
}

function accExplFunc() {
  var x = accExpl.value;
  if (activeAcc.value && activeAcc.value !== accExpl.value) {
    activeAcc.value.className = activeAcc.value.className.replace(" w3-show", "");
  }
  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show";
    activeAcc.value = x; // Mettez à jour l'accordéon actif
  } else {
    x.className = x.className.replace(" w3-show", "");
    activeAcc.value = null; // Réinitialiser l'accordéon actif
  }
}

function accPlanFunc() {
  var x = accPlan.value;
  if (activeAcc.value && activeAcc.value !== accPlan.value) {
    activeAcc.value.className = activeAcc.value.className.replace(" w3-show", "");
  }
  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show";
    activeAcc.value = x; // Mettez à jour l'accordéon actif
  } else {
    x.className = x.className.replace(" w3-show", "");
    activeAcc.value = null; // Réinitialiser l'accordéon actif
  }
}

function accEveFunc() {
  var x = accEve.value;
  if (activeAcc.value && activeAcc.value !== accEve.value) {
    activeAcc.value.className = activeAcc.value.className.replace(" w3-show", "");
  }
  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show";
    activeAcc.value = x; // Mettez à jour l'accordéon actif
  } else {
    x.className = x.className.replace(" w3-show", "");
    activeAcc.value = null; // Réinitialiser l'accordéon actif
  }
}

function accEquipFunc() {
  var x = accEquip.value;
  if (activeAcc.value && activeAcc.value !== accEquip.value) {
    activeAcc.value.className = activeAcc.value.className.replace(" w3-show", "");
  }
  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show";
    activeAcc.value = x; // Mettez à jour l'accordéon actif
  } else {
    x.className = x.className.replace(" w3-show", "");
    activeAcc.value = null; // Réinitialiser l'accordéon actif
  }
}

// Fonction pour gérer la déconnexion
const handleLogout = () => {
  // Supprime les infos locales
  auth.logout();
  // Vide les infos utilisateur du store
  mainStore.username = null;
  mainStore.userPermissions = {};
};

// Vérifie si l'utilisateur a accès à un modèle donné
const hasPermissionForModel = (modelName) => {
  return computed(() => {
    return (
      mainStore.userPermissions[modelName] &&
      mainStore.userPermissions[modelName].length > 0
    );
  });
};
</script>

<template>
  <div class="w3-center w3-signal-green header-container">
    <div class="title-container">
      <h2>GeoPasto</h2>
      <div class="auth_buttons">
        <div v-if="isAuthenticated">
          <Logout @loggedOut="handleLogout" />
          <!-- Affiche le bouton de déconnexion si l'utilisateur est connecté -->
        </div>
        <div v-else>
          <Login @authenticated="handleAuthenticated" />
          <!-- Affiche le formulaire de connexion si non authentifié -->
        </div>
      </div>
    </div>
    <div class="notification-container">
      <Notification v-if="successMessage" :message="successMessage" type="success" @close="clearSuccessMessage" />
      <Notification v-if="errorMessage" :message="errorMessage" type="error" @close="clearErrorMessage" />
    </div>
  </div>

  <div v-if="isAuthenticated" class="w3-sidebar w3-bar-block w3-light-grey w3-card" style="width: 160px">
    <!-- Accordeon 'référentiels'-->
    <div class="nav-item w3-signal-grey" @click="accRefFunc">
      Référentiels <i class="fa fa-caret-down"></i>
    </div>
    <div ref="accRef" class="w3-hide w3-white w3-card">
      <div v-if="hasPermissionForModel('espece').value" :class="[
        'nav-item w3-signal-grey transparent',
        { active: route.path === '/Especes2' },
      ]">
        <RouterLink to="/Especes2">Espèces</RouterLink>
      </div>
      <div v-if="hasPermissionForModel('production').value" :class="[
        'nav-item w3-signal-grey transparent',
        { active: route.path === '/Productions2' },
      ]">
        <RouterLink to="/Productions2">Productions</RouterLink>
      </div>
      <div v-if="hasPermissionForModel('categorie_pension').value" :class="[
        'nav-item w3-signal-grey transparent',
        { active: route.path === '/CategoriesPension2' },
      ]">
        <RouterLink to="/CategoriesPension2">Catégories de pension</RouterLink>
      </div>
      <div v-if="hasPermissionForModel('categorie_animaux').value" :class="[
        'nav-item w3-signal-grey transparent',
        { active: route.path === '/CategoriesAnimaux2' },
      ]">
        <RouterLink to="/CategoriesAnimaux2">Catégories d'animaux</RouterLink>
      </div>
      <div v-if="hasPermissionForModel('race').value" :class="[
        'nav-item w3-signal-grey transparent',
        { active: route.path === '/Races2' },
      ]">
        <RouterLink to="/Races2">Races</RouterLink>
      </div>
      <div v-if="hasPermissionForModel('typeconvention').value" :class="[
        'nav-item w3-signal-grey transparent',
        { active: route.path === '/TypeConventions2' },
      ]">
        <RouterLink to="/TypeConventions2">Types de convention</RouterLink>
      </div>
      <div :class="[
        'nav-item w3-signal-grey transparent',
        { active: route.path === '/TypeExploitants2' },
      ]">
        <RouterLink to="/TypeExploitants2">Types d'Exploitants</RouterLink>
      </div>
      <div :class="[
        'nav-item w3-signal-grey transparent',
        { active: route.path === '/TypeEquipements2' },
      ]">
        <RouterLink to="/TypeEquipements2">Types d'équipement</RouterLink>
      </div>
      <div :class="[
        'nav-item w3-signal-grey transparent',
        { active: route.path === '/TypeCheptels2' },
      ]">
        <RouterLink to="/TypeCheptels2">Types de cheptel</RouterLink>
      </div>
      <div :class="[
        'nav-item w3-signal-grey transparent',
        { active: route.path === '/TypeMesures2' },
      ]">
        <RouterLink to="/TypeMesures2">Types de mesure</RouterLink>
      </div>
      <div :class="[
        'nav-item w3-signal-grey transparent',
        { active: route.path === '/TypeSuivis2' },
      ]">
        <RouterLink to="/TypeSuivis2">Types de suivi</RouterLink>
      </div>
      <div :class="[
        'nav-item w3-signal-grey transparent',
        { active: route.path === '/TypeEvenements2' },
      ]">
        <RouterLink to="/TypeEvenements2">Types d'événements</RouterLink>
      </div>

    </div>


    <!-- Accordeon 'administratif'-->
    <div class="nav-item w3-signal-yellow" @click="accAdmiFunc">
      Administratif <i class="fa fa-caret-down"></i>
    </div>
    <div ref="accAdmi" class="w3-hide w3-white w3-card">
      <div :class="[
        'nav-item w3-signal-yellow transparent',
        { active: route.path === '/ProprietaireFonciers2' },
      ]">
        <RouterLink to="/ProprietaireFonciers2">Propriétaires</RouterLink>
      </div>
      <!-- Teste les persmissions sur le modèle -->
      <div v-if="hasPermissionForModel('unitepastorale').value" :class="[
        'nav-item w3-signal-yellow transparent',
        { active: route.path === '/UnitePastorales2' },
      ]">
        <RouterLink to="/UnitePastorales2">Unités pastorales 2</RouterLink>
      </div>
      <div v-if="hasPermissionForModel('unitepastorale').value" :class="[
        'nav-item w3-signal-yellow transparent',
        { active: route.path === '/UnitePastorales' },
      ]">
        <RouterLink to="/UnitePastorales">Unités pastorales</RouterLink>
      </div>
    </div>

    <!-- Accordeon 'Exploitation'-->
    <div class="nav-item w3-signal-orange" @click="accExplFunc">
      Exploitation <i class="fa fa-caret-down"></i>
    </div>
    <div ref="accExpl" class="w3-hide w3-white w3-card">
      <!-- Teste les persmissions sur le modèle -->
      <!-- <div v-if="hasPermissionForModel('typeconvention').value" :class="[
        'nav-item w3-signal-orange transparent',
        { active: route.path === '/TypeConventions' },
      ]">
        <RouterLink to="/TypeConventions">Types de convention</RouterLink>
      </div> -->
      <div :class="[
        'nav-item w3-signal-orange transparent',
        { active: route.path === '/Conventions2' },
      ]">
        <RouterLink to="/Conventions2">Conventions d'exploitation 2</RouterLink>
      </div>

      <div :class="[
        'nav-item w3-signal-orange transparent',
        { active: route.path === '/SituationExploitations2' },
      ]">
        <RouterLink to="/SituationExploitations2">Situations d'exploitation  2</RouterLink>
      </div>

      <div :class="[
        'nav-item w3-signal-orange transparent',
        { active: route.path === '/Exploitants2' },
      ]">
        <RouterLink to="/Exploitants2">Exploitants</RouterLink>
      </div>

      <div :class="[
        'nav-item w3-signal-orange transparent',
        { active: route.path === '/Eleveurs2' },
      ]">
        <RouterLink to="/Eleveurs2">Eleveurs</RouterLink>
      </div>

      <div :class="[
        'nav-item w3-signal-orange transparent',
        { active: route.path === '/Subventions2' },
      ]">
        <RouterLink to="/Subventions2">Subventions</RouterLink>
      </div>

      <div :class="[
        'nav-item w3-signal-orange transparent',
        { active: route.path === '/PretAbris' },
      ]">
        <RouterLink to="/PretAbris">Prêts d'abris</RouterLink>
      </div>

      <div :class="[
        'nav-item w3-signal-orange transparent',
        { active: route.path === '/Cheptels2' },
      ]">
        <RouterLink to="/Cheptels2">Cheptels</RouterLink>
      </div>

      <div :class="[
        'nav-item w3-signal-orange transparent',
        { active: route.path === '/Bergers2' },
      ]">
        <RouterLink to="/Bergers2">Bergers</RouterLink>
      </div>

      <div :class="[
        'nav-item w3-signal-orange transparent',
        { active: route.path === '/GardeTroupeaux2' },
      ]">
        <RouterLink to="/GardeTroupeaux2">Gardiennage</RouterLink>
      </div>
    </div>

    <!-- Accordeon 'Plans et Mesures'-->
    <div class="nav-item w3-signal-red" @click="accPlanFunc">
      Plans et Mesures <i class="fa fa-caret-down"></i>
    </div>
    <div ref="accPlan" class="w3-hide w3-white w3-card">
      <div :class="[
        'nav-item w3-signal-red transparent',
        { active: route.path === '/PlanSuivis2' },
      ]">
        <RouterLink to="/PlanSuivis2">Plans par alpage 2</RouterLink>
      </div>

      <div :class="[
        'nav-item w3-signal-red transparent',
        { active: route.path === '/PlanSuivis' },
      ]">
        <RouterLink to="/PlanSuivis">Plans par alpage</RouterLink>
      </div>
      
      <div :class="[
        'nav-item w3-signal-red transparent',
        { active: route.path === '/MesurePlans2' },
      ]">
        <RouterLink to="/MesurePlans2">Mesures de suivi2</RouterLink>
      </div>
      <div :class="[
        'nav-item w3-signal-red transparent',
        { active: route.path === '/MesurePlans' },
      ]">
        <RouterLink to="/MesurePlans">Mesures de suivi</RouterLink>
      </div>

      <div :class="[
        'nav-item w3-signal-red transparent',
        { active: route.path === '/MesurePlans' },
      ]">
        <RouterLink to="/MesurePlans">Mesures de suivi</RouterLink>
      </div>
    </div>

    <!-- Accordeon 'Evénements'-->
    <div class="nav-item w3-signal-violet" @click="accEveFunc">
      Evénements <i class="fa fa-caret-down"></i>
    </div>
    <div ref="accEve" class="w3-hide w3-white w3-card">
      
      <div :class="[
        'nav-item w3-signal-violet transparent',
        { active: route.path === '/Evenements' },
      ]">
        <RouterLink to="/Evenements">Evénements</RouterLink>
      </div>
      <div :class="[
        'nav-item w3-signal-violet transparent',
        { active: route.path === '/Evenements2' },
      ]">
        <RouterLink to="/Evenements2">Evénements (modal CRUD)</RouterLink>
      </div>
      <div :class="[
        'nav-item w3-signal-violet transparent',
        { active: route.path === '/Evenement/create-map' },
      ]">
        <RouterLink to="/Evenement/create-map">Ajouter événement (carte)</RouterLink>
      </div>
    </div>

    <!-- Accordeon 'Equipements'-->
    <div class="nav-item w3-signal-blue" @click="accEquipFunc">
      Equipements <i class="fa fa-caret-down"></i>
    </div>
    <div ref="accEquip" class="w3-hide w3-white w3-card">
      
      <div :class="[
        'nav-item w3-signal-blue transparent',
        { active: route.path === '/Logements' },
      ]">
        <RouterLink to="/Logements">Logements</RouterLink>
      </div>
      <div :class="[
        'nav-item w3-signal-blue transparent',
        { active: route.path === '/AbriUrgences2' },
      ]">
        <RouterLink to="/AbriUrgences2">Abris d'urgence</RouterLink>
      </div>
      <div :class="[
        'nav-item w3-signal-blue transparent',
        { active: route.path === '/Commodites2' },
      ]">
        <RouterLink to="/Commodites2">Commodites</RouterLink>
      </div>
    </div>
  </div>

  <div v-if="isAuthenticated" class="w3-container" style="margin-left: 160px">
    <RouterView />
  </div>
  <div v-else>
    <div class="w3-center">
      <h2>Veuillez vous connecter pour accéder à l'application</h2>
    </div>
  </div>
</template>

<style>
.header-container {
  position: relative;
  text-align: center;
}

.title-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-container h1 {
  margin: 0;
  flex-grow: 1;
  text-align: center;
}

.auth-buttons {
  display: flex;
  align-items: center;
}

.notification-container {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 1000;
  width: 350px;
  /* Adjust as needed */
}

.notification-container>div {
  position: absolute;
  top: 0;
  right: 0;
  z-index: 1000;
  width: 350px;
  /* Adjust as needed */
}

.error-message {
  color: red;
  font-weight: bold;
  padding: 10px;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  margin-bottom: 20px;
}

.success-message {
  color: green;
  font-weight: bold;
  padding: 10px;
  background-color: #dff0d8;
  border: 1px solid #d6e9c6;
  border-radius: 4px;
  margin-bottom: 20px;
}

.nav-container {
  display: flex;
  /* flex-wrap: wrap; */
  justify-content: space-between;
  background-color: #2196f3;
  /* Couleur de fond de la barre de navigation */
  padding: 0;
  /* Espacement intérieur pour créer une marge uniforme */
}

.nav-item {
  flex: 1 0 auto;
  /* Chaque élément prendra autant d'espace que nécessaire */
  display: flex;
  justify-content: center;
  align-items: center;
  height: 50px;
  max-height: 80px;
  padding: 0 0 !important;
  /* margin: 5px; Espacement entre les éléments */
}

.nav-item a {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  text-align: center;
  color: white;
  text-decoration: none;
  /* padding: 10px; */
}

.nav-item a:hover {
  background-color: #ddd;
  color: black;
}

.nav-item.active a {
  color: black;
  /* Couleur du texte en noir */
  font-weight: bold;
  /* Texte en gras */
  border: 1px solid white;
  /* Bordure blanche fine */
}

.transparent {
  opacity: 0.7;
}
</style>
