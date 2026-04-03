import pytest

from alpages import models as m


@pytest.mark.parametrize(
    "cls,kwargs,expected",
    [
        (m.UnitePastorale, {"nom_up": "UP1"}, "UP1"),
        (m.ProprietaireFoncier, {"nom_propr": "Dupont"}, "Dupont"),
        (
            m.UPProprietaire,
            {"proprietaire": m.ProprietaireFoncier(nom_propr="P1"), "unite_pastorale": m.UnitePastorale(nom_up="U1")},
            "P1 est propriétaire de U1",
        ),
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
        (m.Exploitant, {"nom_exploitant": "EXP1"}, "EXP1"),
        (
            m.EtreCompose,
            {"eleveur": m.Eleveur(nom_eleveur="ELV"), "exploitant": m.Exploitant(nom_exploitant="EXP")},
            "ELV est membre de EXP",
        ),
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
        (m.TypeCheptel, {"description": "TCH"}, "TCH"),
        (
            m.Elever,
            {
                "eleveur": m.Eleveur(nom_eleveur="EL"),
                "type_cheptel": m.TypeCheptel(description="TC"),
                "situation_exploitation": m.SituationDExploitation(nom_situation="SIT"),
                "nombre_animaux": 5,
            },
            "EL élève TC dans la situation SIT",
        ),
        (m.Production, {"description": "PROD"}, "PROD"),
        (m.Categorie_pension, {"description": "CATP"}, "CATP"),
        (m.Espece, {"description": "ESP"}, "ESP"),
        (m.Race, {"description": "RACE"}, "RACE"),
        (m.Categorie_animaux, {"description": "CATA"}, "CATA"),
        (
            m.Cheptel,
            {
                "eleveur": m.Eleveur(nom_eleveur="ELV"),
                "type_cheptel": m.Type_cheptel(description="TTC"),
                "situation_exploitation": m.SituationDExploitation(nom_situation="SIT"),
                "description": "CHPT",
                "nombre_animaux": 3,
            },
            "ELV élève TTC dans la situation SIT",
        ),
        (m.Type_cheptel, {"description": "TCT"}, "TCT"),
        (m.TypeEvenement, {"description": "TE"}, "TE"),
        (m.Evenement, {"description": "EVT"}, "EVT"),
        (m.TypeEquipement, {"description": "TEQ", "categorie": "CAT"}, "TEQ"),
        (m.QuartierUP, {"quartier_code": "QC"}, "QC"),
        (m.LogementTest, {"nom_logement_test": "LT"}, "LT"),
    ],
)
def test_model_strs(cls, kwargs, expected):
    # instantiate without saving to DB (avoids geometry/DB constraints)
    inst = cls(**kwargs)
    assert str(inst) == expected
