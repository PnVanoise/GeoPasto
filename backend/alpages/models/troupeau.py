from django.contrib.gis.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import F, Q

from .mixins import AuditFieldsMixin


class Production(AuditFieldsMixin, models.Model):
    id_production = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)

    class Meta:
        verbose_name = "production"
        verbose_name_plural = "productions"

    def __str__(self):
        return str(self.description)


class CategoriePension(AuditFieldsMixin, models.Model):
    id_categorie_pension = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)

    class Meta:
        db_table = "alpages_categorie_pension"
        verbose_name = "catégorie de pension"
        verbose_name_plural = "catégories de pension"

    def __str__(self):
        return str(self.description)


class Espece(AuditFieldsMixin, models.Model):
    id_espece = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)

    class Meta:
        verbose_name = "espèce"
        verbose_name_plural = "espèces"

    def __str__(self):
        return str(self.description)


class Race(AuditFieldsMixin, models.Model):
    id_race = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    espece = models.ForeignKey(
        "alpages.Espece",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="races",
    )

    class Meta:
        verbose_name = "race"
        verbose_name_plural = "races"

    def __str__(self):
        return str(self.description)


class CategorieAnimaux(AuditFieldsMixin, models.Model):
    id_categorie_animaux = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    coefficient_UGB = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=False,
        blank=False,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )
    espece = models.ForeignKey(
        "alpages.Espece",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="categories_animaux",
    )

    class Meta:
        db_table = "alpages_categorie_animaux"
        verbose_name = "catégorie d'animaux"
        verbose_name_plural = "catégories d'animaux"

    def __str__(self):
        return str(self.description)


class Cheptel(AuditFieldsMixin, models.Model):
    id_cheptel = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)

    eleveur = models.ForeignKey(
        "alpages.Eleveur",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="cheptels",
    )
    situation_exploitation = models.ForeignKey(
        "alpages.SituationDExploitation",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="cheptels",
    )
    nombre_animaux = models.IntegerField(null=False, blank=False)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)

    coefficient_UGB = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=False,
        blank=False,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )
    production = models.ForeignKey(
        "alpages.Production",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="cheptels",
    )
    pension = models.ForeignKey(
        "alpages.CategoriePension",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="cheptels",
    )
    race = models.ForeignKey(
        "alpages.Race",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="cheptels",
    )
    categorie_animaux = models.ForeignKey(
        "alpages.CategorieAnimaux",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="cheptels",
    )

    class Meta:
        verbose_name = "troupeau"
        verbose_name_plural = "troupeaux"
        constraints = [
            models.CheckConstraint(
                check=Q(date_fin__isnull=True) | Q(date_debut__lte=F("date_fin")),
                name="chk_cheptel_dates_coherentes",
            ),
        ]

    def __str__(self):
        return f"{self.eleveur} élève {self.description} dans la situation {self.situation_exploitation}"
