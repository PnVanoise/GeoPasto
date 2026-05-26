from django.contrib.gis.db import models

from .mixins import AuditFieldsMixin


class TypeEquipement(AuditFieldsMixin, models.Model):
    id_type_equipement = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    categorie = models.CharField(max_length=50, null=False, blank=False)

    class Meta:
        verbose_name = "type d'équipement"
        verbose_name_plural = "types d'équipement"

    def __str__(self):
        return str(self.description)


class EquipementAlpage(AuditFieldsMixin, models.Model):
    id_equipement_alpage = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    etat = models.CharField(max_length=50, null=False, blank=False)
    geometry = models.GeometryField(srid=2154, null=True, blank=True)
    type_equipement = models.ForeignKey(
        "alpages.TypeEquipement",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="eqptsAlpage",
    )
    unite_pastorale = models.ForeignKey(
        "alpages.UnitePastorale",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="eqptsAlpage",
    )

    class Meta:
        verbose_name = "équipement d'alpage"
        verbose_name_plural = "équipements d'alpage"


class EquipementExploitant(AuditFieldsMixin, models.Model):
    id_equipement_exploitant = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=150, null=False, blank=False)
    etat = models.CharField(max_length=50, null=False, blank=False)
    geometry = models.GeometryField(srid=2154, null=True, blank=True)
    type_equipement = models.ForeignKey(
        "alpages.TypeEquipement",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="eqptsExploitant",
    )
    situation_exploitation = models.ForeignKey(
        "alpages.SituationDExploitation",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="eqptsExploitant",
    )
    beneficier_de = models.ForeignKey(
        "alpages.BeneficierDe",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="equipement",
    )

    class Meta:
        verbose_name = "équipement d'exploitant"
        verbose_name_plural = "équipements d'exploitant"
