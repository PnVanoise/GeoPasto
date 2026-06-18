import logging

from django.contrib.gis.db import models
from django.db.models import F, Q
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from .mixins import AuditFieldsMixin

logger = logging.getLogger(__name__)


class UnitePastorale(AuditFieldsMixin, models.Model):
    """
    Unité pastorale. La géométrie active est un cache calculé depuis GeometrieUnitePastorale.
    """

    id_unite_pastorale = models.BigAutoField(primary_key=True)
    code_up = models.CharField(max_length=50, null=False, blank=False)
    nom_up = models.CharField(max_length=50, null=False, blank=False)
    geom_active = models.MultiPolygonField(srid=2154, null=True, blank=True)
    secteur = models.CharField(max_length=50, null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "unité pastorale"
        verbose_name_plural = "unités pastorales"

    def __str__(self):
        return str(self.nom_up)


class GeometrieUnitePastorale(AuditFieldsMixin, models.Model):
    """
    Historique des géométries d'une unité pastorale.
    Une seule entrée doit être valide (date_debut <= aujourd'hui <= date_fin ou date_fin nulle) à un instant donné.
    """

    id_geometrie_up = models.BigAutoField(primary_key=True)
    unite_pastorale = models.ForeignKey(
        "suivi_pasto.UnitePastorale",
        on_delete=models.PROTECT,
        related_name="geometries",
    )
    geometry = models.MultiPolygonField(srid=2154)
    date_debut_validite = models.DateField()
    date_fin_validite = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "géométrie d'unité pastorale"
        verbose_name_plural = "géométries d'unités pastorales"
        ordering = ["-date_debut_validite"]
        constraints = [
            models.CheckConstraint(
                check=Q(date_fin_validite__isnull=True)
                | Q(date_debut_validite__lte=F("date_fin_validite")),
                name="chk_geometrie_up_dates_coherentes",
            ),
        ]

    def __str__(self):
        return f"{self.unite_pastorale} — {self.date_debut_validite}"


def _refresh_geom_active(up):
    today = timezone.now().date()

    qs = (
        GeometrieUnitePastorale.objects.filter(
            unite_pastorale=up,
            date_debut_validite__lte=today,
        )
        .filter(Q(date_fin_validite__isnull=True) | Q(date_fin_validite__gte=today))
        .order_by("-date_debut_validite")
    )

    geom_entry = qs.first()
    geom_active_courante = geom_entry is not None

    if geom_entry is None:
        geom_entry = (
            GeometrieUnitePastorale.objects.filter(
                unite_pastorale=up,
                date_debut_validite__lte=today,
            )
            .order_by("-date_debut_validite")
            .first()
        )

    up.geom_active = geom_entry.geometry if geom_entry else None
    up.active = geom_active_courante
    up.save(update_fields=["geom_active", "active"])
    logger.debug(
        "UP %s (%s) — geom_active=%s active=%s",
        up.pk,
        up.nom_up,
        "set" if up.geom_active else "None",
        up.active,
    )


@receiver([post_save, post_delete], sender=GeometrieUnitePastorale)
def sync_geom_active(sender, instance, **kwargs):
    print(
        f"\n[sync_geom_active] signal reçu — GeometrieUnitePastorale id={instance.pk}, UP id={instance.unite_pastorale_id}"
    )
    _refresh_geom_active(instance.unite_pastorale)


class ProprietaireFoncier(AuditFieldsMixin, models.Model):
    id_proprietaire = models.BigAutoField(primary_key=True)
    nom_propr = models.CharField(max_length=50, null=False, blank=False)
    prenom_propr = models.CharField(max_length=50, null=True, blank=True)
    tel_propr = models.CharField(max_length=30, null=True, blank=True)
    mail_propr = models.CharField(max_length=50, null=True, blank=True)
    adresse_propr = models.CharField(max_length=100, null=True, blank=True)
    commentaire = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "propriétaire foncier"
        verbose_name_plural = "propriétaires fonciers"

    def __str__(self):
        return str(self.nom_propr)


class ProprietaireUnitePastorale(AuditFieldsMixin, models.Model):
    id_proprietaire_up = models.BigAutoField(primary_key=True, db_column="id")
    proprietaire = models.ForeignKey(
        "suivi_pasto.ProprietaireFoncier",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="unites_pastorales_proprietaire",
    )
    unite_pastorale = models.ForeignKey(
        "suivi_pasto.UnitePastorale",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="proprietaires_unite_pastorale",
    )

    class Meta:
        verbose_name = "propriétaire / unité pastorale"
        verbose_name_plural = "propriétaires / unités pastorales"

    def __str__(self):
        return f"{self.proprietaire} est propriétaire de {self.unite_pastorale}"


class QuartierPasto(AuditFieldsMixin, models.Model):
    id_quartier = models.BigAutoField(primary_key=True)
    code_quartier = models.CharField(max_length=50, null=True, blank=True)
    nom_quartier = models.CharField(max_length=50, null=True, blank=True)
    geometry = models.MultiPolygonField(srid=2154, null=True, blank=True)

    situation_exploitation = models.ForeignKey(
        "suivi_pasto.SituationDExploitation",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="quartiers",
    )

    class Meta:
        verbose_name = "quartier d'alpage"
        verbose_name_plural = "quartiers d'alpage"
        constraints = [
            models.UniqueConstraint(
                fields=["situation_exploitation", "code_quartier"],
                name="uniq_code_quartier_par_situation",
            ),
        ]

    def __str__(self):
        return str(self.nom_quartier)
