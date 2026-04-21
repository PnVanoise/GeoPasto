import { createRouter, createWebHistory } from 'vue-router'
import { useMainStore } from '../store'

import Login from '../components/Login.vue'

import EleveurList2 from '../components/EleveurList2.vue'
import ExploitantList2 from '../components/ExploitantList2.vue'
import SubventionList2 from '../components/SubventionList2.vue'
import AbriDUrgenceList2 from '../components/AbriDUrgenceList2.vue'
import EspeceList2 from '../components/EspeceList2.vue'
import ProductionList2 from '../components/ProductionList2.vue'
import CategoriePensionList2 from '../components/CategoriePensionList2.vue'
import CategorieAnimauxList2 from '../components/CategorieAnimauxList2.vue'
import RaceList2 from '../components/RaceList2.vue'
import BergerList2 from '../components/BergerList2.vue'
import GardeTroupeauList2 from '../components/GardeTroupeauList2.vue'
import CommoditeList2 from '../components/CommoditeList2.vue'
import TypeDExploitantList2 from '../components/TypeDExploitantList2.vue'
import TypeEquipementList2 from '../components/TypeEquipementList2.vue'
import TypeDeConventionList2 from '../components/TypeDeConventionList2.vue'
import TypeCheptelList2 from '../components/TypeCheptelList2.vue'
import TypeDeSuiviList2 from '../components/TypeDeSuiviList2.vue'
import TypeEvenementList2 from '../components/TypeEvenementList2.vue'
import CheptelList2 from '../components/CheptelList2.vue'
import TypeDeMesureList2 from '../components/TypeDeMesureList2.vue'

import ConventionList2 from '../components/ConventionList2.vue'


import UnitePastoraleList2 from '../components/UnitePastoraleList2.vue'
import UnitePastoraleList from '../components/UnitePastoraleList.vue'
import UnitePastoraleAdd from '../components/UnitePastoraleAdd.vue'
import UnitePastoraleEdit from '../components/UnitePastoraleEdit.vue'

import ProprietaireFoncierList2 from '../components/ProprietaireFoncierList2.vue'

import UPProprietaireList from '../components/UPProprietaireList.vue'
import UPProprietaireAdd from '../components/UPProprietaireAdd.vue'
import UPProprietaireEdit from '../components/UPProprietaireEdit.vue'

import QuartierPastoList from '../components/QuartierPastoList.vue'
import QuartierPastoAdd from '../components/QuartierPastoAdd.vue'
import QuartierPastoEdit from '../components/QuartierPastoEdit.vue'

import PlanDeSuiviList2 from '../components/PlanDeSuiviList2.vue'
import PlanDeSuiviList from '../components/PlanDeSuiviList.vue'
import PlanDeSuiviAdd from '../components/PlanDeSuiviAdd.vue'
import PlanDeSuiviEdit from '../components/PlanDeSuiviEdit.vue'

import SituationExploitationList2 from '../components/SituationExploitationList2.vue'

import ExploiterList from '../components/ExploiterList.vue'
import ExploiterAdd from '../components/ExploiterAdd.vue'
import ExploiterEdit from '../components/ExploiterEdit.vue'

import MesureDePlanList2 from '../components/MesureDePlanList2.vue'
import MesureDePlanList from '../components/MesureDePlanList.vue'
import MesureDePlanAdd from '../components/MesureDePlanAdd.vue'
import MesureDePlanEdit from '../components/MesureDePlanEdit.vue'

import AbriDUrgenceList from '../components/AbriDUrgenceList.vue'
import AbriDUrgenceAdd from '../components/AbriDUrgenceAdd.vue'
import AbriDUrgenceEdit from '../components/AbriDUrgenceEdit.vue'

import PretAbriList from '../components/PretAbriList.vue'
import PretAbriAdd from '../components/PretAbriAdd.vue'
import PretAbriEdit from '../components/PretAbriEdit.vue'

import RucheList from '../components/RucheList.vue'
import RucheAdd from '../components/RucheAdd.vue'
import RucheEdit from '../components/RucheEdit.vue'

import EvenementEdit from '../components/EvenementEdit.vue'
import EvenementAdd from '../components/EvenementAdd.vue'
import EvenementList from '../components/EvenementList.vue'
import EventForm from '../components/EventForm.vue'
import EventList2 from '../components/EventList2.vue'

import LogementCommoditeList from '../components/LogementCommoditeList.vue'
import LogementCommoditeAdd from '../components/LogementCommoditeAdd.vue'
import LogementCommoditeEdit from '../components/LogementCommoditeEdit.vue'

import LogementList from '../components/LogementList.vue'
import LogementEdit from '../components/LogementEdit.vue'
import LogementAdd from '../components/LogementAdd.vue'

import EquipementList from '../components/EquipementList.vue'
import EquipementEdit from '../components/EquipementEdit.vue'
import EquipementAdd from '../components/EquipementAdd.vue'

import QuartieralpageView from '../components/QuartieralpageView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: UnitePastoraleList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/UnitePastorales2',
      name: 'unitepastorales2',
      component: UnitePastoraleList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/UnitePastorales',
      name: 'unitepastorales',
      component: UnitePastoraleList,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/UnitePastorale/add',
      name: 'addUP',
      component: UnitePastoraleAdd
    },
    {
      path: '/UnitePastorale/edit/:id',
      name: 'editUP',
      component: UnitePastoraleEdit
    },
    {
      path: '/ProprietaireFonciers2',
      name: 'proprietairefonciers2',
      component: ProprietaireFoncierList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/UPProprietaires',
      name: 'upproprietaires',
      component: UPProprietaireList,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/UPProprietaire/add',
      name: 'addUpproprietaire',
      component: UPProprietaireAdd,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/UPProprietaire/add/:UPId',
      name: 'addUPProprWithUPId',
      component: UPProprietaireAdd,
      props: true
    },
    {
      path: '/UPProprietaire/edit/:id',
      name: 'editUPPropr',
      component: UPProprietaireEdit,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/QuartierPastos',
      name: 'quartiers',
      component: QuartierPastoList,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/QuartierPastos/:up_id',
      name: 'quartiersUP',
      component: QuartierPastoList,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/QuartierPasto/add',
      name: 'addQuartier',
      component: QuartierPastoAdd,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/QuartierPasto/add/:UPId',
      name: 'addQuartierWithUPId',
      component: QuartierPastoAdd,
      props: true
    },
    {
      path: '/QuartierPasto/edit/:id',
      name: 'editQuartier',
      component: QuartierPastoEdit,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/TypeSuivis2',
      name: 'typesuivis2',
      component: TypeDeSuiviList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/PlanSuivis2',
      name: 'plansuivis2',
      component: PlanDeSuiviList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/PlanSuivis',
      name: 'plansuivis',
      component: PlanDeSuiviList,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/PlanSuivi/add',
      name: 'addPlanSuivi',
      component: PlanDeSuiviAdd,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/PlanSuivi/edit/:id',
      name: 'editPlanSuivi',
      component: PlanDeSuiviEdit,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/TypeMesures2',
      name: 'typeMesures2',
      component: TypeDeMesureList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/MesurePlans2',
      name: 'mesurePlans2',
      component: MesureDePlanList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/MesurePlans',
      name: 'mesurePlans',
      component: MesureDePlanList,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/MesurePlan/add',
      name: 'addMesurePlan',
      component: MesureDePlanAdd,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/MesurePlan/edit/:id',
      name: 'editMesurePlan',
      component: MesureDePlanEdit,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/TypeConventions2',
      name: 'typeconventions2',
      component: TypeDeConventionList2,
    },
    {
      path: '/Conventions2',
      name: 'conventions2',
      component: ConventionList2,
    },
    {
      path: '/SituationExploitations2',
      name: 'situations2',
      component: SituationExploitationList2,
    },
    {
      path: '/Exploiters',
      name: 'exploiters',
      component: ExploiterList,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Exploiter/add',
      name: 'addExploiter',
      component: ExploiterAdd,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Exploiter/edit/:id',
      name: 'editExploiter',
      component: ExploiterEdit,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Eleveurs2',
      name: 'eleveurs2',
      component: EleveurList2,
      meta: { requiresAuth: true },  // Route protégée
    },

    {
      path: '/TypeExploitants2',
      name: 'typeExploitants2',
      component: TypeDExploitantList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Exploitants2',
      name: 'exploitants2',
      component: ExploitantList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Subventions2',
      name: 'subventions2',
      component: SubventionList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/AbriUrgences',
      name: 'abris',
      component: AbriDUrgenceList,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/AbriUrgence/add',
      name: 'addAbriUrgence',
      component: AbriDUrgenceAdd,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/AbriUrgence/edit/:id',
      name: 'editAbriUrgence',
      component: AbriDUrgenceEdit,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/AbriUrgences2',
      name: 'abris2',
      component: AbriDUrgenceList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/PretAbris',
      name: 'prets',
      component: PretAbriList,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/PretAbri/add',
      name: 'addPret',
      component: PretAbriAdd,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/PretAbri/edit/:id',
      name: 'editPret',
      component: PretAbriEdit,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Especes2',
      name: 'especes2',
      component: EspeceList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path : "/Productions2",
      name : "productions2",
      component : ProductionList2
    },
    {
      path: '/CategoriesPension2',
      name: 'categories_pension2',
      component: CategoriePensionList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/CategoriesAnimaux2',
      name: 'categories_animaux2',
      component: CategorieAnimauxList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Races2',
      name: 'races2',
      component: RaceList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Bergers2',
      name: 'bergers2',
      component: BergerList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/TypeCheptels2',
      name: 'typecheptels2',
      component: TypeCheptelList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/GardeTroupeaux2',
      name: 'gardetroupeaux2',
      component: GardeTroupeauList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Cheptels2',
      name: 'cheptels2',
      component: CheptelList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    // {
    //   path: '/Elevers2',
    //   name: 'elevers2',
    //   component: EleverList2,
    //   meta: { requiresAuth: true },  // Route protégée
    // },
    // {
    //   path: '/Elever/add',
    //   name: 'addElever',
    //   component: EleverAdd,
    //   meta: { requiresAuth: true },  // Route protégée
    // },
    // {
    //   // @param : situation id (pour enregistrement cheptel)
    //   // @param : exploitant id (pour sélection des éleveurs)
    //   path: '/Elever/add/:situId/:explId',
    //   name: 'addEleverWithSituId',
    //   component: EleverAdd,
    //   meta: { requiresAuth: true },  // Route protégée
    //   props: true
    // },
    // {
    //   path: '/Elever/edit/:id',
    //   name: 'editElever',
    //   component: EleverEdit,
    //   meta: { requiresAuth: true },  // Route protégée
    // },
    {
      path: '/Ruches',
      name: 'ruches',
      component: RucheList,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Ruche/add',
      name: 'addRuche',
      component: RucheAdd,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Ruche/edit/:id',
      name: 'editRuche',
      component: RucheEdit,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Evenements',
      name: 'evenements',
      component: EvenementList,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Evenements2',
      name: 'evenements2',
      component: EventList2,
      meta: { requiresAuth: true },
    },
    {
      path: '/Evenement/add',
      name: 'addEvenement',
      component: EvenementAdd,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Evenement/create-map',
      name: 'addEvenementMap',
      component: EventForm,
      meta: { requiresAuth: true },
    },
    {
      path: '/Evenement/edit/:id',
      name: 'editEvenement',
      component: EvenementEdit,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/TypeEvenements2',
      name: 'typeevenements2',
      component: TypeEvenementList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/TypeEquipements2',
      name: 'typeequipements2',
      component: TypeEquipementList2,
      meta: {
        modelName: 'typeequipement',
        requiredPermission: 'view_typeequipement',
        requiresAuth: true
      },  // Route protégée
    },
    {
      path: '/Logements',
      name: 'logements',
      component: LogementList,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Logement/add',
      name: 'addLogement',
      component: LogementAdd
    },
    {
      path: '/Logement/edit/:id',
      name: 'editLogement',
      component: LogementEdit
    },
    {
      path: '/Commodites2',
      name: 'commodites2',
      component: CommoditeList2,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/LogementCommodites',
      name: 'logementCommodites',
      component: LogementCommoditeList,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/LogementCommodite/add',
      name: 'addLogementCommodite',
      component: LogementCommoditeAdd,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/LogementCommodite/add/:logementId',
      name: 'addLogementCommoditeWithLogementId',
      component: LogementCommoditeAdd,
      props: true
    },
    {
      path: '/LogementCommodite/edit/:id',
      name: 'editLogementCommodite',
      component: LogementCommoditeEdit
    },
    {
      path: '/Equipements',
      name: 'equipements',
      component: EquipementList,
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Equipement/add',
      name: 'addEquipement',
      component: EquipementAdd
    },
    {
      path: '/Equipement/edit/:id',
      name: 'editEquipement',
      component: EquipementEdit
    },
    {
      path: '/QuartieralpageView/:id',
      name: 'quartieralpageview',
      component: QuartieralpageView
    },
    {
      path: '/LogementList',
      name: 'LogementList',
      component: LogementList
    },
  ]
});

router.beforeEach(async (to, from, next) => {
  const mainStore = useMainStore();

  // 🔒 Vérifie d'abord l'authentification
  const storedUser = localStorage.getItem('user')
  if (to.meta.requiresAuth && !storedUser) {
    //mainStore.setErrorMessage("Vous devez être connecté pour accéder à cette page.")
    return next({ name: 'Login' })
  }

  // 🛑 si route protégée avec permissions spécifiques
  const requiredPermission = to.meta?.requiredPermission;
  const modelName = to.meta?.modelName;
  const liste = to.meta?.liste;

  if (!mainStore.userPermissions || Object.keys(mainStore.userPermissions).length === 0) {
    // console.log("⚠️ Permissions non chargées, récupération en cours...");
    await mainStore.fetchUserPermissions();
  }

  if (requiredPermission && modelName) {
    const hasPermission = mainStore.hasPermission(modelName, requiredPermission)
    console.log("modelname:", modelName);
    console.log("reqperm:", requiredPermission);

    if (!hasPermission) {
      // Afficher un message d’erreur sans déconnexion
      mainStore.setErrorMessage("Vous n’avez pas les droits nécessaires pour accéder à cette page.")
      console.log(modelName, requiredPermission);
      // Rester sur la page précédente ou aller à une route "sûre"
      console.log('liste', liste);
      return next(false);
    }
  }

  next();
});


export default router;
