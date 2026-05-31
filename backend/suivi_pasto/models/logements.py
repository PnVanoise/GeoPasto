from django.contrib.gis.db import models
from django.db.models import F, Q

from .mixins import AuditFieldsMixin
from ..choices_logement import (
    LST_STATUT,
    LST_ACCES_FINAL,
    LST_PROPRIETE,
    LST_TYPE_LOGEMENT,
    LST_MULTIUSAGE,
    LST_ACTIVITE_LAITIERE,
    LST_ETAT_BATIMENT,
    LST_ACCUEIL_PUBLIC,
    LST_SURFACE_LOGEMENT,
    LST_WC,
    LST_ALIM_ELECTRIQUE,
    LST_ALIM_EAU,
    LST_ORIGINE_EAU,
    LST_QUALITE_EAU,
    LST_DISPO_EAU,
    LST_ASSAINISSEMENT,
    LST_CHAUFFE_EAU,
    LST_OUI_NON,
    LST_OUI_NON_INC,
)


class Logement(AuditFieldsMixin, models.Model):
    id_logement = models.BigAutoField(primary_key=True, db_column="id")
    logement_code = models.CharField(max_length=10)
    nom_logement = models.CharField(max_length=50, null=True, blank=True)
    unite_pastorale = models.ForeignKey(
        "suivi_pasto.UnitePastorale",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="logements",
    )
    statut = models.CharField(max_length=50, choices=LST_STATUT, null=True, blank=True)
    acces_final = models.CharField(
        max_length=50, choices=LST_ACCES_FINAL, null=True, blank=True
    )
    propriete = models.CharField(
        max_length=50, choices=LST_PROPRIETE, null=True, blank=True
    )
    type_logement = models.CharField(
        max_length=50, choices=LST_TYPE_LOGEMENT, null=True, blank=True
    )
    multiusage = models.CharField(
        max_length=50, choices=LST_MULTIUSAGE, null=True, blank=True
    )
    activite_laitiere = models.CharField(
        max_length=50, choices=LST_ACTIVITE_LAITIERE, null=True, blank=True
    )
    etat_batiment = models.CharField(
        max_length=50, choices=LST_ETAT_BATIMENT, null=True, blank=True
    )
    accueil_public = models.CharField(
        max_length=50, choices=LST_ACCUEIL_PUBLIC, null=True, blank=True
    )
    mixite_possible = models.CharField(
        max_length=50, choices=LST_OUI_NON_INC, null=True, blank=True
    )
    surface_logement = models.CharField(
        max_length=50, choices=LST_SURFACE_LOGEMENT, null=True, blank=True
    )
    presence_douche = models.CharField(
        max_length=50, choices=LST_OUI_NON_INC, null=True, blank=True
    )
    type_wc = models.CharField(max_length=50, choices=LST_WC, null=True, blank=True)
    alim_elec = models.CharField(
        max_length=50, choices=LST_ALIM_ELECTRIQUE, null=True, blank=True
    )
    alim_eau = models.CharField(
        max_length=50, choices=LST_ALIM_EAU, null=True, blank=True
    )
    origine_eau = models.CharField(
        max_length=50, choices=LST_ORIGINE_EAU, null=True, blank=True
    )
    qualite_eau = models.CharField(
        max_length=50, choices=LST_QUALITE_EAU, null=True, blank=True
    )
    dispo_eau = models.CharField(
        max_length=50, choices=LST_DISPO_EAU, null=True, blank=True
    )
    assainissement = models.CharField(
        max_length=50, choices=LST_ASSAINISSEMENT, null=True, blank=True
    )
    chauffe_eau = models.CharField(
        max_length=50, choices=LST_CHAUFFE_EAU, null=True, blank=True
    )
    chauffage = models.CharField(
        max_length=50, choices=LST_OUI_NON, null=True, blank=True
    )
    stockage_indep = models.CharField(
        max_length=50, choices=LST_OUI_NON, null=True, blank=True
    )
    geom = models.PointField(srid=2154, null=True)

    class Meta:
        verbose_name = "logement"
        verbose_name_plural = "logements"


class Commodite(AuditFieldsMixin, models.Model):
    id_commodite = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=100, null=False, blank=False)

    class Meta:
        verbose_name = "commodité"
        verbose_name_plural = "commodités"

    def __str__(self):
        return str(self.description)


class AbriDUrgence(AuditFieldsMixin, models.Model):
    id_abri_urgence = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    etat = models.CharField(max_length=50, null=False, blank=False)

    class Meta:
        verbose_name = "abri d'urgence"
        verbose_name_plural = "abris d'urgence"

    def __str__(self):
        return str(self.description)


class AbriDUrgenceCommodite(AuditFieldsMixin, models.Model):
    id_abri_urgence_commodite = models.BigAutoField(primary_key=True)
    abri_urgence = models.ForeignKey(
        "suivi_pasto.AbriDUrgence",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="commodites",
    )
    commodite = models.ForeignKey(
        "suivi_pasto.Commodite",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="abris_urgence",
    )
    etat = models.CharField(max_length=50, null=False, blank=False)
    commentaire = models.CharField(max_length=50, null=True, blank=True)
    quantite = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = "abri d'urgence / commodité"
        verbose_name_plural = "abris d'urgence / commodités"

    def __str__(self):
        return f"{self.abri_urgence} a {self.quantite} de {self.commodite}"


class BeneficierDe(AuditFieldsMixin, models.Model):
    id_beneficier_de = models.BigAutoField(primary_key=True)
    exploitant = models.ForeignKey(
        "suivi_pasto.Exploitant",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="beneficiaires",
    )
    abri_urgence = models.ForeignKey(
        "suivi_pasto.AbriDUrgence",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="beneficiaires",
    )
    date_debut = models.DateField(null=False, blank=False)
    date_fin = models.DateField(null=True, blank=True)
    geometry = models.PointField(srid=2154, null=True, blank=True)

    class Meta:
        verbose_name = "bénéficier de"
        verbose_name_plural = "bénéficier de"
        constraints = [
            models.CheckConstraint(
                check=Q(date_fin__isnull=True) | Q(date_debut__lte=F("date_fin")),
                name="chk_beneficier_de_dates_coherentes",
            ),
        ]

    def __str__(self):
        return f"{self.exploitant} bénéficie de {self.abri_urgence}"
