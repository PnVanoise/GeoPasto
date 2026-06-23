from django.contrib.gis.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import F, Q

from .mixins import AuditFieldsMixin


class Production(AuditFieldsMixin, models.Model):
    id_production = models.AutoField(primary_key=True)
    description = models.CharField(max_length=150, null=False, blank=False)

    class Meta:
        verbose_name = "production"
        verbose_name_plural = "productions"

    def __str__(self):
        return str(self.description)


class CategoriePension(AuditFieldsMixin, models.Model):
    id_categorie_pension = models.AutoField(primary_key=True)
    description = models.CharField(max_length=150, null=False, blank=False)

    class Meta:
        verbose_name = "catégorie de pension"
        verbose_name_plural = "catégories de pension"

    def __str__(self):
        return str(self.description)


class Espece(AuditFieldsMixin, models.Model):
    id_espece = models.AutoField(primary_key=True)
    description = models.CharField(max_length=150, null=False, blank=False)

    class Meta:
        verbose_name = "espèce"
        verbose_name_plural = "espèces"

    def __str__(self):
        return str(self.description)


class Race(AuditFieldsMixin, models.Model):
    id_race = models.AutoField(primary_key=True)
    description = models.CharField(max_length=150, null=False, blank=False)
    espece = models.ForeignKey(
        "suivi_pasto.Espece",
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
    description = models.CharField(max_length=150, null=False, blank=False)
    coefficient_UGB = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=False,
        blank=False,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )
    espece = models.ForeignKey(
        "suivi_pasto.Espece",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="categories_animaux",
    )

    class Meta:
        verbose_name = "catégorie d'animaux"
        verbose_name_plural = "catégories d'animaux"

    def __str__(self):
        return str(self.description)


class Cheptel(AuditFieldsMixin, models.Model):
    id_cheptel = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=150, null=False, blank=False)
    commentaire = models.TextField(null=True, blank=True)

    eleveur = models.ForeignKey(
        "suivi_pasto.Eleveur",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="cheptels",
    )
    exploitant_proprietaire = models.ForeignKey(
        "suivi_pasto.Exploitant",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="cheptels_proprietaire",
        db_column="id_exploitant_proprietaire",
    )
    situation_exploitation = models.ForeignKey(
        "suivi_pasto.SituationDExploitation",
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
        "suivi_pasto.Production",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="cheptels",
    )
    pension = models.ForeignKey(
        "suivi_pasto.CategoriePension",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="cheptels",
    )
    race = models.ForeignKey(
        "suivi_pasto.Race",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="cheptels",
    )
    categorie_animaux = models.ForeignKey(
        "suivi_pasto.CategorieAnimaux",
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
            models.CheckConstraint(
                check=(
                    Q(eleveur__isnull=False, exploitant_proprietaire__isnull=True)
                    | Q(eleveur__isnull=True, exploitant_proprietaire__isnull=False)
                    | Q(eleveur__isnull=True, exploitant_proprietaire__isnull=True)
                ),
                name="chk_cheptel_proprietaire_unique",
            ),
        ]

    def __str__(self):
        proprietaire = self.eleveur or self.exploitant_proprietaire
        return f"{proprietaire} élève {self.description} dans la situation {self.situation_exploitation}"
