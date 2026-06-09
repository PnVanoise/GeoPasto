import os
import sys
import django
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geopasto.settings")
django.setup()

from django.core.serializers import serialize

from suivi_pasto.models import (
    UnitePastorale,
    GeometrieUnitePastorale,
    ProprietaireFoncier,
    ProprietaireUnitePastorale,
    SituationDExploitation,
    ConventionDExploitation,
    QuartierPasto,
    GardeSituation,
    Ruche,
    Exploiter,
    EquipementAlpage,
    EquipementExploitant,
    Logement,
    BeneficierDe,
    AbriDUrgence,
    AbriDUrgenceCommodite,
    PlanDeSuivi,
    MesureDePlan,
    RealisationMesure,
    Evenement,
    Visite,
    Cheptel,
    Eleveur,
    Exploitant,
    EtreCompose,
    Berger,
    SubventionPNV,
)

UP_ID = 109

up = UnitePastorale.objects.filter(id_unite_pastorale=UP_ID)
situations = SituationDExploitation.objects.filter(unite_pastorale_id=UP_ID)
situation_ids = list(situations.values_list("pk", flat=True))
exploitant_ids = list(situations.values_list("exploitant_id", flat=True))
exploitants = Exploitant.objects.filter(pk__in=exploitant_ids)
eleveur_ids = set(
    list(
        EtreCompose.objects.filter(exploitant_id__in=exploitant_ids).values_list(
            "eleveur_id", flat=True
        )
    )
    + list(
        Cheptel.objects.filter(situation_exploitation_id__in=situation_ids).values_list(
            "eleveur_id", flat=True
        )
    )
)
eleveurs = Eleveur.objects.filter(pk__in=eleveur_ids)
plans = PlanDeSuivi.objects.filter(unite_pastorale_id=UP_ID)
plan_ids = list(plans.values_list("pk", flat=True))
mesures = MesureDePlan.objects.filter(plan_suivi_id__in=plan_ids)
mesure_ids = list(mesures.values_list("pk", flat=True))
quartiers = QuartierPasto.objects.filter(situation_exploitation_id__in=situation_ids)
quartier_ids = list(quartiers.values_list("pk", flat=True))
cheptels = Cheptel.objects.filter(situation_exploitation_id__in=situation_ids)
cheptel_ids = list(cheptels.values_list("pk", flat=True))
berger_ids = GardeSituation.objects.filter(
    situation_exploitation_id__in=situation_ids
).values_list("berger_id", flat=True)
bergers = Berger.objects.filter(pk__in=berger_ids)
proprietaire_ids = ProprietaireUnitePastorale.objects.filter(
    unite_pastorale_id=UP_ID
).values_list("proprietaire_id", flat=True)

querysets = [
    ProprietaireFoncier.objects.filter(pk__in=proprietaire_ids),
    eleveurs,
    exploitants,
    EtreCompose.objects.filter(exploitant_id__in=exploitant_ids),
    up,
    GeometrieUnitePastorale.objects.filter(unite_pastorale_id=UP_ID),
    ProprietaireUnitePastorale.objects.filter(unite_pastorale_id=UP_ID),
    ConventionDExploitation.objects.filter(unite_pastorale_id=UP_ID),
    situations,
    quartiers,
    bergers,
    GardeSituation.objects.filter(situation_exploitation_id__in=situation_ids),
    cheptels,
    Exploiter.objects.filter(cheptel_id__in=cheptel_ids),
    Ruche.objects.filter(situation_exploitation_id__in=situation_ids),
    EquipementAlpage.objects.filter(unite_pastorale_id=UP_ID),
    AbriDUrgence.objects.filter(
        beneficiaires__exploitant_id__in=exploitant_ids
    ).distinct(),
    AbriDUrgenceCommodite.objects.filter(
        abri_urgence__beneficiaires__exploitant_id__in=exploitant_ids
    ).distinct(),
    BeneficierDe.objects.filter(exploitant_id__in=exploitant_ids),
    EquipementExploitant.objects.filter(situation_exploitation_id__in=situation_ids),
    Logement.objects.filter(unite_pastorale_id=UP_ID),
    plans,
    mesures,
    RealisationMesure.objects.filter(mesure_plan_id__in=mesure_ids),
    Evenement.objects.filter(situation_id__in=situation_ids),
    Visite.objects.filter(unite_pastorale_id=UP_ID),
    SubventionPNV.objects.filter(exploitant_id__in=exploitant_ids),
]

all_objects = []
for qs in querysets:
    all_objects.extend(list(qs))

output = json.loads(serialize("json", all_objects, indent=2))
filename = f"up_{UP_ID}.json"
with open(filename, "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Exporté {len(output)} objets dans {filename}")
for qs in querysets:
    count = qs.count()
    if count:
        print(f"  {qs.model.__name__}: {count}")
