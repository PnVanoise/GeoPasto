import { createRouter, createWebHistory } from 'vue-router'
import { useMainStore } from '../store'

import Login from '../components/auth/Login.vue'














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
          name: 'typecheptel-list',
          component: () => import('@/views/type_cheptel/TypeCheptelList.vue'),
        },
        {
          path: 'add',
          name: 'typecheptel-add',
          component: () => import('@/views/type_cheptel/TypeCheptelForm.vue'),
        },
        {
          path: ':id',
          name: 'typecheptel-view',
          component: () => import('@/views/type_cheptel/TypeCheptelForm.vue'),
        },
        {
          path: ':id/edit',
          name: 'typecheptel-edit',
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
      component: () => import('@/features/proprietaire/ProprietaireFoncierList2.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/UPProprietaires',
      name: 'upproprietaires',
      component: () => import('@/features/proprietaire/UPProprietaireList2.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/TypeSuivis2',
      name: 'typesuivis2',
      component: () => import('@/features/nomenclatures/TypeDeSuiviList2.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/PlanSuivis2',
      name: 'plansuivis2',
      component: () => import('@/features/plan_suivi/PlanDeSuiviList2.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/TypeMesures2',
      name: 'typeMesures2',
      component: () => import('@/features/nomenclatures/TypeDeMesureList2.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/MesurePlans2',
      name: 'mesurePlans2',
      component: () => import('@/features/plan_suivi/MesureDePlanList2.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/TypeConventions2',
      name: 'typeconventions2',
      component: () => import('@/features/nomenclatures/TypeDeConventionList2.vue'),
    },
    {
      path: '/Conventions2',
      name: 'conventions2',
      component: () => import('@/features/convention_exploitation/ConventionList2.vue'),
    },
    {
      path: '/SituationExploitations2',
      name: 'situations2',
      component: () => import('@/features/situation_exploitation/SituationExploitationList2.vue'),
    },
    {
      path: '/Eleveurs2',
      name: 'eleveurs2',
      component: () => import('@/features/eleveur/EleveurList2.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },

    {
      path: '/TypeExploitants2',
      name: 'typeExploitants2',
      component: () => import('@/features/nomenclatures/TypeDExploitantList2.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Exploitants2',
      name: 'exploitants2',
      component: () => import('@/features/exploitant/ExploitantList2.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Subventions2',
      name: 'subventions2',
      component: () => import('@/features/subvention/SubventionList2.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/AbriUrgences2',
      name: 'abris2',
      component: () => import('@/features/abri_urgence/AbriDUrgenceList2.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Especes2',
      name: 'especes2',
      component: () => import('@/features/nomenclatures/EspeceList2.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path : "/Productions2",
      name : "productions2",
      component: () => import('@/features/nomenclatures/ProductionList2.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/CategoriesPension2',
      name: 'categories_pension2',
      component: () => import('@/features/nomenclatures/CategoriePensionList2.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/CategoriesAnimaux2',
      name: 'categories_animaux2',
      component: () => import('@/features/nomenclatures/CategorieAnimauxList2.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Races2',
      name: 'races2',
      component: () => import('@/features/nomenclatures/RaceList2.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Bergers2',
      name: 'bergers2',
      component: () => import('@/features/berger/BergerList2.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/TypeCheptels2',
      name: 'typecheptels2',
      component: () => import('@/features/nomenclatures/TypeCheptelList2.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/GardeTroupeaux2',
      name: 'gardetroupeaux2',
      component: () => import('@/features/garde_troupeau/GardeTroupeauList2.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/Cheptels2',
      name: 'cheptels2',
      component: () => import('@/features/cheptel/CheptelList2.vue'),
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
      component: () => import('@/features/ruche/RucheList2.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/Evenements2',
      name: 'evenements2',
      component: () => import('@/features/evenement/EventList2.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/TypeEvenements2',
      name: 'typeevenements2',
      component: () => import('@/features/evenement/TypeEvenementList2.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/TypeEquipements2',
      name: 'typeequipements2',
      component: () => import('@/features/equipement/TypeEquipementList2.vue'),
      meta: {
        modelName: 'typeequipement',
        requiredPermission: 'view_typeequipement',
        requiresAuth: true
      },  // Route protégée
    },
    {
      path: '/Logements',
      name: 'logements',
      component: () => import('@/features/logement/LogementList2.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/Commodites2',
      name: 'commodites2',
      component: () => import('@/features/commodite/CommoditeList2.vue'),
      meta: { requiresAuth: true },  // Route protégée
    },
    {
      path: '/LogementCommodites',
      name: 'logementCommodites',
      component: () => import('@/features/commodite/LogementCommoditeList2.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/QuartieralpageView/:id',
      name: 'quartieralpageview',
      component: QuartieralpageView
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
