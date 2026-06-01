from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )

from suivi_pasto.views import LogementViewset, get_choices_logement, CommoditeViewset
from suivi_pasto.views import (
    UnitePastoraleViewset,
    GeometrieUnitePastoraleViewset,
    ProprietaireFoncierViewset,
    QuartierPastoViewset,
    ProprietaireUnitePastoraleViewset,
)
from suivi_pasto.views import (
    TypeConventionViewset,
    ConventionDExploitationViewset,
    EleveurViewset,
    TypeDExploitantViewset,
    ExploitantViewset,
)
from suivi_pasto.views import SituationDExploitationViewset, ExploiterViewset
from suivi_pasto.views import (
    TypeDeSuiviViewset,
    PlanDeSuiviViewset,
    TypeDeMesureViewset,
    MesureDePlanViewset,
    RealisationMesureViewset,
    EtreComposeViewset,
    SubventionPNVViewset,
    AbriDUrgenceViewset,
    AbriDUrgenceCommoditeViewset,
    BeneficierDeViewset,
)

from suivi_pasto.views import RucheViewset, BergerViewset, GardeSituationViewset
from suivi_pasto.views import TypeEvenementViewset, EvenementViewset

from suivi_pasto.views import (
    TypeEquipementViewset,
    EquipementExploitantViewset,
    EquipementAlpageViewset,
)

##########
# dlg le 10/2/26
from suivi_pasto.views import (
    CheptelViewset,
    ProductionViewset,
    CategoriePensionViewset,
    EspeceViewset,
    RaceViewset,
    CategorieAnimauxViewset,
)

##########

from suivi_pasto.views import VisiteViewset

router = routers.SimpleRouter()


router.register("logement", LogementViewset, basename="logement")
router.register("commodite", CommoditeViewset, basename="commodite")

router.register(
    "abriDUrgenceCommodite",
    AbriDUrgenceCommoditeViewset,
    basename="abridurgencecommodite",
)

# Bloc administratif
router.register("unitePastorale", UnitePastoraleViewset, basename="unitepastorale")
router.register(
    "geometrieUP", GeometrieUnitePastoraleViewset, basename="geometrieunitepastorale"
)
router.register(
    "proprietaireFoncier", ProprietaireFoncierViewset, basename="proprietairefoncier"
)
router.register("quartierPasto", QuartierPastoViewset, basename="quartierpasto")
router.register(
    "proprietaireUP",
    ProprietaireUnitePastoraleViewset,
    basename="proprietaireunitepastorale",
)

router.register("typeConvention", TypeConventionViewset, basename="typeconvention")
router.register(
    "conventionExploitation",
    ConventionDExploitationViewset,
    basename="conventionexploitation",
)
router.register(
    "situationExploitation",
    SituationDExploitationViewset,
    basename="situationexploitation",
)
router.register("exploiter", ExploiterViewset, basename="exploiter")

router.register("eleveur", EleveurViewset, basename="eleveur")


router.register("typeExploitant", TypeDExploitantViewset, basename="typeexploitant")
router.register("exploitant", ExploitantViewset, basename="exploitant")
router.register("etreCompose", EtreComposeViewset, basename="etrecompose")
router.register("subventionPNV", SubventionPNVViewset, basename="subventionpnv")
router.register("abriDUrgence", AbriDUrgenceViewset, basename="abridurgence")
router.register("beneficierDe", BeneficierDeViewset, basename="beneficierde")

# Ruche / Berger
router.register("ruche", RucheViewset, basename="ruche")
router.register("berger", BergerViewset, basename="berger")
router.register("gardeSituation", GardeSituationViewset, basename="gardesituation")

# Evenements
router.register("typeEvenement", TypeEvenementViewset, basename="typeevenement")
router.register("evenement", EvenementViewset, basename="evenement")

# BLoc bleu
router.register("typeSuivi", TypeDeSuiviViewset, basename="typesuivi")
router.register("planSuivi", PlanDeSuiviViewset, basename="plansuivi")
router.register("typeMesure", TypeDeMesureViewset, basename="typemesure")
router.register("mesurePlan", MesureDePlanViewset, basename="mesureplan")
router.register(
    "realisationMesure", RealisationMesureViewset, basename="realisationmesure"
)

router.register("typeEquipement", TypeEquipementViewset, basename="typeequipement")
router.register(
    "equipementAlpage", EquipementAlpageViewset, basename="equipementalpage"
)
router.register(
    "equipementExploitant", EquipementExploitantViewset, basename="equipementexploitant"
)

###########
# dlg le 10/2/26
router.register("cheptel", CheptelViewset, basename="cheptel")
router.register("production", ProductionViewset, basename="production")
router.register(
    "categorie_pension", CategoriePensionViewset, basename="categorie_pension"
)
router.register("espece", EspeceViewset, basename="espece")
router.register("race", RaceViewset, basename="race")
router.register(
    "categorie_animaux", CategorieAnimauxViewset, basename="categorie_animaux"
)
###########

router.register("visite", VisiteViewset, basename="visite")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/choices_logement/", get_choices_logement, name="get_choices_logement"),
    path("", include("accounts.urls")),
]
