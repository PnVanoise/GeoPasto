import { createRouter, createWebHistory } from 'vue-router'
import { useMainStore } from '../store'

import Login from '../components/auth/Login.vue'

import EleveurList2 from '../features/eleveur/EleveurList2.vue'
import ExploitantList2 from '../features/exploitant/ExploitantList2.vue'
import SubventionList2 from '../features/subvention/SubventionList2.vue'
import AbriDUrgenceList2 from '../features/abri_urgence/AbriDUrgenceList2.vue'
import EspeceList2 from '../features/nomenclatures/EspeceList2.vue'
import ProductionList2 from '../features/nomenclatures/ProductionList2.vue'
import CategoriePensionList2 from '../features/nomenclatures/CategoriePensionList2.vue'
import CategorieAnimauxList2 from '../features/nomenclatures/CategorieAnimauxList2.vue'
import RaceList2 from '../features/nomenclatures/RaceList2.vue'
import BergerList2 from '../features/berger/BergerList2.vue'
import GardeTroupeauList2 from '../features/garde_troupeau/GardeTroupeauList2.vue'
import CommoditeList2 from '../features/commodite/CommoditeList2.vue'
import TypeDExploitantList2 from '../features/nomenclatures/TypeDExploitantList2.vue'
import TypeEquipementList2 from '../features/equipement/TypeEquipementList2.vue'
import TypeDeConventionList2 from '../features/nomenclatures/TypeDeConventionList2.vue'
import TypeCheptelList2 from '../features/nomenclatures/TypeCheptelList2.vue'
import TypeDeSuiviList2 from '../features/nomenclatures/TypeDeSuiviList2.vue'
import TypeEvenementList2 from '../features/evenement/TypeEvenementList2.vue'
import CheptelList2 from '../features/cheptel/CheptelList2.vue'
import TypeDeMesureList2 from '../features/nomenclatures/TypeDeMesureList2.vue'

import ConventionList2 from '../features/convention_exploitation/ConventionList2.vue'


import ProprietaireFoncierList2 from '../features/proprietaire/ProprietaireFoncierList2.vue'

import UPProprietaireList from '../features/proprietaire/UPProprietaireList.vue'
import UPProprietaireAdd from '../features/proprietaire/UPProprietaireAdd.vue'
import UPProprietaireEdit from '../features/proprietaire/UPProprietaireEdit.vue'

import QuartierPastoList from '../features/quartier_pasto/QuartierPastoList.vue'
import QuartierPastoAdd from '../features/quartier_pasto/QuartierPastoAdd.vue'
import QuartierPastoEdit from '../features/quartier_pasto/QuartierPastoEdit.vue'

import PlanDeSuiviList2 from '../features/plan_suivi/PlanDeSuiviList2.vue'

import SituationExploitationList2 from '../features/situation_exploitation/SituationExploitationList2.vue'

import ExploiterList from '../features/exploiter/ExploiterList.vue'
import ExploiterAdd from '../features/exploiter/ExploiterAdd.vue'
import ExploiterEdit from '../features/exploiter/ExploiterEdit.vue'

import MesureDePlanList2 from '../features/plan_suivi/MesureDePlanList2.vue'


import RucheList from '../features/ruche/RucheList.vue'
import RucheAdd from '../features/ruche/RucheAdd.vue'
import RucheEdit from '../features/ruche/RucheEdit.vue'

import EventList2 from '../features/evenement/EventList2.vue'

import LogementCommoditeList from '../features/commodite/LogementCommoditeList.vue'
import LogementCommoditeAdd from '../features/commodite/LogementCommoditeAdd.vue'
import LogementCommoditeEdit from '../features/commodite/LogementCommoditeEdit.vue'

import LogementList from '../features/logement/LogementList.vue'
import LogementEdit from '../features/logement/LogementEdit.vue'
import LogementAdd from '../features/logement/LogementAdd.vue'


import QuartieralpageView from '../features/quartier_pasto/QuartieralpageView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/unite-pastorale',
      children: [
        {
          path: '',
          name: 'unitepastorale-list',
          component: () => import('@/views/unite_pastorale/UnitePastoraleList.vue'),
        },
        {
          path: 'add',
          name: 'unitepastorale-add',
          component: () => import('@/views/unite_pastorale/UnitePastoraleForm.vue'),
        },
        {
          path: ':id',
          name: 'unitepastorale-view',
          component: () => import('@/views/unite_pastorale/UnitePastoraleForm.vue'),
        },
        {
          path: ':id/edit',
          name: 'unitepastorale-edit',
          component: () => import('@/views/unite_pastorale/UnitePastoraleForm.vue'),
        },
      ],
    },
    {
      path: '/situation-exploitation',
      children: [
        {
          path: '',
          name: 'situationdexploitation-list',
          component: () => import('@/views/situation_exploitation/SituationExploitationList.vue'),
        },
        {
          path: 'add',
          name: 'situationdexploitation-add',
          component: () => import('@/views/situation_exploitation/SituationExploitationForm.vue'),
        },
        {
          path: ':id',
          name: 'situationdexploitation-view',
          component: () => import('@/views/situation_exploitation/SituationExploitationForm.vue'),
        },
        {
          path: ':id/edit',
          name: 'situationdexploitation-edit',
          component: () => import('@/views/situation_exploitation/SituationExploitationForm.vue'),
        },
      ],
    },
    {
      path: '/equipement-alpage',
      children: [
        {
          path: '',
          name: 'equipementalpage-list',
          component: () => import('@/views/equipement_alpage/EquipementAlpageList.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'add',
          name: 'equipementalpage-add',
          component: () => import('@/views/equipement_alpage/EquipementAlpagePageForm.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: ':id',
          name: 'equipementalpage-view',
          component: () => import('@/views/equipement_alpage/EquipementAlpagePageForm.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: ':id/edit',
          name: 'equipementalpage-edit',
          component: () => import('@/views/equipement_alpage/EquipementAlpagePageForm.vue'),
          meta: { requiresAuth: true },
        },
      ],
    },
    {
      path: '/equipement-exploitant',
      children: [
        {
          path: '',
          name: 'equipementexploitant-list',
          component: () => import('@/views/equipement_exploitant/EquipementExploitantList.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'add',
          name: 'equipementexploitant-add',
          component: () => import('@/views/equipement_exploitant/EquipementExploitantPageForm.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: ':id',
          name: 'equipementexploitant-view',
          component: () => import('@/views/equipement_exploitant/EquipementExploitantPageForm.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: ':id/edit',
          name: 'equipementexploitant-edit',
          component: () => import('@/views/equipement_exploitant/EquipementExploitantPageForm.vue'),
          meta: { requiresAuth: true },
        },
      ],
    },
    {
      path: '/evenement',
      children: [
        {
          path: '',
          name: 'evenement-list',
          component: () => import('@/views/evenement/EvenementList.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'add',
          name: 'evenement-add',
          component: () => import('@/views/evenement/EvenementPageForm.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: ':id',
          name: 'evenement-view',
          component: () => import('@/views/evenement/EvenementPageForm.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: ':id/edit',
          name: 'evenement-edit',
          component: () => import('@/views/evenement/EvenementPageForm.vue'),
          meta: { requiresAuth: true },
        },
      ],
    },
    {
      path: '/exploiter',
      children: [
        {
          path: '',
          name: 'exploiter-list',
          component: () => import('@/views/exploiter/ExploiterList.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'add',
          name: 'exploiter-add',
          component: () => import('@/views/exploiter/ExploiterPageForm.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: ':id',
          name: 'exploiter-view',
          component: () => import('@/views/exploiter/ExploiterPageForm.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: ':id/edit',
          name: 'exploiter-edit',
          component: () => import('@/views/exploiter/ExploiterPageForm.vue'),
          meta: { requiresAuth: true },
        },
      ],
    },
    {
      path: '/quartier-pasto',
      children: [
        {
          path: '',
          name: 'quartierpasto-list',
          component: () => import('@/views/quartier_pasto/QuartierPastoList.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'add',
          name: 'quartierpasto-add',
          component: () => import('@/views/quartier_pasto/QuartierPastoPageForm.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: ':id',
          name: 'quartierpasto-view',
          component: () => import('@/views/quartier_pasto/QuartierPastoPageForm.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: ':id/edit',
          name: 'quartierpasto-edit',
          component: () => import('@/views/quartier_pasto/QuartierPastoPageForm.vue'),
          meta: { requiresAuth: true },
        },
      ],
    },
    {
      path: '/cheptel',
      children: [
        {
          path: '',
          name: 'cheptel-list',
          component: () => import('@/views/cheptel/CheptelList.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'add',
          name: 'cheptel-add',
          component: () => import('@/views/cheptel/CheptelForm.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: ':id',
          name: 'cheptel-view',
          component: () => import('@/views/cheptel/CheptelForm.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: ':id/edit',
          name: 'cheptel-edit',
          component: () => import('@/views/cheptel/CheptelForm.vue'),
          meta: { requiresAuth: true },
        },
      ],
    },
    {
      path: '/type-cheptel',
      children: [
        {
          path: '',
          name: 'type_cheptel-list',
          component: () => import('@/views/type_cheptel/TypeCheptelList.vue'),
        },
        {
          path: 'add',
          name: 'type_cheptel-add',
          component: () => import('@/views/type_cheptel/TypeCheptelForm.vue'),
        },
        {
          path: ':id',
          name: 'type_cheptel-view',
          component: () => import('@/views/type_cheptel/TypeCheptelForm.vue'),
        },
        {
          path: ':id/edit',
          name: 'type_cheptel-edit',
          component: () => import('@/views/type_cheptel/TypeCheptelForm.vue'),
        },
      ],
    },
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/unite_pastorale/UnitePastoraleList.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/login',
      name: 'login',
      component: Login
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
      path: '/AbriUrgences2',
      name: 'abris2',
      component: AbriDUrgenceList2,
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
      path: '/Evenements2',
      name: 'evenements2',
      component: EventList2,
      meta: { requiresAuth: true },
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
