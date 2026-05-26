from django.contrib.gis.db import models

from .mixins import AuditFieldsMixin


class Eleveur(AuditFieldsMixin, models.Model):
    id_eleveur = models.AutoField(primary_key=True)
    nom_eleveur = models.CharField(max_length=50, null=False, blank=False)
    prenom_eleveur = models.CharField(max_length=50, null=True, blank=True)
    tel_eleveur = models.CharField(max_length=50, null=True, blank=True)
    mail_eleveur = models.CharField(max_length=50, null=True, blank=True)
    adresse_eleveur = models.CharField(max_length=50, null=True, blank=True)
    commentaire = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        verbose_name = "éleveur"
        verbose_name_plural = "éleveurs"

    def __str__(self):
        return str(self.nom_eleveur)


class TypeDExploitant(AuditFieldsMixin, models.Model):
    id_type_exploitant = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)

    class Meta:
        verbose_name = "type d'exploitant"
        verbose_name_plural = "types d'exploitant"

    def __str__(self):
        return str(self.description)


class Exploitant(AuditFieldsMixin, models.Model):
    id_exploitant = models.AutoField(primary_key=True)
    nom_exploitant = models.CharField(max_length=50, null=False, blank=False)
    type_exploitant = models.ForeignKey(
        "alpages.TypeDExploitant",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="exploitants",
    )
    president = models.ForeignKey(
        "alpages.Eleveur",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="exploitants",
    )

    class Meta:
        verbose_name = "exploitant"
        verbose_name_plural = "exploitants"

    def __str__(self):
        return str(self.nom_exploitant)


class EtreCompose(AuditFieldsMixin, models.Model):
    id_etre_compose = models.BigAutoField(primary_key=True, db_column="id")
    exploitant = models.ForeignKey(
        Exploitant,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    eleveur = models.ForeignKey(
        Eleveur,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    class Meta:
        unique_together = ("exploitant", "eleveur")
        verbose_name = "composition d'exploitant"
        verbose_name_plural = "compositions d'exploitant"

    def __str__(self):
        return f"{self.eleveur} est membre de {self.exploitant}"


class Berger(AuditFieldsMixin, models.Model):
    id_berger = models.BigAutoField(primary_key=True)
    nom_berger = models.CharField(max_length=50, null=False, blank=False)
    prenom_berger = models.CharField(max_length=50, null=False, blank=False)
    tel_berger = models.CharField(max_length=50, null=True, blank=True)
    adresse_berger = models.CharField(max_length=50, null=True, blank=True)
    commentaire = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        verbose_name = "berger"
        verbose_name_plural = "bergers"

    def __str__(self):
        return str(self.nom_berger)
