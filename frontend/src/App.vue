<script setup>
import { computed, ref, onMounted, onBeforeUnmount, nextTick, watch } from "vue";
import { RouterLink, RouterView, useRoute, useRouter } from "vue-router";

import Notification from "./components/Notification.vue";
import NotificationContainer from "./components/NotificationContainer.vue";
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
const menuOpen = ref(false);
const headerRef = ref(null);
const headerHeight = ref(88);

const updateHeaderHeight = () => {
  headerHeight.value = headerRef.value?.offsetHeight || 88;
};

const activeAccordion = ref(null);

const clearSuccessMessage = () => {
  mainStore.setSuccessMessage("");
};

const clearErrorMessage = () => {
  mainStore.setErrorMessage("");
};

const toggleAccordion = (sectionKey) => {
  activeAccordion.value = activeAccordion.value === sectionKey ? null : sectionKey;
};

const isAccordionOpen = (sectionKey) => {
  return activeAccordion.value === sectionKey;
};

const toggleMenu = () => {
  menuOpen.value = !menuOpen.value;
};

const closeMenu = () => {
  menuOpen.value = false;
};

const handleDrawerClick = (event) => {
  if (event.target.closest("a")) {
    closeMenu();
  }
};

// Fonction pour gérer la déconnexion
const handleLogout = () => {
  // Nettoie la session sans forcer de rechargement de page.
  mainStore.logout();
  mainStore.username = null;
  mainStore.userPermissions = {};
  delete auth.axiosInstance.defaults.headers.common.Authorization;
  closeMenu();

  if (route.path !== "/") {
    router.replace("/");
  }
};

// Vérifie si l'utilisateur a accès à un modèle donné
const hasPermissionForModel = (modelName) => {
  return Boolean(
    mainStore.userPermissions[modelName] &&
    mainStore.userPermissions[modelName].length > 0
  );
};

onMounted(async () => {
  await nextTick();
  updateHeaderHeight();
  window.addEventListener("resize", updateHeaderHeight);

  if (isAuthenticated.value) {
    await initializeUserData();
  }
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", updateHeaderHeight);
});

watch(
  () => isAuthenticated.value,
  async (connected) => {
    if (connected) {
      await initializeUserData();
    }
  }
);

watch(
  () => route.path,
  () => {
    closeMenu();
  }
);
</script>

<template>
  <div class="app-root" :style="{ '--header-height': `${headerHeight}px` }">
    <template v-if="!isAuthenticated">
      <div class="login-page">
        <div class="login-panel w3-card-4">
          <div class="login-branding">
            <img src="/geopasto_logo.png" alt="Logo GeoPasto" class="login-logo app-logo" />
            <img src="/PNV_logo.png" alt="Logo client" class="login-logo client-logo" />
          </div>
          <!-- <h2>GeoPasto</h2> -->
          <p>Connectez-vous pour acceder a l'application.</p>
          <Login />
        </div>
        <div class="notification-container">
          <Notification
            v-if="successMessage"
            :message="successMessage"
            type="success"
            @close="clearSuccessMessage"
          />
          <Notification
            v-if="errorMessage"
            :message="errorMessage"
            type="error"
            @close="clearErrorMessage"
          />
        </div>
      </div>
    </template>

    <template v-else>
      <header ref="headerRef" class="app-header w3-signal-green">
        <div class="header-left">
          <button
            type="button"
            class="burger-btn"
            @click="toggleMenu"
            :aria-expanded="menuOpen"
            aria-label="Ouvrir le menu"
          >
            <span></span>
            <span></span>
            <span></span>
          </button>
          <img src="/geopasto_logo.png" alt="Logo GeoPasto" class="app-logo" />
          <img src="/PNV_logo.png" alt="Logo client" class="client-logo" />
          <!-- <h2>GeoPasto</h2> -->
        </div>
        <div class="header-right">
          <div class="user-info header-pill">
            Utilisateur connecté :
            <strong>{{ mainStore.username || mainStore.user?.username || "inconnu" }}</strong>
          </div>
          <Logout class="header-pill logout-chip" @loggedOut="handleLogout" />
        </div>
        <div class="notification-container">
          <Notification
            v-if="successMessage"
            :message="successMessage"
            type="success"
            @close="clearSuccessMessage"
          />
          <Notification
            v-if="errorMessage"
            :message="errorMessage"
            type="error"
            @close="clearErrorMessage"
          />
        </div>
      </header>

      <Transition name="menu-fade">
        <div v-if="menuOpen" class="menu-backdrop" @click="closeMenu"></div>
      </Transition>

      <Transition name="menu-slide">
        <aside
          v-if="menuOpen"
          class="app-drawer w3-bar-block w3-light-grey w3-card"
          @click="handleDrawerClick"
        >
          <div class="drawer-header">
            <strong>Menu</strong>
            <button type="button" class="drawer-close" @click="closeMenu" aria-label="Fermer le menu">
              x
            </button>
          </div>

          <!-- Accordeon 'referentiels'-->
          <div class="nav-item w3-signal-grey" @click="toggleAccordion('ref')">
            Referentiels
            <i class="fa fa-caret-down accordion-caret" :class="{ open: isAccordionOpen('ref') }"></i>
          </div>
          <div v-show="isAccordionOpen('ref')" class="w3-white w3-card">
            <div
              v-if="hasPermissionForModel('espece')"
              :class="['nav-item w3-signal-grey transparent', { active: route.path === '/Especes2' }]"
            >
              <RouterLink to="/Especes2">Especes</RouterLink>
            </div>
            <div
              v-if="hasPermissionForModel('production')"
              :class="['nav-item w3-signal-grey transparent', { active: route.path === '/Productions2' }]"
            >
              <RouterLink to="/Productions2">Productions</RouterLink>
            </div>
            <div
              v-if="hasPermissionForModel('categorie_pension')"
              :class="['nav-item w3-signal-grey transparent', { active: route.path === '/CategoriesPension2' }]"
            >
              <RouterLink to="/CategoriesPension2">Categories de pension</RouterLink>
            </div>
            <div
              v-if="hasPermissionForModel('categorie_animaux')"
              :class="['nav-item w3-signal-grey transparent', { active: route.path === '/CategoriesAnimaux2' }]"
            >
              <RouterLink to="/CategoriesAnimaux2">Categories d'animaux</RouterLink>
            </div>
            <div
              v-if="hasPermissionForModel('race')"
              :class="['nav-item w3-signal-grey transparent', { active: route.path === '/Races2' }]"
            >
              <RouterLink to="/Races2">Races</RouterLink>
            </div>
            <div
              v-if="hasPermissionForModel('typeconvention')"
              :class="['nav-item w3-signal-grey transparent', { active: route.path === '/TypeConventions2' }]"
            >
              <RouterLink to="/TypeConventions2">Types de convention</RouterLink>
            </div>
            <div :class="['nav-item w3-signal-grey transparent', { active: route.path === '/TypeExploitants2' }]">
              <RouterLink to="/TypeExploitants2">Types d'Exploitants</RouterLink>
            </div>
            <div :class="['nav-item w3-signal-grey transparent', { active: route.path === '/TypeEquipements2' }]">
              <RouterLink to="/TypeEquipements2">Types d'equipement</RouterLink>
            </div>
            <div :class="['nav-item w3-signal-grey transparent', { active: route.path === '/TypeCheptels2' }]">
              <RouterLink to="/TypeCheptels2">Types de cheptel</RouterLink>
            </div>
            <div :class="['nav-item w3-signal-grey transparent', { active: route.path === '/TypeMesures2' }]">
              <RouterLink to="/TypeMesures2">Types de mesure</RouterLink>
            </div>
            <div :class="['nav-item w3-signal-grey transparent', { active: route.path === '/TypeSuivis2' }]">
              <RouterLink to="/TypeSuivis2">Types de suivi</RouterLink>
            </div>
            <div :class="['nav-item w3-signal-grey transparent', { active: route.path === '/TypeEvenements2' }]">
              <RouterLink to="/TypeEvenements2">Types d'evenements</RouterLink>
            </div>
          </div>

          <!-- Accordeon 'administratif'-->
          <div class="nav-item w3-signal-yellow" @click="toggleAccordion('admi')">
            Administratif
            <i class="fa fa-caret-down accordion-caret" :class="{ open: isAccordionOpen('admi') }"></i>
          </div>
          <div v-show="isAccordionOpen('admi')" class="w3-white w3-card">
            <div
              :class="['nav-item w3-signal-yellow transparent', { active: route.path === '/ProprietaireFonciers2' }]"
            >
              <RouterLink to="/ProprietaireFonciers2">Proprietaires</RouterLink>
            </div>
            <div
              v-if="hasPermissionForModel('unitepastorale')"
              :class="['nav-item w3-signal-yellow transparent', { active: route.path === '/UnitePastorales2' }]"
            >
              <RouterLink to="/unite-pastorale">Unites pastorales</RouterLink>
            </div>
            <!-- <div
              v-if="hasPermissionForModel('unitepastorale')"
              :class="['nav-item w3-signal-yellow transparent', { active: route.path === '/UnitePastorales' }]"
            >
              <RouterLink to="/UnitePastorales">Unites pastorales</RouterLink>
            </div> -->
          </div>

          <!-- Accordeon 'Exploitation'-->
          <div class="nav-item w3-signal-orange" @click="toggleAccordion('expl')">
            Exploitation
            <i class="fa fa-caret-down accordion-caret" :class="{ open: isAccordionOpen('expl') }"></i>
          </div>
          <div v-show="isAccordionOpen('expl')" class="w3-white w3-card">
            <div :class="['nav-item w3-signal-orange transparent', { active: route.path === '/Conventions2' }]">
              <RouterLink to="/Conventions2">Conventions d'exploitation 2</RouterLink>
            </div>

            <div
              :class="['nav-item w3-signal-orange transparent', { active: route.path === '/SituationExploitations2' }]"
            >
              <RouterLink to="/SituationExploitations2">Situations d'exploitation 2</RouterLink>
            </div>

            <div :class="['nav-item w3-signal-orange transparent', { active: route.path === '/Exploitants2' }]">
              <RouterLink to="/Exploitants2">Exploitants</RouterLink>
            </div>

            <div :class="['nav-item w3-signal-orange transparent', { active: route.path === '/Eleveurs2' }]">
              <RouterLink to="/Eleveurs2">Eleveurs</RouterLink>
            </div>

            <div :class="['nav-item w3-signal-orange transparent', { active: route.path === '/Subventions2' }]">
              <RouterLink to="/Subventions2">Subventions</RouterLink>
            </div>

            <div :class="['nav-item w3-signal-orange transparent', { active: route.path === '/PretAbris' }]">
              <RouterLink to="/PretAbris">Prets d'abris</RouterLink>
            </div>

            <div :class="['nav-item w3-signal-orange transparent', { active: route.path === '/Cheptels2' }]">
              <RouterLink to="/Cheptels2">Cheptels</RouterLink>
            </div>

            <div :class="['nav-item w3-signal-orange transparent', { active: route.path === '/Bergers2' }]">
              <RouterLink to="/Bergers2">Bergers</RouterLink>
            </div>

            <div :class="['nav-item w3-signal-orange transparent', { active: route.path === '/GardeTroupeaux2' }]">
              <RouterLink to="/GardeTroupeaux2">Gardiennage</RouterLink>
            </div>
          </div>

          <!-- Accordeon 'Plans et Mesures'-->
          <div class="nav-item w3-signal-red" @click="toggleAccordion('plan')">
            Plans et Mesures
            <i class="fa fa-caret-down accordion-caret" :class="{ open: isAccordionOpen('plan') }"></i>
          </div>
          <div v-show="isAccordionOpen('plan')" class="w3-white w3-card">
            <div :class="['nav-item w3-signal-red transparent', { active: route.path === '/PlanSuivis2' }]">
              <RouterLink to="/PlanSuivis2">Plans par alpage 2</RouterLink>
            </div>

            <div :class="['nav-item w3-signal-red transparent', { active: route.path === '/PlanSuivis' }]">
              <RouterLink to="/PlanSuivis">Plans par alpage</RouterLink>
            </div>

            <div :class="['nav-item w3-signal-red transparent', { active: route.path === '/MesurePlans2' }]">
              <RouterLink to="/MesurePlans2">Mesures de suivi 2</RouterLink>
            </div>
            <div :class="['nav-item w3-signal-red transparent', { active: route.path === '/MesurePlans' }]">
              <RouterLink to="/MesurePlans">Mesures de suivi</RouterLink>
            </div>
          </div>

          <!-- Accordeon 'Evenements'-->
          <div class="nav-item w3-signal-violet" @click="toggleAccordion('eve')">
            Evenements
            <i class="fa fa-caret-down accordion-caret" :class="{ open: isAccordionOpen('eve') }"></i>
          </div>
          <div v-show="isAccordionOpen('eve')" class="w3-white w3-card">
            <!-- <div :class="['nav-item w3-signal-violet transparent', { active: route.path === '/Evenements' }]">
              <RouterLink to="/Evenements">Evenements</RouterLink>
            </div> -->
            <div :class="['nav-item w3-signal-violet transparent', { active: route.path === '/Evenements2' }]">
              <RouterLink to="/Evenements2">Evenements</RouterLink>
            </div>
            <!-- <div
              :class="['nav-item w3-signal-violet transparent', { active: route.path === '/Evenement/create-map' }]"
            >
              <RouterLink to="/Evenement/create-map">Ajouter evenement (carte)</RouterLink>
            </div> -->
          </div>

          <!-- Accordeon 'Equipements'-->
          <div class="nav-item w3-signal-blue" @click="toggleAccordion('equip')">
            Equipements
            <i class="fa fa-caret-down accordion-caret" :class="{ open: isAccordionOpen('equip') }"></i>
          </div>
          <div v-show="isAccordionOpen('equip')" class="w3-white w3-card">
            <div :class="['nav-item w3-signal-blue transparent', { active: route.path === '/Logements' }]">
              <RouterLink to="/Logements">Logements</RouterLink>
            </div>
            <div :class="['nav-item w3-signal-blue transparent', { active: route.path === '/AbriUrgences2' }]">
              <RouterLink to="/AbriUrgences2">Abris d'urgence</RouterLink>
            </div>
            <div :class="['nav-item w3-signal-blue transparent', { active: route.path === '/Commodites2' }]">
              <RouterLink to="/Commodites2">Commodites</RouterLink>
            </div>
          </div>
        </aside>
      </Transition>

      <div :class="['app-main', { 'drawer-open': menuOpen }]">
        <main class="app-content">
          <RouterView />
          <NotificationContainer />
        </main>
      </div>
    </template>
  </div>
</template>

<style>
.app-root {
  --drawer-width: min(350px, 88vw);
  min-height: 100vh;
}

.login-page {
  min-height: 100vh;
  background-image: linear-gradient(rgba(0, 0, 0, 0.35), rgba(0, 0, 0, 0.45)),
    url('/geopasto_accueil.jpg');
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
}

.login-panel {
  width: min(450px, 95vw);
  background: rgba(255, 255, 255, 0.5);
  padding: 28px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(0px);
}

.login-panel h2 {
  margin: 10px 0 6px;
  text-align: center;
}

.login-panel p {
  margin: 0 0 16px;
  text-align: center;
  color: #444;
}

.login-branding {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 14px;
}

.login-logo {
  object-fit: contain;
  border-radius: 8px;
}

.login-branding .app-logo,
.login-branding .client-logo {
  height: 96px;
  width: auto;
}

.header-left .app-logo,
.header-left .client-logo {
  height: 48px;
  width: auto;
  object-fit: contain;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 88px;
  padding: 12px 20px;
  position: relative;
  color: #fff;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.burger-btn {
  width: 42px;
  height: 42px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.18);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.burger-btn:hover {
  background: rgba(0, 0, 0, 0.3);
}

.burger-btn span {
  width: 20px;
  height: 2px;
  background: #fff;
}

.header-left h2 {
  margin: 0;
  font-size: 1.6rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-pill {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.45);
  min-height: 40px;
  padding: 8px 14px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  /* transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.15s ease; */
}

.user-info {
  color: #fff;
  gap: 6px;
}

.logout-chip {
  color: #fff;
  background: rgba(235, 87, 87, 0.35);
  border-radius: 999px;
  cursor: pointer;
  font-weight: 600;
}

.logout-chip:hover {
  background: rgba(235, 87, 87, 0.5);
  border-color: rgba(255, 255, 255, 0.72);
  /* transform: translateY(-1px); */
}

.logout-chip:focus-visible {
  outline: 2px solid rgba(255, 255, 255, 0.9);
  outline-offset: 2px;
}

.notification-container {
  position: absolute;
  top: 12px;
  right: 20px;
  z-index: 1000;
  width: min(360px, 92vw);
}

.notification-container {
  position: fixed;
  z-index: 999999;
}

.notification-container>div {
  position: absolute;
  top: 0;
  right: 0;
  z-index: 1000;
  width: min(360px, 92vw);
}

.app-main {
  min-height: calc(100vh - var(--header-height, 88px));
  width: 100%;
  margin-left: 0;
  transition: margin-left 0.24s ease, width 0.24s ease;
}

.app-main.drawer-open {
  margin-left: var(--drawer-width);
  width: calc(100% - var(--drawer-width));
}

.app-drawer {
  position: fixed;
  top: var(--header-height, 88px);
  left: 0;
  width: var(--drawer-width);
  height: calc(100vh - var(--header-height, 88px));
  overflow-y: auto;
  z-index: 2000;
  box-shadow: 12px 0 28px rgba(0, 0, 0, 0.25);
}

.drawer-header {
  position: sticky;
  top: 0;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: #f0f0f0;
  border-bottom: 1px solid #ddd;
}

.drawer-close {
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #ddd;
  cursor: pointer;
  font-weight: 700;
}

.menu-backdrop {
  position: fixed;
  top: var(--header-height, 88px);
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.35);
  z-index: 1900;
}

.app-content {
  width: 100%;
  padding: 16px;
}

.nav-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 44px;
  padding: 0 10px !important;
  cursor: pointer;
}

.nav-item a {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  text-align: center;
  padding: 8px;
  color: white;
  text-decoration: none;
}

/* .menu-slide-enter-active,
.menu-slide-leave-active {
  transition: transform 0.24s ease;
}

.menu-slide-enter-from,
.menu-slide-leave-to {
  transform: translateX(-100%);
} */

.menu-fade-enter-active,
.menu-fade-leave-active {
  transition: opacity 0.2s ease;
}

.menu-fade-enter-from,
.menu-fade-leave-to {
  opacity: 0;
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

.accordion-caret {
  margin-left: 8px;
  /* transition: transform 0.2s ease; */
}

/* .accordion-caret.open {
  transform: rotate(180deg);
} */

@media (max-width: 1024px) {
  .header-left h2 {
    font-size: 1.3rem;
  }

  .header-right {
    margin-top: 8px;
  }

  .app-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
    padding-right: 20px;
  }

  .header-left {
    justify-content: flex-start;
  }

  .app-main.drawer-open {
    margin-left: 0;
    width: 100%;
  }

  .notification-container {
    position: static;
    width: 100%;
  }

  .notification-container > div {
    position: static;
    width: 100%;
  }
}
</style>
