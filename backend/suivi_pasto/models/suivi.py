from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.db.models import F, Q

from .mixins import AuditFieldsMixin


class TypeDeSuivi(AuditFieldsMixin, models.Model):
    id_type_suivi = models.AutoField(primary_key=True)
    description = models.CharField(max_length=150, null=False, blank=False)

    class Meta:
        verbose_name = "type de suivi"
        verbose_name_plural = "types de suivi"

    def __str__(self):
        return str(self.description)


class PlanDeSuivi(AuditFieldsMixin, models.Model):
    id_plan_suivi = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=150, null=False, blank=False)
    commentaire = models.TextField(null=True, blank=True)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    type_suivi = models.ForeignKey(
        "suivi_pasto.TypeDeSuivi",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="plans_de_suivi",
    )
    unite_pastorale = models.ForeignKey(
        "suivi_pasto.UnitePastorale",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="plans_de_suivi",
    )

    class Meta:
        verbose_name = "plan de suivi"
        verbose_name_plural = "plans de suivi"
        constraints = [
            models.CheckConstraint(
                check=Q(date_fin__isnull=True) | Q(date_debut__lte=F("date_fin")),
                name="chk_plan_suivi_dates_coherentes",
            ),
        ]

    def __str__(self):
        return str(self.description)


class TypeDeMesure(AuditFieldsMixin, models.Model):
    id_type_mesure = models.AutoField(primary_key=True)
    description = models.CharField(max_length=150, null=False, blank=False)

    class Meta:
        verbose_name = "type de mesure"
        verbose_name_plural = "types de mesure"

    def __str__(self):
        return str(self.description)


class Enjeu(AuditFieldsMixin, models.Model):
    id_enjeu = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=150, null=False, blank=False)

    class Meta:
        verbose_name = "enjeu"
        verbose_name_plural = "enjeux"
        ordering = ["description"]

    def __str__(self):
        return str(self.description)


class MesureDePlan(AuditFieldsMixin, models.Model):
    id_mesure_plan = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=150, null=False, blank=False)
    commentaire = models.TextField(null=True, blank=True)
    debut_periode = models.DateField(null=True, blank=True)
    fin_periode = models.DateField(null=True, blank=True)
    type_mesure = models.ForeignKey(
        "suivi_pasto.TypeDeMesure",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="mesures_de_plan",
    )
    plan_suivi = models.ForeignKey(
        "suivi_pasto.PlanDeSuivi",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="mesures_de_plan",
    )
    geometry = models.GeometryField(srid=2154, null=True, blank=True)
    obligation = models.BooleanField(default=False)
    enjeux = models.ManyToManyField(
        "suivi_pasto.Enjeu",
        blank=True,
        related_name="mesures_de_plan",
    )

    class Meta:
        verbose_name = "mesure de plan"
        verbose_name_plural = "mesures de plan"
        constraints = [
            models.CheckConstraint(
                check=Q(fin_periode__isnull=True)
                | Q(debut_periode__lte=F("fin_periode")),
                name="chk_mesure_plan_periodes_coherentes",
            ),
        ]

    def __str__(self):
        return str(self.description)


class RealisationMesure(AuditFieldsMixin, models.Model):
    STATUT_CHOICES = [
        ("non_realisee", "Non réalisée"),
        ("partielle", "Partiellement réalisée"),
        ("realisee", "Réalisée"),
    ]

    id_realisation_mesure = models.BigAutoField(primary_key=True)
    mesure_plan = models.ForeignKey(
        "suivi_pasto.MesureDePlan",
        on_delete=models.PROTECT,
        related_name="realisations",
    )
    situation = models.ForeignKey(
        "suivi_pasto.SituationDExploitation",
        on_delete=models.PROTECT,
        related_name="realisations_mesures",
    )
    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default="non_realisee"
    )
    commentaire = models.TextField(null=True, blank=True)
    date_realisation = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "réalisation de mesure"
        verbose_name_plural = "réalisations de mesures"
        unique_together = [("mesure_plan", "situation")]

    def __str__(self):
        return f"{self.mesure_plan} – {self.situation} – {self.statut}"


class TypeEvenement(AuditFieldsMixin, models.Model):
    id_type_evenement = models.AutoField(primary_key=True)
    description = models.CharField(max_length=150, null=False, blank=False)

    class Meta:
        verbose_name = "type d'événement"
        verbose_name_plural = "types d'événement"

    def __str__(self):
        return str(self.description)


class Evenement(AuditFieldsMixin, models.Model):
    id_evenement = models.BigAutoField(primary_key=True)
    date_evenement = models.DateField(null=False, blank=False)
    observateur = models.CharField(max_length=50, null=False, blank=False)
    date_observation = models.DateField(null=False, blank=False)
    source = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=150, null=False, blank=False)
    commentaire = models.TextField(null=True, blank=True)
    geometry = models.GeometryField(srid=2154, null=True, blank=True)
    situation = models.ForeignKey(
        "suivi_pasto.SituationDExploitation",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="evenements",
    )
    mesure_plan = models.ForeignKey(
        "suivi_pasto.MesureDePlan",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="evenements",
    )
    type_evenement = models.ForeignKey(
        "suivi_pasto.TypeEvenement",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="evenements",
    )

    class Meta:
        verbose_name = "événement"
        verbose_name_plural = "événements"

    def __str__(self):
        return str(self.description)


class Visite(AuditFieldsMixin, models.Model):
    id_visite = models.BigAutoField(primary_key=True)
    date_visite = models.DateField()
    description = models.CharField(max_length=150)
    commentaire = models.TextField(null=True, blank=True)
    unite_pastorale = models.ForeignKey(
        "suivi_pasto.UnitePastorale",
        on_delete=models.PROTECT,
        related_name="visites",
    )
    contacts_alpagistes = models.ManyToManyField(
        "suivi_pasto.Eleveur",
        blank=True,
        related_name="visites_contact",
    )
    observateurs = models.ManyToManyField(
        get_user_model(),
        blank=True,
        related_name="visites_observees",
    )

    class Meta:
        verbose_name = "visite"
        verbose_name_plural = "visites"
        ordering = ["-date_visite"]

    def __str__(self):
        return f"Visite {self.date_visite} – {self.unite_pastorale}"
