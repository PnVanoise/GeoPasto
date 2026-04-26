import pytest

from alpages import models as m


@pytest.mark.parametrize(
    "cls,kwargs,expected",
    [
        (m.UnitePastorale, {"nom_up": "UP1"}, "UP1"),
        (m.ProprietaireFoncier, {"nom_propr": "Dupont"}, "Dupont"),
        (m.QuartierPasto, {"nom_quartier": "Q1"}, "Q1"),
        (m.TypeDeSuivi, {"description": "SUIVI"}, "SUIVI"),
        (m.PlanDeSuivi, {"description": "PLAN1"}, "PLAN1"),
        (m.TypeDeMesure, {"description": "MESURE"}, "MESURE"),
        (m.MesureDePlan, {"description": "MESUREPLAN"}, "MESUREPLAN"),
        (m.TypeConvention, {"description": "CONV"}, "CONV"),
        (m.ConventionDExploitation, {"id_convention": 42}, "42"),
        (m.SituationDExploitation, {"nom_situation": "SIT"}, "SIT"),
        (m.Eleveur, {"nom_eleveur": "E1"}, "E1"),
        (m.TypeDExploitant, {"description": "TYPEEX"}, "TYPEEX"),
        (m.SubventionPNV, {"description": "SUBV"}, "SUBV"),
        (m.Commodite, {"description": "COMMO"}, "COMMO"),
        (m.AbriDUrgence, {"description": "ABRI"}, "ABRI"),
        (
            m.AbriDUrgenceCommodite,
            {"abri_urgence": m.AbriDUrgence(description="A"), "commodite": m.Commodite(description="C"), "quantite": "2"},
            "A a 2 de C",
        ),
        (m.BeneficierDe, {"exploitant": m.Exploitant(nom_exploitant="EXP"), "abri_urgence": m.AbriDUrgence(description="AB")}, "EXP bénéficie de AB"),
        (m.Ruche, {"description": "R1"}, "R1"),
        (m.Berger, {"nom_berger": "B1", "prenom_berger": "P1"}, "B1"),
        (m.GardeSituation, {"id_garde_situation": 7}, "7"),
        (m.Production, {"description": "PROD"}, "PROD"),
        (m.CategoriePension, {"description": "CATP"}, "CATP"),
        (m.Espece, {"description": "ESP"}, "ESP"),
        (m.Race, {"description": "RACE"}, "RACE"),
        (m.CategorieAnimaux, {"description": "CATA"}, "CATA"),
        (
            m.Cheptel,
            {
                "eleveur": m.Eleveur(nom_eleveur="ELV"),
                "type_cheptel": m.TypeCheptel(description="TTC"),
                "situation_exploitation": m.SituationDExploitation(nom_situation="SIT"),
                "description": "CHPT",
                "nombre_animaux": 3,
            },
            "ELV élève TTC dans la situation SIT",
        ),
        (m.TypeCheptel, {"description": "TCT"}, "TCT"),
        (m.TypeEvenement, {"description": "TE"}, "TE"),
        (m.Evenement, {"description": "EVT"}, "EVT"),
        (m.TypeEquipement, {"description": "TEQ", "categorie": "CAT"}, "TEQ"),
    ],
)
def test_model_strs(cls, kwargs, expected):
    # instantiate without saving to DB (avoids geometry/DB constraints)
    inst = cls(**kwargs)
    assert str(inst) == expected
