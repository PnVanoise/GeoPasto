from django.contrib.gis.db import models

from .mixins import AuditFieldsMixin


class Eleveur(AuditFieldsMixin, models.Model):
    id_eleveur = models.AutoField(primary_key=True)
    nom_eleveur = models.CharField(max_length=50, null=False, blank=False)
    prenom_eleveur = models.CharField(max_length=50, null=True, blank=True)
    tel_eleveur = models.CharField(max_length=50, null=True, blank=True)
    mail_eleveur = models.CharField(max_length=50, null=True, blank=True)
    adresse_eleveur = models.CharField(max_length=50, null=True, blank=True)
    commentaire = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "éleveur"
        verbose_name_plural = "éleveurs"

    def __str__(self):
        return str(self.nom_eleveur)


class TypeDExploitant(AuditFieldsMixin, models.Model):
    id_type_exploitant = models.AutoField(primary_key=True)
    description = models.CharField(max_length=150, null=False, blank=False)

    class Meta:
        verbose_name = "type d'exploitant"
        verbose_name_plural = "types d'exploitant"

    def __str__(self):
        return str(self.description)


class Exploitant(AuditFieldsMixin, models.Model):
    id_exploitant = models.AutoField(primary_key=True)
    nom_exploitant = models.CharField(max_length=50, null=False, blank=False)
    type_exploitant = models.ForeignKey(
        "suivi_pasto.TypeDExploitant",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="exploitants",
    )
    president = models.ForeignKey(
        "suivi_pasto.Eleveur",
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
        related_name="compositions",
    )
    eleveur = models.ForeignKey(
        Eleveur,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    exploitant_membre = models.ForeignKey(
        Exploitant,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="memberships",
        db_column="id_exploitant_membre",
    )

    class Meta:
        verbose_name = "composition d'exploitant"
        verbose_name_plural = "compositions d'exploitant"
        constraints = [
            models.UniqueConstraint(
                fields=["exploitant", "eleveur"],
                condition=models.Q(eleveur__isnull=False),
                name="uq_etrecompose_exploitant_eleveur",
            ),
            models.UniqueConstraint(
                fields=["exploitant", "exploitant_membre"],
                condition=models.Q(exploitant_membre__isnull=False),
                name="uq_etrecompose_exploitant_exploitant_membre",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(eleveur__isnull=False, exploitant_membre__isnull=True)
                    | models.Q(eleveur__isnull=True, exploitant_membre__isnull=False)
                ),
                name="chk_etrecompose_exactement_un_membre",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(exploitant_membre__isnull=True)
                    | ~models.Q(exploitant_membre=models.F("exploitant"))
                ),
                name="chk_etrecompose_pas_autoreference",
            ),
        ]

    def __str__(self):
        membre = self.eleveur if self.eleveur_id else self.exploitant_membre
        return f"{membre} est membre de {self.exploitant}"


class Berger(AuditFieldsMixin, models.Model):
    id_berger = models.BigAutoField(primary_key=True)
    nom_berger = models.CharField(max_length=50, null=False, blank=False)
    prenom_berger = models.CharField(max_length=50, null=False, blank=False)
    tel_berger = models.CharField(max_length=50, null=True, blank=True)
    adresse_berger = models.CharField(max_length=50, null=True, blank=True)
    commentaire = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "berger"
        verbose_name_plural = "bergers"

    def __str__(self):
        return str(self.nom_berger)
