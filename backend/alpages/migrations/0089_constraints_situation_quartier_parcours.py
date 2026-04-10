from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Count, F, Q


def validate_before_hardening(apps, schema_editor):
    Situation = apps.get_model("alpages", "SituationDExploitation")
    Quartier = apps.get_model("alpages", "QuartierPasto")
    Exploiter = apps.get_model("alpages", "Exploiter")

    # Backfill opportuniste: si un quartier n'a pas de situation, on essaie
    # de la déduire via les parcours existants (quartier -> exploiter -> cheptel -> situation).
    for q in Quartier.objects.filter(situation_exploitation__isnull=True).iterator():
        candidate_ids = list(
            Exploiter.objects.filter(
                quartier_id=q.pk,
                cheptel__situation_exploitation__isnull=False,
            )
            .values_list("cheptel__situation_exploitation_id", flat=True)
            .distinct()
        )
        if len(candidate_ids) == 1:
            q.situation_exploitation_id = candidate_ids[0]
            q.save(update_fields=["situation_exploitation"])

    ambiguous_quartiers = []
    for q in Quartier.objects.filter(situation_exploitation__isnull=True).iterator():
        candidate_ids = list(
            Exploiter.objects.filter(
                quartier_id=q.pk,
                cheptel__situation_exploitation__isnull=False,
            )
            .values_list("cheptel__situation_exploitation_id", flat=True)
            .distinct()
        )
        if len(candidate_ids) > 1:
            ambiguous_quartiers.append(q.pk)
        if len(ambiguous_quartiers) >= 20:
            break

    if ambiguous_quartiers:
        raise RuntimeError(
            "Quartiers avec situations ambiguës (plusieurs situations candidates via les parcours). "
            "Exemples id_quartier: "
            + ", ".join(map(str, ambiguous_quartiers))
        )

    missing_annee = list(
        Situation.objects.filter(annee__isnull=True).values_list("id_situation", flat=True)[:20]
    )
    if missing_annee:
        raise RuntimeError(
            "Situations sans annee. Exemples id_situation: " + ", ".join(map(str, missing_annee))
        )

    dup_situation = (
        Situation.objects.filter(unite_pastorale__isnull=False)
        .values("unite_pastorale_id", "annee")
        .annotate(c=Count("id_situation"))
        .filter(c__gt=1)
    )
    if dup_situation.exists():
        ex = dup_situation.first()
        raise RuntimeError(
            "Doublon (unite_pastorale, annee) avant contrainte uniq_situation_up_annee: "
            f"up={ex['unite_pastorale_id']}, annee={ex['annee']}"
        )

    # Des quartiers historiques peuvent rester orphelins tant que le champ
    # situation_exploitation est nullable. On ne bloque pas la migration ici.

    missing_parcours = list(
        Exploiter.objects.filter(
            Q(quartier__isnull=True) | Q(cheptel__isnull=True) | Q(date_debut__isnull=True)
        ).values_list("id_exploiter", flat=True)[:20]
    )
    if missing_parcours:
        raise RuntimeError(
            "Parcours incomplets avant contraintes. Exemples id_exploiter: "
            + ", ".join(map(str, missing_parcours))
        )

    bad_coherence = list(
        Exploiter.objects.exclude(
            cheptel__situation_exploitation=F("quartier__situation_exploitation")
        ).values_list("id_exploiter", flat=True)[:20]
    )
    if bad_coherence:
        raise RuntimeError(
            "Parcours incohérents (cheptel.situation != quartier.situation). Exemples id_exploiter: "
            + ", ".join(map(str, bad_coherence))
        )

    dup_parcours = (
        Exploiter.objects.values("cheptel_id", "quartier_id", "date_debut")
        .annotate(c=Count("id_exploiter"))
        .filter(c__gt=1)
    )
    if dup_parcours.exists():
        ex = dup_parcours.first()
        raise RuntimeError(
            "Doublon parcours avant contrainte uniq_parcours_cheptel_quartier_debut: "
            f"cheptel={ex['cheptel_id']}, quartier={ex['quartier_id']}, date_debut={ex['date_debut']}"
        )


class Migration(migrations.Migration):

    dependencies = [
        ("alpages", "0088_backfill_annee_et_parcours"),
    ]

    operations = [
        migrations.RunPython(validate_before_hardening, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="quartierpasto",
            name="situation_exploitation",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="quartiers",
                to="alpages.situationdexploitation",
            ),
        ),
        migrations.AlterField(
            model_name="exploiter",
            name="quartier",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="parcours",
                to="alpages.quartierpasto",
            ),
        ),
        migrations.AlterField(
            model_name="exploiter",
            name="cheptel",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="parcours",
                to="alpages.cheptel",
            ),
        ),
        migrations.AlterField(
            model_name="exploiter",
            name="date_debut",
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name="exploiter",
            name="date_fin",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="situationdexploitation",
            name="annee",
            field=models.PositiveSmallIntegerField(),
        ),
    ]
