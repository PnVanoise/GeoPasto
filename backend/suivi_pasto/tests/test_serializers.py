"""
Comprehensive serializer tests for the alpages app.

Existing smoke tests (SerializersSmokeTest) are preserved unchanged.
All new tests use IDs >= 100 to avoid conflicts with the smoke-test IDs (20, 21).

GeoFeature serializers (QuartierPasto, BeneficierDe) expose non-geometry fields
under data['properties'] and the geometry under data['geometry'].
"""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase

from suivi_pasto.models import (
    UnitePastorale,
    GeometrieUnitePastorale,
    ProprietaireFoncier,
    ProprietaireUnitePastorale,
    QuartierPasto,
    TypeDeSuivi,
    PlanDeSuivi,
    TypeDeMesure,
    MesureDePlan,
    Enjeu,
    RealisationMesure,
    TypeConvention,
    ConventionDExploitation,
    SituationDExploitation,
    Exploiter,
    Eleveur,
    Exploitant,
    EtreCompose,
    SubventionPNV,
    Commodite,
    AbriDUrgence,
    AbriDUrgenceCommodite,
    BeneficierDe,
    Berger,
    GardeSituation,
    Production,
    CategoriePension,
    Espece,
    Race,
    CategorieAnimaux,
    Cheptel,
    TypeEvenement,
    TypeEquipement,
    Visite,
)
from suivi_pasto.serializers import (
    EleveurSerializer,
    GeometrieUnitePastoraleSerializer,
    UnitePastoraleSerializer,
    ProprietaireUnitePastoraleSerializer,
    SituationDExploitationSerializer,
    ConventionDExploitationSerializer,
    ExploiterSerializer,
    QuartierPastoSerializer,
    GardeSituationSerializer,
    ExploitantSerializer,
    BeneficierDeSerializer,
    PlanDeSuiviSerializer,
    MesureDePlanSerializer,
    RealisationMesureSerializer,
    SubventionPNVSerializer,
    TypeConventionSerializer,
    TypeDeSuiviSerializer,
    TypeDeMesureSerializer,
    BergerSerializer,
    ProductionSerializer,
    CategoriePensionSerializer,
    EspeceSerializer,
    RaceSerializer,
    CategorieAnimauxSerializer,
    CheptelSerializer,
    TypeEvenementSerializer,
    TypeEquipementSerializer,
    AbriDUrgenceSerializer,
    CommoditeSerializer,
    AbriDUrgenceCommoditeSerializer,
    VisiteSerializer,
)

# ---------------------------------------------------------------------------
# Geometry helpers (SRID 2154 - RGF93 / Lambert-93).
# Each call returns a brand-new GEOSGeometry instance so that the in place
# transform() calls made by GeoFeature serializers do not affect other tests.
# ---------------------------------------------------------------------------


def _up_geom():
    return GEOSGeometry("SRID=2154;MULTIPOLYGON(((0 0,0 1,1 1,1 0,0 0)))")


def _qp_geom():
    return GEOSGeometry("SRID=2154;MULTIPOLYGON(((0 0,0 1,1 1,1 0,0 0)))")


def _pt_geom():
    return GEOSGeometry("SRID=2154;POINT(0 0)")


# ============================================================================
# Original smoke tests (MUST NOT be changed)
# ============================================================================


class SerializersSmokeTest(TestCase):

    def test_situation_serializer_fields(self):
        s = SituationDExploitation.objects.create(
            id_situation=20,
            nom_situation="S20",
            date_debut=date(2020, 1, 1),
        )
        ser = SituationDExploitationSerializer(s)
        data = ser.data
        self.assertIn("id_situation", data)
        self.assertIn("nom_situation", data)

    def test_commodite_serializer(self):
        c = Commodite.objects.create(id_commodite=20, description="C20")
        ser = CommoditeSerializer(c)
        self.assertEqual(ser.data["description"], "C20")

    def test_abri_commodite_serializer(self):
        a = AbriDUrgence.objects.create(
            id_abri_urgence=20, description="A20", etat="OK"
        )
        c = Commodite.objects.create(id_commodite=21, description="C21")
        ac = AbriDUrgenceCommodite.objects.create(
            id_abri_urgence_commodite=20, abri_urgence=a, commodite=c, etat="OK"
        )
        ser = AbriDUrgenceCommoditeSerializer(ac)
        self.assertIn("abri_urgence_description", ser.data)
        self.assertIn("commodite_desc", ser.data)


# ============================================================================
# EleveurSerializer
# ============================================================================


class EleveurSerializerTest(TestCase):
    """Tests for EleveurSerializer, focusing on the nom_complet computed field."""

    def test_nom_complet_with_nom_and_prenom(self):
        """nom='dupont', prenom='jean' → 'DUPONT jean'."""
        e = Eleveur.objects.create(
            id_eleveur=100, nom_eleveur="dupont", prenom_eleveur="jean"
        )
        data = EleveurSerializer(e).data
        self.assertEqual(data["nom_complet"], "DUPONT jean")

    def test_nom_complet_with_nom_only_prenom_none(self):
        """nom='martin', prenom=None → 'MARTIN' (trailing space stripped)."""
        e = Eleveur.objects.create(
            id_eleveur=101, nom_eleveur="martin", prenom_eleveur=None
        )
        data = EleveurSerializer(e).data
        self.assertEqual(data["nom_complet"], "MARTIN")

    def test_nom_complet_with_empty_string_prenom(self):
        """nom='martin', prenom='' → 'MARTIN' (same as None case)."""
        e = Eleveur.objects.create(
            id_eleveur=102, nom_eleveur="martin", prenom_eleveur=""
        )
        data = EleveurSerializer(e).data
        self.assertEqual(data["nom_complet"], "MARTIN")

    def test_basic_field_presence(self):
        """All expected fields must be present in the serialized output."""
        e = Eleveur.objects.create(id_eleveur=103, nom_eleveur="Test")
        data = EleveurSerializer(e).data
        for field in (
            "id_eleveur",
            "nom_eleveur",
            "prenom_eleveur",
            "nom_complet",
            "adresse_eleveur",
            "tel_eleveur",
            "mail_eleveur",
            "commentaire",
        ):
            self.assertIn(field, data, msg=f"Missing field: {field}")


# ============================================================================
# SituationDExploitationSerializer – extended
# ============================================================================


class SituationDExploitationExtendedTest(TestCase):
    """Additional tests for the exploitant_nom computed field."""

    def test_exploitant_nom_when_exploitant_is_set(self):
        exploitant = Exploitant.objects.create(
            id_exploitant=100, nom_exploitant="Ferme100"
        )
        sit = SituationDExploitation.objects.create(
            id_situation=100,
            nom_situation="S100",
            exploitant=exploitant,
        )
        data = SituationDExploitationSerializer(sit).data
        self.assertEqual(data["exploitant_nom"], "Ferme100")

    def test_exploitant_nom_is_none_when_no_exploitant(self):
        sit = SituationDExploitation.objects.create(
            id_situation=101,
            nom_situation="S101",
        )
        data = SituationDExploitationSerializer(sit).data
        self.assertIsNone(data["exploitant_nom"])


# ============================================================================
# ExploiterSerializer
# ============================================================================


class ExploiterSerializerTest(TestCase):
    """Tests for the situation_nom and quartier_nom source-based fields."""

    def test_quartier_nom_populated_when_fk_set(self):
        sit = SituationDExploitation.objects.create(
            id_situation=102,
            nom_situation="Sit102",
        )
        qp = QuartierPasto.objects.create(
            id_quartier=100,
            nom_quartier="Quartier100",
            geometry=_qp_geom(),
            situation_exploitation=sit,
        )
        exp = Exploiter.objects.create(
            id_exploiter=100,
            quartier=qp,
            date_debut=date(2024, 6, 1),
            date_fin=date(2024, 9, 30),
        )
        data = ExploiterSerializer(exp).data
        self.assertEqual(data["quartier_nom"], "Quartier100")


class ExploiterNombreAnimauxValidationTest(TestCase):
    def setUp(self):
        self.up = UnitePastorale.objects.create(
            id_unite_pastorale=150,
            code_up="UP150",
            nom_up="UP 150",
            geom_active=_up_geom(),
        )
        self.situation = SituationDExploitation.objects.create(
            id_situation=150,
            nom_situation="Sit150",
            unite_pastorale=self.up,
        )
        self.quartier = QuartierPasto.objects.create(
            id_quartier=150,
            nom_quartier="Quartier150",
            geometry=_qp_geom(),
            situation_exploitation=self.situation,
        )

        self.cheptel_1 = Cheptel.objects.create(
            id_cheptel=150,
            description="Troupeau150",
            situation_exploitation=self.situation,
            nombre_animaux=40,
        )
        self.cheptel_2 = Cheptel.objects.create(
            id_cheptel=151,
            description="Troupeau151",
            situation_exploitation=self.situation,
            nombre_animaux=60,
        )

    def test_accepts_value_within_specific_herd_limit(self):
        serializer = ExploiterSerializer(
            data={
                "id_exploiter": 150,
                "quartier": self.quartier.id_quartier,
                "cheptel": self.cheptel_1.id_cheptel,
                "date_debut": "2024-06-01",
                "date_fin": "2024-06-10",
                "nombre_animaux": 35,
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rejects_value_above_specific_herd_limit(self):
        serializer = ExploiterSerializer(
            data={
                "id_exploiter": 151,
                "quartier": self.quartier.id_quartier,
                "cheptel": self.cheptel_1.id_cheptel,
                "date_debut": "2024-06-01",
                "date_fin": "2024-06-10",
                "nombre_animaux": 41,
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("nombre_animaux", serializer.errors)

    def test_rejects_value_above_all_herds_sum_when_cheptel_null(self):
        serializer = ExploiterSerializer(
            data={
                "id_exploiter": 152,
                "quartier": self.quartier.id_quartier,
                "cheptel": None,
                "date_debut": "2024-06-01",
                "date_fin": "2024-06-10",
                "nombre_animaux": 101,
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("nombre_animaux", serializer.errors)

    def test_accepts_value_within_all_herds_sum_when_cheptel_null(self):
        serializer = ExploiterSerializer(
            data={
                "id_exploiter": 153,
                "quartier": self.quartier.id_quartier,
                "cheptel": None,
                "date_debut": "2024-06-01",
                "date_fin": "2024-06-10",
                "nombre_animaux": 100,
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)


# ============================================================================
# QuartierPastoSerializer  (GeoFeature – properties under data['properties'])
# ============================================================================


class QuartierPastoSerializerTest(TestCase):
    """
    QuartierPastoSerializer is a GeoFeatureModelSerializer.
    Non-geometry fields are nested under data['properties'].
    """

    def test_fields_in_properties(self):
        sit = SituationDExploitation.objects.create(
            id_situation=100,
            nom_situation="Sit QP",
        )
        qp = QuartierPasto.objects.create(
            id_quartier=101,
            nom_quartier="QP101",
            geometry=_qp_geom(),
            situation_exploitation=sit,
        )
        data = QuartierPastoSerializer(qp).data
        self.assertEqual(data["type"], "Feature")
        self.assertEqual(data["properties"]["nom_quartier"], "QP101")
        self.assertEqual(data["properties"]["situation_exploitation"], sit.id_situation)

    def test_no_situation_exploitation(self):
        qp = QuartierPasto.objects.create(
            id_quartier=102,
            nom_quartier="QP102",
            geometry=_qp_geom(),
            situation_exploitation=None,
        )
        data = QuartierPastoSerializer(qp).data
        self.assertIsNone(data["properties"]["situation_exploitation"])

    def test_geometry_none_returns_empty_polygon_fallback(self):
        """When geometry is None the serializer substitutes an empty Polygon."""
        qp = QuartierPasto.objects.create(
            id_quartier=103,
            nom_quartier="QP103",
            geometry=None,
        )
        data = QuartierPastoSerializer(qp).data
        self.assertEqual(data["geometry"], {"type": "MultiPolygon", "coordinates": []})

    def test_geometry_set_returns_geojson_feature(self):
        """A QuartierPasto with a real geometry must be serialized as a GeoJSON Feature."""
        qp = QuartierPasto.objects.create(
            id_quartier=104,
            nom_quartier="QP104",
            geometry=_qp_geom(),
        )
        data = QuartierPastoSerializer(qp).data
        self.assertEqual(data["type"], "Feature")


# ============================================================================
# GardeSituationSerializer
# ============================================================================


class GardeSituationSerializerTest(TestCase):
    """Tests for the berger_nom, berger_prenom, and situation_nom fields."""

    def test_berger_nom_prenom_and_situation_nom_populated(self):
        berger = Berger.objects.create(
            id_berger=100,
            nom_berger="Mouton",
            prenom_berger="Pierre",
        )
        sit = SituationDExploitation.objects.create(
            id_situation=103,
            nom_situation="Sit103",
        )
        gs = GardeSituation.objects.create(
            id_garde_situation=100,
            date_debut=date(2023, 1, 1),
            berger=berger,
            situation_exploitation=sit,
        )
        data = GardeSituationSerializer(gs).data
        self.assertEqual(data["berger_nom"], "Mouton")
        self.assertEqual(data["berger_prenom"], "Pierre")
        self.assertEqual(data["situation_nom"], "Sit103")


# ============================================================================
# ExploitantSerializer
# ============================================================================


class ExploitantSerializerTest(TestCase):
    """Tests for ExploitantSerializer: membres_ids, create, and update logic."""

    def _make_eleveur(self, pk, nom):
        return Eleveur.objects.create(id_eleveur=pk, nom_eleveur=nom)

    def test_membres_ids_returns_list_of_eleveur_ids(self):
        exp = Exploitant.objects.create(
            id_exploitant=100, nom_exploitant="Groupement100"
        )
        e1 = self._make_eleveur(105, "E1")
        e2 = self._make_eleveur(106, "E2")
        EtreCompose.objects.create(exploitant=exp, eleveur=e1)
        EtreCompose.objects.create(exploitant=exp, eleveur=e2)
        data = ExploitantSerializer(exp).data
        self.assertCountEqual(data["membres_ids"], [105, 106])

    def test_create_with_membres_creates_etre_compose_records(self):
        e = self._make_eleveur(107, "EleveurCreate")
        ser = ExploitantSerializer(
            data={
                "id_exploitant": 101,
                "nom_exploitant": "GroupCreate",
                "membres": [107],
                "president": None,
                "type_exploitant": None,
            }
        )
        self.assertTrue(ser.is_valid(), ser.errors)
        instance = ser.save()
        self.assertTrue(
            EtreCompose.objects.filter(exploitant=instance, eleveur=e).exists(),
            "EtreCompose should be created for the provided member.",
        )

    def test_update_adds_new_and_removes_old_membres(self):
        exp = Exploitant.objects.create(id_exploitant=102, nom_exploitant="GroupUpdate")
        old_e = self._make_eleveur(108, "OldMember")
        new_e = self._make_eleveur(109, "NewMember")
        EtreCompose.objects.create(exploitant=exp, eleveur=old_e)

        ser = ExploitantSerializer(
            exp,
            data={
                "id_exploitant": 102,
                "nom_exploitant": "GroupUpdate",
                "membres": [109],
                "president": None,
                "type_exploitant": None,
            },
        )
        self.assertTrue(ser.is_valid(), ser.errors)
        ser.save()

        self.assertFalse(
            EtreCompose.objects.filter(exploitant=exp, eleveur=old_e).exists(),
            "Old member should have been removed.",
        )
        self.assertTrue(
            EtreCompose.objects.filter(exploitant=exp, eleveur=new_e).exists(),
            "New member should have been added.",
        )


# ============================================================================
# BeneficierDeSerializer  (GeoFeature – properties under data['properties'])
# ============================================================================


class BeneficierDeSerializerTest(TestCase):
    """
    BeneficierDeSerializer is a GeoFeatureModelSerializer.
    Computed fields exploitant_nom and abri_description live under data['properties'].
    """

    def test_exploitant_nom_and_abri_description_populated(self):
        exp = Exploitant.objects.create(
            id_exploitant=103, nom_exploitant="ExploitantBen"
        )
        abri = AbriDUrgence.objects.create(
            id_abri_urgence=100,
            description="Abri100",
            etat="Bon",
        )
        bd = BeneficierDe.objects.create(
            id_beneficier_de=100,
            exploitant=exp,
            abri_urgence=abri,
            date_debut=date(2024, 1, 1),
            geometry=_pt_geom(),
        )
        data = BeneficierDeSerializer(bd).data
        self.assertEqual(data["properties"]["exploitant_nom"], "ExploitantBen")
        self.assertEqual(data["properties"]["abri_description"], "Abri100")

    def test_exploitant_nom_is_none_when_no_exploitant(self):
        bd = BeneficierDe.objects.create(
            id_beneficier_de=101,
            exploitant=None,
            date_debut=date(2024, 1, 1),
        )
        data = BeneficierDeSerializer(bd).data
        self.assertIsNone(data["properties"]["exploitant_nom"])

    def test_abri_description_is_none_when_no_abri_urgence(self):
        bd = BeneficierDe.objects.create(
            id_beneficier_de=102,
            abri_urgence=None,
            date_debut=date(2024, 1, 1),
        )
        data = BeneficierDeSerializer(bd).data
        self.assertIsNone(data["properties"]["abri_description"])


# ============================================================================
# PlanDeSuiviSerializer
# ============================================================================


class PlanDeSuiviSerializerTest(TestCase):
    """Tests for the type_suivi_detail and unite_pastorale_detail nested fields."""

    def test_type_suivi_detail_contains_description(self):
        ts = TypeDeSuivi.objects.create(id_type_suivi=100, description="SuiviDesc")
        up = UnitePastorale.objects.create(
            id_unite_pastorale=103,
            code_up="UP103",
            nom_up="UP103 Nom",
            geom_active=_up_geom(),
        )
        plan = PlanDeSuivi.objects.create(
            id_plan_suivi=100,
            description="Plan100",
            type_suivi=ts,
            unite_pastorale=up,
        )
        data = PlanDeSuiviSerializer(plan).data
        self.assertIn("description", data["type_suivi_detail"])

    def test_unite_pastorale_detail_contains_nom_up(self):
        ts = TypeDeSuivi.objects.create(id_type_suivi=101, description="SuiviDesc2")
        up = UnitePastorale.objects.create(
            id_unite_pastorale=104,
            code_up="UP104",
            nom_up="UP104 Nom",
            geom_active=_up_geom(),
        )
        plan = PlanDeSuivi.objects.create(
            id_plan_suivi=101,
            description="Plan101",
            type_suivi=ts,
            unite_pastorale=up,
        )
        data = PlanDeSuiviSerializer(plan).data
        self.assertIn("nom_up", data["unite_pastorale_detail"])


# ============================================================================
# MesureDePlanSerializer
# ============================================================================


class MesureDePlanSerializerTest(TestCase):
    """Tests for the type_mesure_detail and plan_suivi_detail nested fields."""

    def _make_plan(self):
        return PlanDeSuivi.objects.create(id_plan_suivi=102, description="PlanBase")

    def test_type_mesure_detail_contains_description(self):
        tm = TypeDeMesure.objects.create(id_type_mesure=100, description="MesureDesc")
        plan = self._make_plan()
        mesure = MesureDePlan.objects.create(
            id_mesure_plan=100,
            description="Mesure100",
            type_mesure=tm,
            plan_suivi=plan,
        )
        data = MesureDePlanSerializer(mesure).data
        self.assertIn("description", data["properties"]["type_mesure_detail"])

    def test_plan_suivi_detail_contains_description(self):
        plan = self._make_plan()
        mesure = MesureDePlan.objects.create(
            id_mesure_plan=101,
            description="Mesure101",
            plan_suivi=plan,
        )
        data = MesureDePlanSerializer(mesure).data
        self.assertIn("description", data["properties"]["plan_suivi_detail"])


# ============================================================================
# SubventionPNVSerializer
# ============================================================================


class SubventionPNVSerializerTest(TestCase):
    """Tests for the exploitant_detail nested field."""

    def test_exploitant_detail_contains_nom_exploitant(self):
        exp = Exploitant.objects.create(id_exploitant=104, nom_exploitant="ExpSub")
        sub = SubventionPNV.objects.create(
            id_subvention=100,
            montant=Decimal("1000.00"),
            exploitant=exp,
        )
        data = SubventionPNVSerializer(sub).data
        self.assertIn("nom_exploitant", data["exploitant_detail"])


# ============================================================================
# ============================================================================
# Simple field-presence tests (one method per serializer)
# ============================================================================


class TypeConventionSerializerFieldsTest(TestCase):
    def test_fields_present(self):
        tc = TypeConvention.objects.create(
            id_type_convention=100, description="Conv100"
        )
        data = TypeConventionSerializer(tc).data
        self.assertIn("id_type_convention", data)
        self.assertIn("description", data)


class TypeDeSuiviSerializerFieldsTest(TestCase):
    def test_fields_present(self):
        ts = TypeDeSuivi.objects.create(id_type_suivi=103, description="Suivi103")
        data = TypeDeSuiviSerializer(ts).data
        self.assertIn("id_type_suivi", data)
        self.assertIn("description", data)


class TypeDeMesureSerializerFieldsTest(TestCase):
    def test_fields_present(self):
        tm = TypeDeMesure.objects.create(id_type_mesure=101, description="Mesure101")
        data = TypeDeMesureSerializer(tm).data
        self.assertIn("id_type_mesure", data)
        self.assertIn("description", data)


class BergerSerializerFieldsTest(TestCase):
    def test_fields_present(self):
        b = Berger.objects.create(
            id_berger=101,
            nom_berger="Renard",
            prenom_berger="Paul",
        )
        data = BergerSerializer(b).data
        self.assertIn("nom_berger", data)
        self.assertIn("prenom_berger", data)


class ProductionSerializerFieldsTest(TestCase):
    def test_fields_present(self):
        p = Production.objects.create(id_production=100, description="Lait")
        data = ProductionSerializer(p).data
        self.assertIn("id_production", data)
        self.assertIn("description", data)


class CategoriePensionSerializerFieldsTest(TestCase):
    def test_fields_present(self):
        cp = CategoriePension.objects.create(
            id_categorie_pension=100,
            description="PensionTest",
        )
        data = CategoriePensionSerializer(cp).data
        self.assertIn("id_categorie_pension", data)
        self.assertIn("description", data)


class EspeceSerializerFieldsTest(TestCase):
    def test_fields_present(self):
        e = Espece.objects.create(id_espece=100, description="Caprin")
        data = EspeceSerializer(e).data
        self.assertIn("id_espece", data)
        self.assertIn("description", data)


class RaceSerializerFieldsTest(TestCase):
    def test_fields_present(self):
        esp = Espece.objects.create(id_espece=101, description="Bovin")
        r = Race.objects.create(id_race=100, description="Salers", espece=esp)
        data = RaceSerializer(r).data
        self.assertIn("id_race", data)
        self.assertIn("description", data)
        self.assertIn("espece", data)
        self.assertIn("espece_description", data)
        self.assertEqual(data["espece_description"], "Bovin")


class CategorieAnimauxSerializerFieldsTest(TestCase):
    def test_fields_present(self):
        esp = Espece.objects.create(id_espece=102, description="Ovin")
        ca = CategorieAnimaux.objects.create(
            id_categorie_animaux=100,
            description="Agneau",
            espece=esp,
        )
        data = CategorieAnimauxSerializer(ca).data
        self.assertIn("id_categorie_animaux", data)
        self.assertIn("description", data)
        self.assertIn("espece", data)


class CheptelSerializerFieldsTest(TestCase):
    def test_fields_present(self):
        elev = Eleveur.objects.create(id_eleveur=110, nom_eleveur="ElevCheptel")
        sit = SituationDExploitation.objects.create(
            id_situation=105,
            nom_situation="SitCheptel",
        )
        cheptel = Cheptel.objects.create(
            id_cheptel=100,
            description="Troupeau100",
            eleveur=elev,
            situation_exploitation=sit,
            nombre_animaux=50,
        )
        data = CheptelSerializer(cheptel).data
        self.assertIn("id_cheptel", data)
        self.assertIn("description", data)


class TypeEvenementSerializerFieldsTest(TestCase):
    def test_fields_present(self):
        te = TypeEvenement.objects.create(
            id_type_evenement=100,
            description="Incendie",
        )
        data = TypeEvenementSerializer(te).data
        self.assertIn("id_type_evenement", data)
        self.assertIn("description", data)
        self.assertIn("created_by", data)
        self.assertIn("created_on", data)
        self.assertIn("modified_by", data)
        self.assertIn("modified_on", data)


class TypeEquipementSerializerFieldsTest(TestCase):
    def test_fields_present(self):
        te = TypeEquipement.objects.create(
            id_type_equipement=100,
            description="Clôture",
            categorie="Alpage",
        )
        data = TypeEquipementSerializer(te).data
        self.assertIn("id_type_equipement", data)
        self.assertIn("description", data)
        self.assertIn("categorie", data)
        self.assertIn("created_by", data)
        self.assertIn("created_on", data)
        self.assertIn("modified_by", data)
        self.assertIn("modified_on", data)


class AbriDUrgenceSerializerFieldsTest(TestCase):
    def test_fields_present(self):
        a = AbriDUrgence.objects.create(
            id_abri_urgence=100,
            description="Cabane100",
            etat="Bon",
        )
        data = AbriDUrgenceSerializer(a).data
        self.assertIn("id_abri_urgence", data)
        self.assertIn("description", data)
        self.assertIn("etat", data)
        self.assertIn("created_by", data)
        self.assertIn("created_on", data)
        self.assertIn("modified_by", data)
        self.assertIn("modified_on", data)


# ============================================================================
# Helpers communs aux nouveaux tests
# ============================================================================


def _make_situation(pk, nom, date_debut=None, date_fin=None, up=None):
    return SituationDExploitation.objects.create(
        id_situation=pk,
        nom_situation=nom,
        date_debut=date_debut,
        date_fin=date_fin,
        unite_pastorale=up,
    )


# ============================================================================
# GeometrieUnitePastoraleSerializer — validate()
# ============================================================================


class GeometrieUnitePastoraleSerializerTest(TestCase):

    def setUp(self):
        self.up = UnitePastorale.objects.create(
            id_unite_pastorale=200,
            code_up="UP200",
            nom_up="UP 200",
            geom_active=_up_geom(),
        )

    def _data(self, debut, fin):
        return {
            "type": "Feature",
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [[[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]],
            },
            "properties": {
                "unite_pastorale": self.up.id_unite_pastorale,
                "date_debut_validite": str(debut),
                "date_fin_validite": str(fin),
            },
        }

    def test_valid_dates_accepted(self):
        ser = GeometrieUnitePastoraleSerializer(
            data=self._data("2020-01-01", "2021-01-01")
        )
        self.assertTrue(ser.is_valid(), ser.errors)

    def test_equal_dates_accepted(self):
        ser = GeometrieUnitePastoraleSerializer(
            data=self._data("2020-06-01", "2020-06-01")
        )
        self.assertTrue(ser.is_valid(), ser.errors)

    def test_debut_after_fin_rejected(self):
        ser = GeometrieUnitePastoraleSerializer(
            data=self._data("2021-01-01", "2020-01-01")
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("date_fin_validite", ser.errors)


# ============================================================================
# SituationDExploitationSerializer — validate() + to_internal_value()
# ============================================================================


class SituationDExploitationValidationTest(TestCase):

    def test_date_debut_after_date_fin_rejected(self):
        ser = SituationDExploitationSerializer(
            data={
                "id_situation": 200,
                "nom_situation": "Sit200",
                "date_debut": "2023-09-01",
                "date_fin": "2023-06-01",
                "unite_pastorale": None,
            }
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("date_fin", ser.errors)

    def test_valid_dates_accepted(self):
        ser = SituationDExploitationSerializer(
            data={
                "id_situation": 201,
                "nom_situation": "Sit201",
                "date_debut": "2023-06-01",
                "date_fin": "2023-09-30",
                "unite_pastorale": None,
            }
        )
        self.assertTrue(ser.is_valid(), ser.errors)

    def test_to_internal_value_accepts_id_key_alias(self):
        # The frontend sometimes sends 'id' instead of 'id_situation'.
        # to_internal_value maps the key so validation passes.
        # id_situation is read_only and therefore absent from validated_data.
        ser = SituationDExploitationSerializer(
            data={
                "id": 202,
                "nom_situation": "Sit202",
                "unite_pastorale": None,
            }
        )
        self.assertTrue(ser.is_valid(), ser.errors)
        self.assertNotIn("id_situation", ser.errors)


# ============================================================================
# ConventionDExploitationSerializer — validate()
# ============================================================================


class ConventionDExploitationSerializerTest(TestCase):

    def setUp(self):
        self.up = UnitePastorale.objects.create(
            id_unite_pastorale=210,
            code_up="UP210",
            nom_up="UP 210",
            geom_active=_up_geom(),
        )
        self.type_conv = TypeConvention.objects.create(
            id_type_convention=200,
            description="Conv200",
        )
        self.exploitant = Exploitant.objects.create(
            id_exploitant=200,
            nom_exploitant="Expl200",
        )

    def _base_data(self, **overrides):
        data = {
            "type": "Feature",
            "geometry": None,
            "properties": {
                "id_convention": 200,
                "unite_pastorale": self.up.id_unite_pastorale,
                "exploitant": self.exploitant.id_exploitant,
                "type_convention": self.type_conv.id_type_convention,
                "date_debut": "2023-01-01",
                "date_fin": "2023-12-31",
            },
        }
        data["properties"].update(overrides)
        return data

    def test_valid_data_accepted(self):
        ser = ConventionDExploitationSerializer(data=self._base_data())
        self.assertTrue(ser.is_valid(), ser.errors)

    def test_date_debut_after_date_fin_rejected(self):
        ser = ConventionDExploitationSerializer(
            data=self._base_data(date_debut="2024-01-01", date_fin="2023-01-01")
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("date_fin", ser.errors)

    def test_debut_periode_expl_after_fin_rejected(self):
        ser = ConventionDExploitationSerializer(
            data=self._base_data(
                debut_periode_expl="2023-09-01",
                fin_periode_expl="2023-06-01",
            )
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("fin_periode_expl", ser.errors)


# ============================================================================
# MesureDePlanSerializer — validate(), _validate_periode_mm_jj(), create(), update()
# ============================================================================


class MesureDePlanValidationTest(TestCase):

    def _base_data(self, **overrides):
        data = {
            "type": "Feature",
            "geometry": None,
            "properties": {
                "id_mesure_plan": 200,
                "description": "Mesure200",
                "plan_suivi": None,
                "type_mesure": None,
                "obligation": False,
            },
        }
        data["properties"].update(overrides)
        return data

    def test_valid_data_accepted(self):
        ser = MesureDePlanSerializer(data=self._base_data())
        self.assertTrue(ser.is_valid(), ser.errors)

    def test_date_debut_after_date_fin_rejected(self):
        ser = MesureDePlanSerializer(
            data=self._base_data(
                date_debut_validite="2024-01-01",
                date_fin_validite="2023-01-01",
            )
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("date_fin_validite", ser.errors)

    def test_invalid_periode_format_rejected(self):
        ser = MesureDePlanSerializer(
            data=self._base_data(debut_periode_realisation="7-15")
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("debut_periode_realisation", ser.errors)

    def test_valid_periode_format_accepted(self):
        ser = MesureDePlanSerializer(
            data=self._base_data(
                debut_periode_realisation="07-15",
                fin_periode_realisation="09-30",
            )
        )
        self.assertTrue(ser.is_valid(), ser.errors)

    def test_fin_periode_before_debut_rejected(self):
        ser = MesureDePlanSerializer(
            data=self._base_data(
                debut_periode_realisation="09-01",
                fin_periode_realisation="07-01",
            )
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("fin_periode_realisation", ser.errors)

    def test_create_sets_enjeux_m2m(self):
        e1 = Enjeu.objects.create(id_enjeu=200, description="Enjeu200")
        e2 = Enjeu.objects.create(id_enjeu=201, description="Enjeu201")
        data = self._base_data(id_mesure_plan=201, description="Mesure201")
        data["properties"]["enjeu_ids"] = [e1.id_enjeu, e2.id_enjeu]
        ser = MesureDePlanSerializer(data=data)
        self.assertTrue(ser.is_valid(), ser.errors)
        instance = ser.save()
        self.assertCountEqual(
            list(instance.enjeux.values_list("id_enjeu", flat=True)),
            [e1.id_enjeu, e2.id_enjeu],
        )

    def test_update_replaces_enjeux_m2m(self):
        e1 = Enjeu.objects.create(id_enjeu=202, description="Enjeu202")
        e2 = Enjeu.objects.create(id_enjeu=203, description="Enjeu203")
        mesure = MesureDePlan.objects.create(
            id_mesure_plan=202,
            description="Mesure202",
            obligation=False,
        )
        mesure.enjeux.set([e1])
        data = self._base_data(id_mesure_plan=202, description="Mesure202")
        data["properties"]["enjeu_ids"] = [e2.id_enjeu]
        ser = MesureDePlanSerializer(mesure, data=data)
        self.assertTrue(ser.is_valid(), ser.errors)
        updated = ser.save()
        self.assertCountEqual(
            list(updated.enjeux.values_list("id_enjeu", flat=True)),
            [e2.id_enjeu],
        )

    def test_update_without_enjeu_ids_preserves_m2m(self):
        e1 = Enjeu.objects.create(id_enjeu=204, description="Enjeu204")
        mesure = MesureDePlan.objects.create(
            id_mesure_plan=203,
            description="Mesure203",
            obligation=False,
        )
        mesure.enjeux.set([e1])
        data = self._base_data(id_mesure_plan=203, description="Mesure203 updated")
        ser = MesureDePlanSerializer(mesure, data=data)
        self.assertTrue(ser.is_valid(), ser.errors)
        updated = ser.save()
        self.assertCountEqual(
            list(updated.enjeux.values_list("id_enjeu", flat=True)),
            [e1.id_enjeu],
        )


# ============================================================================
# RealisationMesureSerializer — validate()
# ============================================================================


class RealisationMesureSerializerTest(TestCase):

    def setUp(self):
        self.mesure = MesureDePlan.objects.create(
            id_mesure_plan=210,
            description="Mesure210",
            obligation=False,
            date_debut_validite=date(2023, 6, 1),
            date_fin_validite=date(2023, 9, 30),
        )
        self.situation = _make_situation(
            210,
            "Sit210",
            date_debut=date(2023, 5, 1),
            date_fin=date(2023, 10, 31),
        )

    def _data(self, mesure_pk, situation_pk, **overrides):
        d = {
            "id_realisation_mesure": 200,
            "mesure_plan": mesure_pk,
            "situation": situation_pk,
            "statut": "non_realisee",
        }
        d.update(overrides)
        return d

    def test_compatible_periods_accepted(self):
        ser = RealisationMesureSerializer(
            data=self._data(self.mesure.id_mesure_plan, self.situation.id_situation)
        )
        self.assertTrue(ser.is_valid(), ser.errors)

    def test_mesure_debut_after_situation_fin_rejected(self):
        sit_courte = _make_situation(
            211,
            "Sit211",
            date_debut=date(2022, 1, 1),
            date_fin=date(2022, 6, 30),
        )
        ser = RealisationMesureSerializer(
            data=self._data(
                self.mesure.id_mesure_plan,
                sit_courte.id_situation,
                id_realisation_mesure=201,
            )
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("non_field_errors", ser.errors)

    def test_mesure_fin_before_situation_debut_rejected(self):
        sit_tardive = _make_situation(
            212,
            "Sit212",
            date_debut=date(2024, 1, 1),
            date_fin=date(2024, 12, 31),
        )
        ser = RealisationMesureSerializer(
            data=self._data(
                self.mesure.id_mesure_plan,
                sit_tardive.id_situation,
                id_realisation_mesure=202,
            )
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("non_field_errors", ser.errors)


# ============================================================================
# GardeSituationSerializer — validate() étendu
# ============================================================================


class GardeSituationValidationTest(TestCase):

    def setUp(self):
        self.situation = _make_situation(
            220,
            "Sit220",
            date_debut=date(2023, 6, 1),
            date_fin=date(2023, 9, 30),
        )
        self.berger = Berger.objects.create(
            id_berger=200, nom_berger="Mouton", prenom_berger="Pierre"
        )

    def _data(self, debut, fin, pk=200):
        return {
            "id_garde_situation": pk,
            "date_debut": str(debut),
            "date_fin": str(fin),
            "berger": self.berger.id_berger,
            "situation_exploitation": self.situation.id_situation,
        }

    def test_valid_dates_within_situation_accepted(self):
        ser = GardeSituationSerializer(data=self._data("2023-06-15", "2023-09-15"))
        self.assertTrue(ser.is_valid(), ser.errors)

    def test_date_debut_after_date_fin_rejected(self):
        ser = GardeSituationSerializer(data=self._data("2023-09-01", "2023-06-01"))
        self.assertFalse(ser.is_valid())
        self.assertIn("date_fin", ser.errors)

    def test_date_debut_before_situation_debut_rejected(self):
        ser = GardeSituationSerializer(data=self._data("2023-05-01", "2023-08-01"))
        self.assertFalse(ser.is_valid())
        self.assertIn("date_debut", ser.errors)

    def test_date_fin_after_situation_fin_rejected(self):
        ser = GardeSituationSerializer(
            data=self._data("2023-07-01", "2023-11-01", pk=201)
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("date_fin", ser.errors)


# ============================================================================
# CheptelSerializer — validate() + get_annee()
# ============================================================================


class CheptelSerializerValidationTest(TestCase):

    def setUp(self):
        self.situation = _make_situation(
            230,
            "Sit230",
            date_debut=date(2023, 6, 1),
            date_fin=date(2023, 9, 30),
        )
        self.eleveur = Eleveur.objects.create(id_eleveur=200, nom_eleveur="ElevCheptel")
        self.exploitant = Exploitant.objects.create(
            id_exploitant=210, nom_exploitant="ExplCheptel"
        )

    def _data(self, pk=200, **overrides):
        d = {
            "id_cheptel": pk,
            "description": f"Cheptel{pk}",
            "situation_exploitation": self.situation.id_situation,
            "nombre_animaux": 10,
            "eleveur": self.eleveur.id_eleveur,
            "exploitant_proprietaire": None,
            "production": None,
            "pension": None,
            "race": None,
            "categorie_animaux": None,
        }
        d.update(overrides)
        return d

    def test_valid_with_eleveur_accepted(self):
        ser = CheptelSerializer(data=self._data())
        self.assertTrue(ser.is_valid(), ser.errors)

    def test_valid_with_exploitant_accepted(self):
        ser = CheptelSerializer(
            data=self._data(
                pk=201,
                eleveur=None,
                exploitant_proprietaire=self.exploitant.id_exploitant,
            )
        )
        self.assertTrue(ser.is_valid(), ser.errors)

    def test_both_eleveur_and_exploitant_rejected(self):
        ser = CheptelSerializer(
            data=self._data(
                pk=202,
                exploitant_proprietaire=self.exploitant.id_exploitant,
            )
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("exploitant_proprietaire", ser.errors)

    def test_neither_eleveur_nor_exploitant_rejected(self):
        ser = CheptelSerializer(
            data=self._data(pk=203, eleveur=None, exploitant_proprietaire=None)
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("eleveur", ser.errors)

    def test_date_debut_after_date_fin_rejected(self):
        ser = CheptelSerializer(
            data=self._data(
                pk=204,
                date_debut="2023-09-01",
                date_fin="2023-06-01",
            )
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("date_fin", ser.errors)

    def test_date_debut_before_situation_debut_rejected(self):
        ser = CheptelSerializer(
            data=self._data(pk=205, date_debut="2023-05-01", date_fin="2023-08-01")
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("date_debut", ser.errors)

    def test_get_annee_returns_year_when_date_debut_set(self):
        cheptel = Cheptel.objects.create(
            id_cheptel=210,
            description="CheptelAnnee",
            eleveur=self.eleveur,
            situation_exploitation=self.situation,
            nombre_animaux=5,
            date_debut=date(2023, 6, 15),
        )
        data = CheptelSerializer(cheptel).data
        self.assertEqual(data["annee"], 2023)

    def test_get_annee_returns_none_when_no_date_debut(self):
        cheptel = Cheptel.objects.create(
            id_cheptel=211,
            description="CheptelSansDate",
            eleveur=self.eleveur,
            situation_exploitation=self.situation,
            nombre_animaux=5,
        )
        data = CheptelSerializer(cheptel).data
        self.assertIsNone(data["annee"])


# ============================================================================
# ExploiterSerializer — validate() dates + get_cheptel_nom() + get_situation_exploitation()
# ============================================================================


class ExploiterValidationExtendedTest(TestCase):

    def setUp(self):
        self.up = UnitePastorale.objects.create(
            id_unite_pastorale=220,
            code_up="UP220",
            nom_up="UP 220",
            geom_active=_up_geom(),
        )
        self.situation = _make_situation(
            240,
            "Sit240",
            date_debut=date(2023, 6, 1),
            date_fin=date(2023, 9, 30),
            up=self.up,
        )
        self.quartier = QuartierPasto.objects.create(
            id_quartier=200,
            nom_quartier="Q200",
            geometry=_qp_geom(),
            situation_exploitation=self.situation,
        )
        self.cheptel = Cheptel.objects.create(
            id_cheptel=220,
            description="CheptelExt",
            situation_exploitation=self.situation,
            nombre_animaux=50,
            eleveur=Eleveur.objects.create(id_eleveur=210, nom_eleveur="ElevExt"),
        )

    def _data(self, pk=200, **overrides):
        d = {
            "id_exploiter": pk,
            "quartier": self.quartier.id_quartier,
            "cheptel": self.cheptel.id_cheptel,
            "date_debut": "2023-06-15",
            "date_fin": "2023-09-15",
            "nombre_animaux": 10,
        }
        d.update(overrides)
        return d

    def test_date_debut_after_date_fin_rejected(self):
        ser = ExploiterSerializer(
            data=self._data(pk=200, date_debut="2023-09-01", date_fin="2023-06-01")
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("date_fin", ser.errors)

    def test_date_debut_before_situation_rejected(self):
        ser = ExploiterSerializer(
            data=self._data(pk=201, date_debut="2023-05-01", date_fin="2023-08-01")
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("date_debut", ser.errors)

    def test_date_fin_after_situation_rejected(self):
        ser = ExploiterSerializer(
            data=self._data(pk=202, date_debut="2023-07-01", date_fin="2023-11-01")
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("date_fin", ser.errors)

    def test_get_cheptel_nom_with_description(self):
        exp = Exploiter.objects.create(
            id_exploiter=200,
            quartier=self.quartier,
            cheptel=self.cheptel,
            date_debut=date(2023, 6, 15),
            date_fin=date(2023, 9, 15),
        )
        data = ExploiterSerializer(exp).data
        self.assertEqual(data["cheptel_nom"], "CheptelExt")

    def test_get_cheptel_nom_without_description(self):
        cheptel_sans_desc = Cheptel.objects.create(
            id_cheptel=221,
            description="placeholder",
            situation_exploitation=self.situation,
            nombre_animaux=10,
            eleveur=Eleveur.objects.create(id_eleveur=211, nom_eleveur="ElevSansDesc"),
        )
        cheptel_sans_desc.description = ""
        cheptel_sans_desc.save()
        exp = Exploiter.objects.create(
            id_exploiter=201,
            quartier=self.quartier,
            cheptel=cheptel_sans_desc,
            date_debut=date(2023, 6, 15),
            date_fin=date(2023, 9, 15),
        )
        data = ExploiterSerializer(exp).data
        self.assertEqual(
            data["cheptel_nom"], f"Troupeau #{cheptel_sans_desc.id_cheptel}"
        )

    def test_get_cheptel_nom_no_cheptel_returns_tous_troupeaux(self):
        exp = Exploiter.objects.create(
            id_exploiter=202,
            quartier=self.quartier,
            cheptel=None,
            date_debut=date(2023, 6, 15),
            date_fin=date(2023, 9, 15),
        )
        data = ExploiterSerializer(exp).data
        self.assertEqual(data["cheptel_nom"], "Tous les troupeaux")

    def test_get_situation_exploitation_from_cheptel(self):
        exp = Exploiter.objects.create(
            id_exploiter=203,
            quartier=self.quartier,
            cheptel=self.cheptel,
            date_debut=date(2023, 6, 15),
            date_fin=date(2023, 9, 15),
        )
        data = ExploiterSerializer(exp).data
        self.assertEqual(data["situation_exploitation"], self.situation.id_situation)

    def test_get_situation_exploitation_from_quartier_when_no_cheptel(self):
        exp = Exploiter.objects.create(
            id_exploiter=204,
            quartier=self.quartier,
            cheptel=None,
            date_debut=date(2023, 6, 15),
            date_fin=date(2023, 9, 15),
        )
        data = ExploiterSerializer(exp).data
        self.assertEqual(data["situation_exploitation"], self.situation.id_situation)


# ============================================================================
# UnitePastoraleSerializer — create(), update(), get_proprios_ids()
# ============================================================================


class UnitePastoraleSerializerTest(TestCase):

    def setUp(self):
        self.p1 = ProprietaireFoncier.objects.create(
            id_proprietaire=200, nom_propr="Durand"
        )
        self.p2 = ProprietaireFoncier.objects.create(
            id_proprietaire=201, nom_propr="Martin"
        )

    def _feature(self, pk, code, nom, proprios):
        return {
            "type": "Feature",
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [[[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]],
            },
            "properties": {
                "id_unite_pastorale": pk,
                "code_up": code,
                "nom_up": nom,
                "proprios": proprios,
            },
        }

    def test_create_with_proprios_links_proprietaires(self):
        ser = UnitePastoraleSerializer(
            data=self._feature(300, "UP300", "UP 300", [self.p1.id_proprietaire])
        )
        self.assertTrue(ser.is_valid(), ser.errors)
        up = ser.save()
        self.assertEqual(
            ProprietaireUnitePastorale.objects.filter(unite_pastorale=up).count(), 1
        )

    def test_create_without_proprios(self):
        ser = UnitePastoraleSerializer(data=self._feature(301, "UP301", "UP 301", []))
        self.assertTrue(ser.is_valid(), ser.errors)
        up = ser.save()
        self.assertEqual(
            ProprietaireUnitePastorale.objects.filter(unite_pastorale=up).count(), 0
        )

    def test_get_proprios_ids_returns_list(self):
        up = UnitePastorale.objects.create(
            id_unite_pastorale=302,
            code_up="UP302",
            nom_up="UP 302",
            geom_active=_up_geom(),
        )
        ProprietaireUnitePastorale.objects.create(
            unite_pastorale=up, proprietaire=self.p1
        )
        ProprietaireUnitePastorale.objects.create(
            unite_pastorale=up, proprietaire=self.p2
        )
        data = UnitePastoraleSerializer(up).data
        self.assertCountEqual(
            data["properties"]["proprios_ids"],
            [self.p1.id_proprietaire, self.p2.id_proprietaire],
        )

    def test_update_adds_proprio(self):
        up = UnitePastorale.objects.create(
            id_unite_pastorale=303,
            code_up="UP303",
            nom_up="UP 303",
            geom_active=_up_geom(),
        )
        ProprietaireUnitePastorale.objects.create(
            unite_pastorale=up, proprietaire=self.p1
        )
        feature = self._feature(
            303,
            "UP303",
            "UP 303 updated",
            [self.p1.id_proprietaire, self.p2.id_proprietaire],
        )
        ser = UnitePastoraleSerializer(up, data=feature)
        self.assertTrue(ser.is_valid(), ser.errors)
        ser.save()
        self.assertEqual(
            ProprietaireUnitePastorale.objects.filter(unite_pastorale=up).count(), 2
        )

    def test_update_removes_proprio(self):
        up = UnitePastorale.objects.create(
            id_unite_pastorale=304,
            code_up="UP304",
            nom_up="UP 304",
            geom_active=_up_geom(),
        )
        ProprietaireUnitePastorale.objects.create(
            unite_pastorale=up, proprietaire=self.p1
        )
        ProprietaireUnitePastorale.objects.create(
            unite_pastorale=up, proprietaire=self.p2
        )
        feature = self._feature(304, "UP304", "UP 304", [self.p2.id_proprietaire])
        ser = UnitePastoraleSerializer(up, data=feature)
        self.assertTrue(ser.is_valid(), ser.errors)
        ser.save()
        self.assertFalse(
            ProprietaireUnitePastorale.objects.filter(
                unite_pastorale=up, proprietaire=self.p1
            ).exists()
        )
        self.assertTrue(
            ProprietaireUnitePastorale.objects.filter(
                unite_pastorale=up, proprietaire=self.p2
            ).exists()
        )


# ============================================================================
# ExploitantSerializer — validate() cycle + update() + get_membres_exploitants_ids()
# ============================================================================


class ExploitantSerializerExtendedTest(TestCase):

    def setUp(self):
        self.exp_a = Exploitant.objects.create(
            id_exploitant=300, nom_exploitant="ExplA"
        )
        self.exp_b = Exploitant.objects.create(
            id_exploitant=301, nom_exploitant="ExplB"
        )
        self.eleveur = Eleveur.objects.create(id_eleveur=300, nom_eleveur="ElevExt2")

    def test_self_membership_rejected(self):
        ser = ExploitantSerializer(
            self.exp_a,
            data={
                "nom_exploitant": "ExplA",
                "membres_exploitants": [self.exp_a.id_exploitant],
                "type_exploitant": None,
                "president": None,
            },
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("membres_exploitants", ser.errors)

    def test_cycle_detection_rejected(self):
        # B est déjà membre de A ; tenter de faire B membre de A à nouveau → cycle détecté
        EtreCompose.objects.create(
            exploitant=self.exp_a,
            exploitant_membre=self.exp_b,
        )
        ser = ExploitantSerializer(
            self.exp_a,
            data={
                "nom_exploitant": "ExplA",
                "membres_exploitants": [self.exp_b.id_exploitant],
                "type_exploitant": None,
                "president": None,
            },
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("membres_exploitants", ser.errors)

    def test_get_membres_exploitants_ids(self):
        EtreCompose.objects.create(exploitant=self.exp_a, exploitant_membre=self.exp_b)
        data = ExploitantSerializer(self.exp_a).data
        self.assertIn(self.exp_b.id_exploitant, data["membres_exploitants_ids"])

    def test_update_preserves_membres_when_not_provided(self):
        EtreCompose.objects.create(exploitant=self.exp_a, eleveur=self.eleveur)
        ser = ExploitantSerializer(
            self.exp_a,
            data={
                "nom_exploitant": "ExplA Renamed",
                "type_exploitant": None,
                "president": None,
            },
        )
        self.assertTrue(ser.is_valid(), ser.errors)
        ser.save()
        self.assertTrue(
            EtreCompose.objects.filter(
                exploitant=self.exp_a, eleveur=self.eleveur
            ).exists()
        )

    def test_update_replaces_membres_when_provided(self):
        e2 = Eleveur.objects.create(id_eleveur=301, nom_eleveur="ElevNew")
        EtreCompose.objects.create(exploitant=self.exp_a, eleveur=self.eleveur)
        ser = ExploitantSerializer(
            self.exp_a,
            data={
                "nom_exploitant": "ExplA",
                "membres": [e2.id_eleveur],
                "type_exploitant": None,
                "president": None,
            },
        )
        self.assertTrue(ser.is_valid(), ser.errors)
        ser.save()
        self.assertFalse(
            EtreCompose.objects.filter(
                exploitant=self.exp_a, eleveur=self.eleveur
            ).exists()
        )
        self.assertTrue(
            EtreCompose.objects.filter(exploitant=self.exp_a, eleveur=e2).exists()
        )


# ============================================================================
# VisiteSerializer — create(), update(), SerializerMethodFields
# ============================================================================


class VisiteSerializerTest(TestCase):

    def setUp(self):
        User = get_user_model()
        self.up = UnitePastorale.objects.create(
            id_unite_pastorale=310,
            code_up="UP310",
            nom_up="UP 310",
            geom_active=_up_geom(),
        )
        self.eleveur = Eleveur.objects.create(
            id_eleveur=310, nom_eleveur="ElevVisite", prenom_eleveur="Jean"
        )
        self.user = User.objects.create_user(
            username="visite_obs",
            first_name="Alice",
            last_name="Dupont",
            password="pass",
        )
        self.user_no_name = User.objects.create_user(
            username="visite_obs2",
            password="pass",
        )

    def test_create_sets_m2m_relations(self):
        ser = VisiteSerializer(
            data={
                "id_visite": 200,
                "date_visite": "2023-07-15",
                "description": "Visite test",
                "unite_pastorale": self.up.id_unite_pastorale,
                "contact_alpagiste_ids": [self.eleveur.id_eleveur],
                "observateur_ids": [self.user.id],
            }
        )
        self.assertTrue(ser.is_valid(), ser.errors)
        visite = ser.save()
        self.assertIn(self.eleveur, visite.contacts_alpagistes.all())
        self.assertIn(self.user, visite.observateurs.all())

    def test_create_without_m2m(self):
        ser = VisiteSerializer(
            data={
                "id_visite": 201,
                "date_visite": "2023-07-16",
                "description": "Visite sans M2M",
                "unite_pastorale": self.up.id_unite_pastorale,
            }
        )
        self.assertTrue(ser.is_valid(), ser.errors)
        visite = ser.save()
        self.assertEqual(visite.contacts_alpagistes.count(), 0)
        self.assertEqual(visite.observateurs.count(), 0)

    def test_update_replaces_m2m_when_ids_provided(self):
        visite = Visite.objects.create(
            id_visite=202,
            date_visite=date(2023, 7, 15),
            description="Visite update",
            unite_pastorale=self.up,
        )
        visite.contacts_alpagistes.set([self.eleveur])
        e2 = Eleveur.objects.create(id_eleveur=311, nom_eleveur="ElevNew2")
        ser = VisiteSerializer(
            visite,
            data={
                "id_visite": 202,
                "date_visite": "2023-07-15",
                "description": "Visite update",
                "unite_pastorale": self.up.id_unite_pastorale,
                "contact_alpagiste_ids": [e2.id_eleveur],
            },
        )
        self.assertTrue(ser.is_valid(), ser.errors)
        updated = ser.save()
        self.assertNotIn(self.eleveur, updated.contacts_alpagistes.all())
        self.assertIn(e2, updated.contacts_alpagistes.all())

    def test_update_preserves_m2m_when_ids_not_provided(self):
        visite = Visite.objects.create(
            id_visite=203,
            date_visite=date(2023, 7, 15),
            description="Visite preserve",
            unite_pastorale=self.up,
        )
        visite.contacts_alpagistes.set([self.eleveur])
        ser = VisiteSerializer(
            visite,
            data={
                "id_visite": 203,
                "date_visite": "2023-07-15",
                "description": "Visite preserve updated",
                "unite_pastorale": self.up.id_unite_pastorale,
            },
        )
        self.assertTrue(ser.is_valid(), ser.errors)
        updated = ser.save()
        self.assertIn(self.eleveur, updated.contacts_alpagistes.all())

    def test_get_contacts_alpagistes_format(self):
        visite = Visite.objects.create(
            id_visite=204,
            date_visite=date(2023, 7, 15),
            description="Visite contacts",
            unite_pastorale=self.up,
        )
        visite.contacts_alpagistes.set([self.eleveur])
        data = VisiteSerializer(visite).data
        contacts = data["contacts_alpagistes"]
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0]["id"], self.eleveur.id_eleveur)
        self.assertIn("full_name", contacts[0])
        self.assertEqual(contacts[0]["full_name"], "ElevVisite Jean")

    def test_get_observateurs_with_full_name(self):
        visite = Visite.objects.create(
            id_visite=205,
            date_visite=date(2023, 7, 15),
            description="Visite obs",
            unite_pastorale=self.up,
        )
        visite.observateurs.set([self.user])
        data = VisiteSerializer(visite).data
        obs = data["observateurs"]
        self.assertEqual(len(obs), 1)
        self.assertEqual(obs[0]["full_name"], "Alice Dupont")

    def test_get_observateurs_falls_back_to_username(self):
        visite = Visite.objects.create(
            id_visite=206,
            date_visite=date(2023, 7, 15),
            description="Visite obs2",
            unite_pastorale=self.up,
        )
        visite.observateurs.set([self.user_no_name])
        data = VisiteSerializer(visite).data
        obs = data["observateurs"]
        self.assertEqual(obs[0]["full_name"], "visite_obs2")

    def test_get_unite_pastorale_nom_when_present(self):
        visite = Visite.objects.create(
            id_visite=207,
            date_visite=date(2023, 7, 15),
            description="Visite UP",
            unite_pastorale=self.up,
        )
        data = VisiteSerializer(visite).data
        self.assertEqual(data["unite_pastorale_nom"], "UP 310")


# ============================================================================
# ProprietaireUnitePastoraleSerializer — get_proprietaire_nom()
# ============================================================================


class ProprietaireUnitePastoraleSerializerTest(TestCase):

    def setUp(self):
        self.up = UnitePastorale.objects.create(
            id_unite_pastorale=320,
            code_up="UP320",
            nom_up="UP 320",
            geom_active=_up_geom(),
        )

    def test_proprietaire_nom_with_prenom(self):
        proprio = ProprietaireFoncier.objects.create(
            id_proprietaire=300,
            nom_propr="Durand",
            prenom_propr="Jacques",
        )
        lien = ProprietaireUnitePastorale.objects.create(
            unite_pastorale=self.up, proprietaire=proprio
        )
        data = ProprietaireUnitePastoraleSerializer(lien).data
        self.assertEqual(data["proprietaire_nom"], "Durand Jacques")

    def test_proprietaire_nom_without_prenom(self):
        proprio = ProprietaireFoncier.objects.create(
            id_proprietaire=301,
            nom_propr="Martin",
            prenom_propr=None,
        )
        lien = ProprietaireUnitePastorale.objects.create(
            unite_pastorale=self.up, proprietaire=proprio
        )
        data = ProprietaireUnitePastoraleSerializer(lien).data
        self.assertEqual(data["proprietaire_nom"], "Martin")

    def test_up_nom_field(self):
        proprio = ProprietaireFoncier.objects.create(
            id_proprietaire=302, nom_propr="Roux"
        )
        lien = ProprietaireUnitePastorale.objects.create(
            unite_pastorale=self.up, proprietaire=proprio
        )
        data = ProprietaireUnitePastoraleSerializer(lien).data
        self.assertEqual(data["up_nom"], "UP 320")
