from django.contrib.gis.db import models

from .mixins import AuditFieldsMixin


class TypeDeSuivi(AuditFieldsMixin, models.Model):
    id_type_suivi = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)

    class Meta:
        verbose_name = "type de suivi"
        verbose_name_plural = "types de suivi"

    def __str__(self):
        return str(self.description)


class PlanDeSuivi(AuditFieldsMixin, models.Model):
    id_plan_suivi = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    type_suivi = models.ForeignKey(
        "alpages.TypeDeSuivi",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="plans_de_suivi",
    )
    unite_pastorale = models.ForeignKey(
        "alpages.UnitePastorale",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="plans_de_suivi",
    )

    class Meta:
        verbose_name = "plan de suivi"
        verbose_name_plural = "plans de suivi"

    def __str__(self):
        return str(self.description)


class TypeDeMesure(AuditFieldsMixin, models.Model):
    id_type_mesure = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)

    class Meta:
        verbose_name = "type de mesure"
        verbose_name_plural = "types de mesure"

    def __str__(self):
        return str(self.description)


class MesureDePlan(AuditFieldsMixin, models.Model):
    id_mesure_plan = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    commentaire = models.CharField(max_length=50, null=True, blank=True)
    debut_periode = models.DateField(null=True, blank=True)
    fin_periode = models.DateField(null=True, blank=True)
    type_mesure = models.ForeignKey(
        "alpages.TypeDeMesure",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="mesures_de_plan",
    )
    plan_suivi = models.ForeignKey(
        "alpages.PlanDeSuivi",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="mesures_de_plan",
    )
    geometry = models.GeometryField(srid=2154, null=True, blank=True)

    class Meta:
        verbose_name = "mesure de plan"
        verbose_name_plural = "mesures de plan"

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
        "alpages.MesureDePlan",
        on_delete=models.PROTECT,
        related_name="realisations",
    )
    situation = models.ForeignKey(
        "alpages.SituationDExploitation",
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
    description = models.CharField(max_length=50, null=False, blank=False)

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
    description = models.CharField(max_length=500, null=True, blank=True)
    geometry = models.GeometryField(srid=2154, null=True, blank=True)
    situation = models.ForeignKey(
        "alpages.SituationDExploitation",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="evenements",
    )
    mesure_plan = models.ForeignKey(
        "alpages.MesureDePlan",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="evenements",
    )
    type_evenement = models.ForeignKey(
        "alpages.TypeEvenement",
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
