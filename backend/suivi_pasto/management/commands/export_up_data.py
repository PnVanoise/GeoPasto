import json
from datetime import date, datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from suivi_pasto.models import (
    AbriDUrgence,
    AbriDUrgenceCommodite,
    Berger,
    BeneficierDe,
    Cheptel,
    ConventionDExploitation,
    EquipementAlpage,
    EquipementExploitant,
    EtreCompose,
    Eleveur,
    Evenement,
    Exploitant,
    Exploiter,
    GardeSituation,
    Logement,
    MesureDePlan,
    PlanDeSuivi,
    ProprietaireFoncier,
    ProprietaireUnitePastorale,
    QuartierPasto,
    RealisationMesure,
    Ruche,
    SituationDExploitation,
    SubventionPNV,
    UnitePastorale,
    Visite,
)

User = get_user_model()


def _val(v):
    if v is None:
        return None
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    if isinstance(v, Decimal):
        return str(v)
    if hasattr(v, "ewkt"):
        return v.ewkt
    return v


def serialize_qs(qs):
    """Sérialise un queryset en liste de {pk, fields}. Ignore created_on/modified_on."""
    result = []
    model = qs.model
    pk_attname = model._meta.pk.attname
    skip = {"created_on", "modified_on"}

    for obj in qs:
        fields = {}
        for f in model._meta.fields:
            if f.attname in skip:
                continue
            if f.primary_key:
                continue
            fields[f.attname] = _val(getattr(obj, f.attname))
        result.append({"pk": getattr(obj, pk_attname), "fields": fields})
    return result


class Command(BaseCommand):
    help = (
        "Exporte toutes les données liées à une ou plusieurs UPs. "
        "Produit un fichier JSON utilisable par import_up_data."
    )

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--ups",
            metavar="CODES",
            help="Codes UP séparés par des virgules (ex : UP001,UP002)",
        )
        group.add_argument(
            "--up-ids",
            metavar="IDS",
            help="IDs UP séparés par des virgules (ex : 3,7)",
        )
        parser.add_argument("--output", required=True, metavar="FICHIER")

    def handle(self, **options):
        # --- 1. Résolution des UPs ---
        if options["ups"]:
            codes = [c.strip() for c in options["ups"].split(",")]
            ups = list(UnitePastorale.objects.filter(code_up__in=codes))
            found_codes = {up.code_up for up in ups}
            missing = set(codes) - found_codes
            if missing:
                raise CommandError(f"UPs introuvables : {', '.join(sorted(missing))}")
        else:
            ids = [int(i.strip()) for i in options["up_ids"].split(",")]
            ups = list(UnitePastorale.objects.filter(id_unite_pastorale__in=ids))
            if len(ups) != len(ids):
                raise CommandError("Certains IDs UP sont introuvables")

        up_ids = {up.id_unite_pastorale for up in ups}
        self.stdout.write(
            f"Export pour {len(ups)} UP(s) : {[up.code_up for up in ups]}"
        )

        # --- 2. Collecte des IDs par modèle ---

        situation_ids = set(
            SituationDExploitation.objects.filter(
                unite_pastorale_id__in=up_ids
            ).values_list("id_situation", flat=True)
        )

        # Exploitants directs (situations + conventions)
        exploitant_ids = set(
            SituationDExploitation.objects.filter(id_situation__in=situation_ids)
            .exclude(exploitant__isnull=True)
            .values_list("exploitant_id", flat=True)
        )
        exploitant_ids.update(
            ConventionDExploitation.objects.filter(unite_pastorale_id__in=up_ids)
            .exclude(exploitant__isnull=True)
            .values_list("exploitant_id", flat=True)
        )
        exploitant_ids.update(
            SubventionPNV.objects.filter(exploitant_id__in=exploitant_ids).values_list(
                "exploitant_id", flat=True
            )
        )

        # EtreCompose (membres des exploitants)
        etre_compose_qs = EtreCompose.objects.filter(exploitant_id__in=exploitant_ids)
        membre_expl_ids = set(
            etre_compose_qs.exclude(exploitant_membre__isnull=True).values_list(
                "exploitant_membre_id", flat=True
            )
        )
        if membre_expl_ids:
            exploitant_ids.update(membre_expl_ids)
            extra_ec = EtreCompose.objects.filter(exploitant_id__in=membre_expl_ids)
            etre_compose_qs = (etre_compose_qs | extra_ec).distinct()

        # Éleveurs
        eleveur_ids = set(
            etre_compose_qs.exclude(eleveur__isnull=True).values_list(
                "eleveur_id", flat=True
            )
        )
        eleveur_ids.update(
            Exploitant.objects.filter(id_exploitant__in=exploitant_ids)
            .exclude(president__isnull=True)
            .values_list("president_id", flat=True)
        )
        cheptel_ids = set(
            Cheptel.objects.filter(
                situation_exploitation_id__in=situation_ids
            ).values_list("id_cheptel", flat=True)
        )
        eleveur_ids.update(
            Cheptel.objects.filter(id_cheptel__in=cheptel_ids)
            .exclude(eleveur__isnull=True)
            .values_list("eleveur_id", flat=True)
        )
        visite_ids = set(
            Visite.objects.filter(unite_pastorale_id__in=up_ids).values_list(
                "id_visite", flat=True
            )
        )
        for v in Visite.objects.filter(id_visite__in=visite_ids).prefetch_related(
            "contacts_alpagistes"
        ):
            eleveur_ids.update(
                v.contacts_alpagistes.values_list("id_eleveur", flat=True)
            )

        berger_ids = set(
            GardeSituation.objects.filter(situation_exploitation_id__in=situation_ids)
            .exclude(berger__isnull=True)
            .values_list("berger_id", flat=True)
        )

        proprietaire_ids = set(
            ProprietaireUnitePastorale.objects.filter(unite_pastorale_id__in=up_ids)
            .exclude(proprietaire__isnull=True)
            .values_list("proprietaire_id", flat=True)
        )

        quartier_ids = set(
            QuartierPasto.objects.filter(
                situation_exploitation_id__in=situation_ids
            ).values_list("id_quartier", flat=True)
        )

        plan_ids = set(
            PlanDeSuivi.objects.filter(unite_pastorale_id__in=up_ids).values_list(
                "id_plan_suivi", flat=True
            )
        )

        mesure_ids = set(
            MesureDePlan.objects.filter(plan_suivi_id__in=plan_ids).values_list(
                "id_mesure_plan", flat=True
            )
        )

        abri_ids = set(
            BeneficierDe.objects.filter(exploitant_id__in=exploitant_ids)
            .exclude(abri_urgence__isnull=True)
            .values_list("abri_urgence_id", flat=True)
        )

        # --- 3. Sérialisation ---
        sections = {}

        # UPs (pour la table de résolution dans import_up_data)
        sections["UnitePastorale"] = [
            {"pk": up.id_unite_pastorale, "code_up": up.code_up} for up in ups
        ]

        sections["ProprietaireFoncier"] = serialize_qs(
            ProprietaireFoncier.objects.filter(id_proprietaire__in=proprietaire_ids)
        )
        sections["Eleveur"] = serialize_qs(
            Eleveur.objects.filter(id_eleveur__in=eleveur_ids)
        )
        sections["Exploitant"] = serialize_qs(
            Exploitant.objects.filter(id_exploitant__in=exploitant_ids)
        )
        sections["EtreCompose"] = serialize_qs(etre_compose_qs)
        sections["Berger"] = serialize_qs(
            Berger.objects.filter(id_berger__in=berger_ids)
        )
        sections["ProprietaireUnitePastorale"] = serialize_qs(
            ProprietaireUnitePastorale.objects.filter(unite_pastorale_id__in=up_ids)
        )
        sections["SituationDExploitation"] = serialize_qs(
            SituationDExploitation.objects.filter(id_situation__in=situation_ids)
        )
        sections["ConventionDExploitation"] = serialize_qs(
            ConventionDExploitation.objects.filter(unite_pastorale_id__in=up_ids)
        )
        sections["Cheptel"] = serialize_qs(
            Cheptel.objects.filter(id_cheptel__in=cheptel_ids)
        )
        sections["QuartierPasto"] = serialize_qs(
            QuartierPasto.objects.filter(id_quartier__in=quartier_ids)
        )
        sections["Exploiter"] = serialize_qs(
            Exploiter.objects.filter(cheptel_id__in=cheptel_ids)
        )
        sections["GardeSituation"] = serialize_qs(
            GardeSituation.objects.filter(situation_exploitation_id__in=situation_ids)
        )
        sections["Ruche"] = serialize_qs(
            Ruche.objects.filter(situation_exploitation_id__in=situation_ids)
        )
        sections["PlanDeSuivi"] = serialize_qs(
            PlanDeSuivi.objects.filter(id_plan_suivi__in=plan_ids)
        )
        sections["MesureDePlan"] = serialize_qs(
            MesureDePlan.objects.filter(id_mesure_plan__in=mesure_ids)
        )

        # M2M MesureDePlan ↔ Enjeu
        mp_enjeux = []
        for mp in MesureDePlan.objects.filter(
            id_mesure_plan__in=mesure_ids
        ).prefetch_related("enjeux"):
            for enjeu in mp.enjeux.all():
                mp_enjeux.append(
                    {"mesure_plan_pk": mp.id_mesure_plan, "enjeu_pk": enjeu.id_enjeu}
                )
        sections["MesureDePlan_enjeux"] = mp_enjeux

        sections["RealisationMesure"] = serialize_qs(
            RealisationMesure.objects.filter(situation_id__in=situation_ids)
        )
        sections["Evenement"] = serialize_qs(
            Evenement.objects.filter(situation_id__in=situation_ids)
        )
        sections["Visite"] = serialize_qs(
            Visite.objects.filter(id_visite__in=visite_ids)
        )

        # M2M Visite ↔ Eleveur
        visite_eleveurs = []
        for v in Visite.objects.filter(id_visite__in=visite_ids).prefetch_related(
            "contacts_alpagistes"
        ):
            for e in v.contacts_alpagistes.all():
                visite_eleveurs.append(
                    {"visite_pk": v.id_visite, "eleveur_pk": e.id_eleveur}
                )
        sections["Visite_contacts_alpagistes"] = visite_eleveurs

        # M2M Visite ↔ User (usernames)
        visite_users = []
        for v in Visite.objects.filter(id_visite__in=visite_ids).prefetch_related(
            "observateurs"
        ):
            for u in v.observateurs.all():
                visite_users.append({"visite_pk": v.id_visite, "username": u.username})
        sections["Visite_observateurs"] = visite_users

        sections["EquipementAlpage"] = serialize_qs(
            EquipementAlpage.objects.filter(unite_pastorale_id__in=up_ids)
        )
        sections["AbriDUrgence"] = serialize_qs(
            AbriDUrgence.objects.filter(id_abri_urgence__in=abri_ids)
        )
        sections["BeneficierDe"] = serialize_qs(
            BeneficierDe.objects.filter(exploitant_id__in=exploitant_ids)
        )
        sections["EquipementExploitant"] = serialize_qs(
            EquipementExploitant.objects.filter(
                situation_exploitation_id__in=situation_ids
            )
        )
        sections["AbriDUrgenceCommodite"] = serialize_qs(
            AbriDUrgenceCommodite.objects.filter(abri_urgence_id__in=abri_ids)
        )
        sections["SubventionPNV"] = serialize_qs(
            SubventionPNV.objects.filter(exploitant_id__in=exploitant_ids)
        )
        sections["Logement"] = serialize_qs(
            Logement.objects.filter(unite_pastorale_id__in=up_ids)
        )

        export = {
            "meta": {
                "ups": [up.code_up for up in ups],
                "up_ids": list(up_ids),
            },
            "sections": sections,
        }

        output_path = options["output"]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export, f, indent=2, ensure_ascii=False)

        total = sum(len(v) for v in sections.values())
        self.stdout.write(
            self.style.SUCCESS(
                f"\nExport terminé : {total} enregistrements dans {output_path}"
            )
        )
        for key, items in sections.items():
            if items:
                self.stdout.write(f"  {key:<35} : {len(items)}")
