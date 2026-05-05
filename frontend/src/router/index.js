import { createRouter, createWebHistory } from 'vue-router'
import { useMainStore } from '../store'

import Login from '../components/auth/Login.vue'

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
      path: '/proprietaire-foncier',
      children: [
        { path: '',         name: 'proprietairefoncier-list', component: () => import('@/views/proprietaire/ProprietaireFoncierList.vue') },
        { path: 'add',      name: 'proprietairefoncier-add',  component: () => import('@/views/proprietaire/ProprietaireFoncierPageForm.vue') },
        { path: ':id',      name: 'proprietairefoncier-view', component: () => import('@/views/proprietaire/ProprietaireFoncierPageForm.vue') },
        { path: ':id/edit', name: 'proprietairefoncier-edit', component: () => import('@/views/proprietaire/ProprietaireFoncierPageForm.vue') },
      ],
    },
    {
      path: '/up-proprietaire',
      children: [
        { path: '',         name: 'upproprietaire-list', component: () => import('@/views/proprietaire/UPProprietaireList.vue') },
        { path: 'add',      name: 'upproprietaire-add',  component: () => import('@/views/proprietaire/UPProprietairePageForm.vue') },
        { path: ':id',      name: 'upproprietaire-view', component: () => import('@/views/proprietaire/UPProprietairePageForm.vue') },
        { path: ':id/edit', name: 'upproprietaire-edit', component: () => import('@/views/proprietaire/UPProprietairePageForm.vue') },
      ],
    },
    {
      path: '/type-suivi',
      children: [
        { path: '',         name: 'typedesuivi-list', component: () => import('@/views/nomenclatures/TypeDeSuiviList.vue') },
        { path: 'add',      name: 'typedesuivi-add',  component: () => import('@/views/nomenclatures/TypeDeSuiviPageForm.vue') },
        { path: ':id',      name: 'typedesuivi-view', component: () => import('@/views/nomenclatures/TypeDeSuiviPageForm.vue') },
        { path: ':id/edit', name: 'typedesuivi-edit', component: () => import('@/views/nomenclatures/TypeDeSuiviPageForm.vue') },
      ],
    },
    {
      path: '/plan-suivi',
      children: [
        { path: '',         name: 'plandesuivi-list', component: () => import('@/views/plan_suivi/PlanDeSuiviList.vue') },
        { path: 'add',      name: 'plandesuivi-add',  component: () => import('@/views/plan_suivi/PlanDeSuiviPageForm.vue') },
        { path: ':id',      name: 'plandesuivi-view', component: () => import('@/views/plan_suivi/PlanDeSuiviPageForm.vue') },
        { path: ':id/edit', name: 'plandesuivi-edit', component: () => import('@/views/plan_suivi/PlanDeSuiviPageForm.vue') },
      ],
    },
    {
      path: '/type-mesure',
      children: [
        { path: '',         name: 'typedemesure-list', component: () => import('@/views/nomenclatures/TypeDeMesureList.vue') },
        { path: 'add',      name: 'typedemesure-add',  component: () => import('@/views/nomenclatures/TypeDeMesurePageForm.vue') },
        { path: ':id',      name: 'typedemesure-view', component: () => import('@/views/nomenclatures/TypeDeMesurePageForm.vue') },
        { path: ':id/edit', name: 'typedemesure-edit', component: () => import('@/views/nomenclatures/TypeDeMesurePageForm.vue') },
      ],
    },
    {
      path: '/mesure-plan',
      children: [
        { path: '',         name: 'mesuredeplan-list', component: () => import('@/views/plan_suivi/MesureDePlanList.vue') },
        { path: 'add',      name: 'mesuredeplan-add',  component: () => import('@/views/plan_suivi/MesureDePlanPageForm.vue') },
        { path: ':id',      name: 'mesuredeplan-view', component: () => import('@/views/plan_suivi/MesureDePlanPageForm.vue') },
        { path: ':id/edit', name: 'mesuredeplan-edit', component: () => import('@/views/plan_suivi/MesureDePlanPageForm.vue') },
      ],
    },
    {
      path: '/type-convention',
      children: [
        { path: '',         name: 'typeconvention-list', component: () => import('@/views/nomenclatures/TypeConventionList.vue') },
        { path: 'add',      name: 'typeconvention-add',  component: () => import('@/views/nomenclatures/TypeConventionPageForm.vue') },
        { path: ':id',      name: 'typeconvention-view', component: () => import('@/views/nomenclatures/TypeConventionPageForm.vue') },
        { path: ':id/edit', name: 'typeconvention-edit', component: () => import('@/views/nomenclatures/TypeConventionPageForm.vue') },
      ],
    },
    {
      path: '/convention-exploitation',
      children: [
        { path: '',         name: 'conventiondexploitation-list', component: () => import('@/views/convention_exploitation/ConventionList.vue') },
        { path: 'add',      name: 'conventiondexploitation-add',  component: () => import('@/views/convention_exploitation/ConventionPageForm.vue') },
        { path: ':id',      name: 'conventiondexploitation-view', component: () => import('@/views/convention_exploitation/ConventionPageForm.vue') },
        { path: ':id/edit', name: 'conventiondexploitation-edit', component: () => import('@/views/convention_exploitation/ConventionPageForm.vue') },
      ],
    },
    {
      path: '/eleveur',
      children: [
        { path: '',         name: 'eleveur-list', component: () => import('@/views/eleveur/EleveurList.vue') },
        { path: 'add',      name: 'eleveur-add',  component: () => import('@/views/eleveur/EleveurPageForm.vue') },
        { path: ':id',      name: 'eleveur-view', component: () => import('@/views/eleveur/EleveurPageForm.vue') },
        { path: ':id/edit', name: 'eleveur-edit', component: () => import('@/views/eleveur/EleveurPageForm.vue') },
      ],
    },

    {
      path: '/type-exploitant',
      children: [
        { path: '',         name: 'typedexploitant-list', component: () => import('@/views/nomenclatures/TypeDExploitantList.vue') },
        { path: 'add',      name: 'typedexploitant-add',  component: () => import('@/views/nomenclatures/TypeDExploitantPageForm.vue') },
        { path: ':id',      name: 'typedexploitant-view', component: () => import('@/views/nomenclatures/TypeDExploitantPageForm.vue') },
        { path: ':id/edit', name: 'typedexploitant-edit', component: () => import('@/views/nomenclatures/TypeDExploitantPageForm.vue') },
      ],
    },
    {
      path: '/exploitant',
      children: [
        { path: '',         name: 'exploitant-list', component: () => import('@/views/exploitant/ExploitantList.vue') },
        { path: 'add',      name: 'exploitant-add',  component: () => import('@/views/exploitant/ExploitantPageForm.vue') },
        { path: ':id',      name: 'exploitant-view', component: () => import('@/views/exploitant/ExploitantPageForm.vue') },
        { path: ':id/edit', name: 'exploitant-edit', component: () => import('@/views/exploitant/ExploitantPageForm.vue') },
      ],
    },
    {
      path: '/subvention',
      children: [
        { path: '',         name: 'subventionpnv-list', component: () => import('@/views/subvention/SubventionList.vue') },
        { path: 'add',      name: 'subventionpnv-add',  component: () => import('@/views/subvention/SubventionPageForm.vue') },
        { path: ':id',      name: 'subventionpnv-view', component: () => import('@/views/subvention/SubventionPageForm.vue') },
        { path: ':id/edit', name: 'subventionpnv-edit', component: () => import('@/views/subvention/SubventionPageForm.vue') },
      ],
    },
    {
      path: '/abri-urgence',
      children: [
        { path: '',         name: 'abriurgence-list', component: () => import('@/views/abri_urgence/AbriDUrgenceList.vue') },
        { path: 'add',      name: 'abriurgence-add',  component: () => import('@/views/abri_urgence/AbriDUrgencePageForm.vue') },
        { path: ':id',      name: 'abriurgence-view', component: () => import('@/views/abri_urgence/AbriDUrgencePageForm.vue') },
        { path: ':id/edit', name: 'abriurgence-edit', component: () => import('@/views/abri_urgence/AbriDUrgencePageForm.vue') },
      ],
    },
    {
      path: '/espece',
      children: [
        { path: '',         name: 'espece-list', component: () => import('@/views/nomenclatures/EspeceList.vue') },
        { path: 'add',      name: 'espece-add',  component: () => import('@/views/nomenclatures/EspecePageForm.vue') },
        { path: ':id',      name: 'espece-view', component: () => import('@/views/nomenclatures/EspecePageForm.vue') },
        { path: ':id/edit', name: 'espece-edit', component: () => import('@/views/nomenclatures/EspecePageForm.vue') },
      ],
    },
    {
      path: '/production',
      children: [
        { path: '',         name: 'production-list', component: () => import('@/views/nomenclatures/ProductionList.vue') },
        { path: 'add',      name: 'production-add',  component: () => import('@/views/nomenclatures/ProductionPageForm.vue') },
        { path: ':id',      name: 'production-view', component: () => import('@/views/nomenclatures/ProductionPageForm.vue') },
        { path: ':id/edit', name: 'production-edit', component: () => import('@/views/nomenclatures/ProductionPageForm.vue') },
      ],
    },
    {
      path: '/categorie-pension',
      children: [
        { path: '',         name: 'categoriepension-list', component: () => import('@/views/nomenclatures/CategoriePensionList.vue') },
        { path: 'add',      name: 'categoriepension-add',  component: () => import('@/views/nomenclatures/CategoriePensionPageForm.vue') },
        { path: ':id',      name: 'categoriepension-view', component: () => import('@/views/nomenclatures/CategoriePensionPageForm.vue') },
        { path: ':id/edit', name: 'categoriepension-edit', component: () => import('@/views/nomenclatures/CategoriePensionPageForm.vue') },
      ],
    },
    {
      path: '/categorie-animaux',
      children: [
        { path: '',         name: 'categorieanimaux-list', component: () => import('@/views/nomenclatures/CategorieAnimauxList.vue') },
        { path: 'add',      name: 'categorieanimaux-add',  component: () => import('@/views/nomenclatures/CategorieAnimauxPageForm.vue') },
        { path: ':id',      name: 'categorieanimaux-view', component: () => import('@/views/nomenclatures/CategorieAnimauxPageForm.vue') },
        { path: ':id/edit', name: 'categorieanimaux-edit', component: () => import('@/views/nomenclatures/CategorieAnimauxPageForm.vue') },
      ],
    },
    {
      path: '/race',
      children: [
        { path: '',         name: 'race-list', component: () => import('@/views/nomenclatures/RaceList.vue') },
        { path: 'add',      name: 'race-add',  component: () => import('@/views/nomenclatures/RacePageForm.vue') },
        { path: ':id',      name: 'race-view', component: () => import('@/views/nomenclatures/RacePageForm.vue') },
        { path: ':id/edit', name: 'race-edit', component: () => import('@/views/nomenclatures/RacePageForm.vue') },
      ],
    },
    {
      path: '/berger',
      children: [
        { path: '',        name: 'berger-list', component: () => import('@/views/berger/BergerList.vue') },
        { path: 'add',     name: 'berger-add',  component: () => import('@/views/berger/BergerPageForm.vue') },
        { path: ':id',     name: 'berger-view', component: () => import('@/views/berger/BergerPageForm.vue') },
        { path: ':id/edit',name: 'berger-edit', component: () => import('@/views/berger/BergerPageForm.vue') },
      ],
    },
    {
      path: '/garde-situation',
      children: [
        { path: '',         name: 'gardesituation-list', component: () => import('@/views/garde_troupeau/GardeTroupeauList.vue') },
        { path: 'add',      name: 'gardesituation-add',  component: () => import('@/views/garde_troupeau/GardeTroupeauPageForm.vue') },
        { path: ':id',      name: 'gardesituation-view', component: () => import('@/views/garde_troupeau/GardeTroupeauPageForm.vue') },
        { path: ':id/edit', name: 'gardesituation-edit', component: () => import('@/views/garde_troupeau/GardeTroupeauPageForm.vue') },
      ],
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
      path: '/ruche',
      children: [
        { path: '',         name: 'ruche-list', component: () => import('@/views/ruche/RucheList.vue') },
        { path: 'add',      name: 'ruche-add',  component: () => import('@/views/ruche/RuchePageForm.vue') },
        { path: ':id',      name: 'ruche-view', component: () => import('@/views/ruche/RuchePageForm.vue') },
        { path: ':id/edit', name: 'ruche-edit', component: () => import('@/views/ruche/RuchePageForm.vue') },
      ],
    },
    {
      path: '/type-evenement',
      children: [
        { path: '',         name: 'typeevenement-list', component: () => import('@/views/nomenclatures/TypeEvenementList.vue') },
        { path: 'add',      name: 'typeevenement-add',  component: () => import('@/views/nomenclatures/TypeEvenementPageForm.vue') },
        { path: ':id',      name: 'typeevenement-view', component: () => import('@/views/nomenclatures/TypeEvenementPageForm.vue') },
        { path: ':id/edit', name: 'typeevenement-edit', component: () => import('@/views/nomenclatures/TypeEvenementPageForm.vue') },
      ],
    },
    {
      path: '/type-equipement',
      children: [
        { path: '',         name: 'typeequipement-list', component: () => import('@/views/nomenclatures/TypeEquipementList.vue') },
        { path: 'add',      name: 'typeequipement-add',  component: () => import('@/views/nomenclatures/TypeEquipementPageForm.vue') },
        { path: ':id',      name: 'typeequipement-view', component: () => import('@/views/nomenclatures/TypeEquipementPageForm.vue') },
        { path: ':id/edit', name: 'typeequipement-edit', component: () => import('@/views/nomenclatures/TypeEquipementPageForm.vue') },
      ],
    },
    {
      path: '/logement',
      children: [
        { path: '',         name: 'logement-list', component: () => import('@/views/logement/LogementList.vue') },
        { path: 'add',      name: 'logement-add',  component: () => import('@/views/logement/LogementPageForm.vue') },
        { path: ':id',      name: 'logement-view', component: () => import('@/views/logement/LogementPageForm.vue') },
        { path: ':id/edit', name: 'logement-edit', component: () => import('@/views/logement/LogementPageForm.vue') },
      ],
    },
    {
      path: '/commodite',
      children: [
        { path: '',         name: 'commodite-list', component: () => import('@/views/commodite/CommoditeList.vue') },
        { path: 'add',      name: 'commodite-add',  component: () => import('@/views/commodite/CommoditePageForm.vue') },
        { path: ':id',      name: 'commodite-view', component: () => import('@/views/commodite/CommoditePageForm.vue') },
        { path: ':id/edit', name: 'commodite-edit', component: () => import('@/views/commodite/CommoditePageForm.vue') },
      ],
    },
    {
      path: '/logement-commodite',
      children: [
        { path: '',         name: 'logementcommodite-list', component: () => import('@/views/logement_commodite/LogementCommoditeList.vue') },
        { path: 'add',      name: 'logementcommodite-add',  component: () => import('@/views/logement_commodite/LogementCommoditePageForm.vue') },
        { path: ':id',      name: 'logementcommodite-view', component: () => import('@/views/logement_commodite/LogementCommoditePageForm.vue') },
        { path: ':id/edit', name: 'logementcommodite-edit', component: () => import('@/views/logement_commodite/LogementCommoditePageForm.vue') },
      ],
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
