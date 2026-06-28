import json
import logging
from calendar import monthrange
from datetime import date

from django.db import connection, transaction
from django.db.models import Q
from django.utils import timezone

from django.contrib.gis.geos import MultiPolygon, Polygon as GEOSPolygon
from django.contrib.gis.db.models import Union
from django.contrib.gis.db.models.functions import Transform, MakeValid, SnapToGrid

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, action

from .pagination import DefaultPagination
from .viewsets_base import BaseModelViewSet

from suivi_pasto.models import Logement, Commodite
from suivi_pasto.models import (
    UnitePastorale,
    GeometrieUnitePastorale,
    ProprietaireFoncier,
    QuartierPasto,
    ProprietaireUnitePastorale,
    _refresh_geom_active,
)
from suivi_pasto.models import (
    TypeDeSuivi,
    PlanDeSuivi,
    TypeDeMesure,
    Enjeu,
    MesureDePlan,
    RealisationMesure,
)
from suivi_pasto.models import (
    TypeConvention,
    ConventionDExploitation,
    Eleveur,
    TypeDExploitant,
    Exploitant,
    EtreCompose,
    SubventionPNV,
    AbriDUrgence,
    AbriDUrgenceCommodite,
    BeneficierDe,
)
from suivi_pasto.models import SituationDExploitation, Exploiter

from suivi_pasto.models import (
    Cheptel,
    Production,
    CategoriePension,
    Espece,
    Race,
    CategorieAnimaux,
)
from suivi_pasto.serializers import (
    CheptelSerializer,
    ProductionSerializer,
    CategoriePensionSerializer,
    EspeceSerializer,
    RaceSerializer,
    CategorieAnimauxSerializer,
)

from suivi_pasto.models import Ruche, Berger, GardeSituation
from suivi_pasto.serializers import (
    RucheSerializer,
    BergerSerializer,
    GardeSituationSerializer,
)

from suivi_pasto.models import TypeEvenement, Evenement
from suivi_pasto.serializers import TypeEvenementSerializer, EvenementSerializer

from suivi_pasto.serializers import LogementSerializer, CommoditeSerializer
from suivi_pasto.serializers import (
    UnitePastoraleSerializer,
    UnitePastoraleLSerializer,
    GeometrieUnitePastoraleSerializer,
    ProprietaireFoncierSerializer,
    QuartierPastoSerializer,
    ProprietaireUnitePastoraleSerializer,
)
from suivi_pasto.serializers import (
    TypeDeSuiviSerializer,
    PlanDeSuiviSerializer,
    TypeDeMesureSerializer,
    EnjeuSerializer,
    MesureDePlanSerializer,
    RealisationMesureSerializer,
)
from suivi_pasto.serializers import (
    TypeConventionSerializer,
    ConventionDExploitationSerializer,
    EleveurSerializer,
    TypeDExploitantSerializer,
    ExploitantSerializer,
    EtreComposeSerializer,
    SubventionPNVSerializer,
    AbriDUrgenceSerializer,
    AbriDUrgenceCommoditeSerializer,
    BeneficierDeSerializer,
)
from suivi_pasto.serializers import (
    SituationDExploitationSerializer,
    ExploiterSerializer,
)

from suivi_pasto.models import TypeEquipement, EquipementExploitant, EquipementAlpage
from suivi_pasto.serializers import (
    TypeEquipementSerializer,
    EquipementExploitantSerializer,
    EquipementAlpageSerializer,
)

from suivi_pasto.models import Visite
from suivi_pasto.serializers import VisiteSerializer


from .choices_logement import (
    LST_STATUT,
    LST_ACCES_FINAL,
    LST_PROPRIETE,
    LST_TYPE_LOGEMENT,
    LST_MULTIUSAGE,
    LST_ACCUEIL_PUBLIC,
    LST_ACTIVITE_LAITIERE,
    LST_ETAT_BATIMENT,
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

logger = logging.getLogger(__name__)


@api_view(["GET"])
def get_choices_logement(request):
    data = {
        "statut": [
            {"value": value, "display": display} for value, display in LST_STATUT
        ],
        "acces_final": [
            {"value": value, "display": display} for value, display in LST_ACCES_FINAL
        ],
        "propriete": [
            {"value": value, "display": display} for value, display in LST_PROPRIETE
        ],
        "type_logement": [
            {"value": value, "display": display} for value, display in LST_TYPE_LOGEMENT
        ],
        "multiusage": [
            {"value": value, "display": display} for value, display in LST_MULTIUSAGE
        ],
        "accueil_public": [
            {"value": value, "display": display}
            for value, display in LST_ACCUEIL_PUBLIC
        ],
        "activite_laitiere": [
            {"value": value, "display": display}
            for value, display in LST_ACTIVITE_LAITIERE
        ],
        "etat_batiment": [
            {"value": value, "display": display} for value, display in LST_ETAT_BATIMENT
        ],
        "mixite_possible": [
            {"value": value, "display": display} for value, display in LST_OUI_NON_INC
        ],
        "surface_logement": [
            {"value": value, "display": display}
            for value, display in LST_SURFACE_LOGEMENT
        ],
        "presence_douche": [
            {"value": value, "display": display} for value, display in LST_OUI_NON_INC
        ],
        "type_wc": [{"value": value, "display": display} for value, display in LST_WC],
        "alim_elec": [
            {"value": value, "display": display}
            for value, display in LST_ALIM_ELECTRIQUE
        ],
        "alim_eau": [
            {"value": value, "display": display} for value, display in LST_ALIM_EAU
        ],
        "origine_eau": [
            {"value": value, "display": display} for value, display in LST_ORIGINE_EAU
        ],
        "qualite_eau": [
            {"value": value, "display": display} for value, display in LST_QUALITE_EAU
        ],
        "dispo_eau": [
            {"value": value, "display": display} for value, display in LST_DISPO_EAU
        ],
        "assainissement": [
            {"value": value, "display": display}
            for value, display in LST_ASSAINISSEMENT
        ],
        "chauffe_eau": [
            {"value": value, "display": display} for value, display in LST_CHAUFFE_EAU
        ],
        "chauffage": [
            {"value": value, "display": display} for value, display in LST_OUI_NON
        ],
        "stockage_indep": [
            {"value": value, "display": display} for value, display in LST_OUI_NON
        ],
    }
    return Response(data)


# Bloc administratif (orange)
class UnitePastoraleViewset(BaseModelViewSet):
    serializer_class = UnitePastoraleSerializer

    def get_queryset(self):
        queryset = (
            UnitePastorale.objects.prefetch_related("proprietaires_unite_pastorale")
            .annotate(geom_4326=Transform("geom_active", 4326))
            .order_by("nom_up")
        )

        nom_up_filter = self.request.GET.get("nom_up")
        if nom_up_filter is not None:
            queryset = queryset.filter(nom_up=nom_up_filter)

        return queryset

    # /unitePastorale/light/ → Serializer Light
    @action(detail=False, methods=["get"], url_path="light")
    def list_light(self, request):
        queryset = self.get_queryset()
        # Use the light serializer for this endpoint; enable pagination when
        # `page` param is present.
        self.pagination_class = DefaultPagination
        return self.conditional_list(
            request, serializer_class=UnitePastoraleLSerializer
        )

    # /unitePastorale/{id}/historique/ → journal auditlog (UP + géométries + propriétaires)
    @action(detail=True, methods=["get"], url_path="historique")
    def historique(self, request, pk=None):
        from auditlog.models import LogEntry
        from django.contrib.contenttypes.models import ContentType

        instance = self.get_object()

        _ACTION_LABELS = {
            LogEntry.Action.CREATE: "Création",
            LogEntry.Action.UPDATE: "Modification",
            LogEntry.Action.DELETE: "Suppression",
            LogEntry.Action.ACCESS: "Accès",
        }

        _WKT_PREFIXES = (
            "POINT",
            "MULTIPOINT",
            "LINESTRING",
            "MULTILINESTRING",
            "POLYGON",
            "MULTIPOLYGON",
            "GEOMETRYCOLLECTION",
            "SRID=",
        )

        def _mask_wkt(val):
            if isinstance(val, str) and val.upper().startswith(_WKT_PREFIXES):
                return "(géométrie)"
            return val

        def _serialize(entry, model_key, strip_fields=None, replace_fields=None):
            changes = {
                k: [_mask_wkt(v) for v in vals]
                for k, vals in entry.changes_dict.items()
            }
            if strip_fields:
                changes = {k: v for k, v in changes.items() if k not in strip_fields}
            if replace_fields:
                for field, mapping in replace_fields.items():
                    if field in changes:
                        changes[field] = [mapping.get(v, v) for v in changes[field]]
            return {
                "timestamp": entry.timestamp.isoformat(),
                "actor": entry.actor.get_username() if entry.actor else None,
                "action": _ACTION_LABELS.get(entry.action, str(entry.action)),
                "changes": changes,
                "model": model_key,
            }

        def _linked_log_entries(ct, current_pks, fk_field_name):
            """Entrées pour les objets existants + supprimés liés à cette UP."""
            pk_strs = [str(p) for p in current_pks]
            up_pk_str = str(instance.pk)
            existing = LogEntry.objects.filter(
                content_type=ct, object_pk__in=pk_strs
            ).select_related("actor")
            deleted = [
                e
                for e in LogEntry.objects.filter(
                    content_type=ct,
                    action=LogEntry.Action.DELETE,
                )
                .exclude(object_pk__in=pk_strs)
                .select_related("actor")
                if str(e.changes_dict.get(fk_field_name, [None])[0]) == up_pk_str
            ]
            return list(existing) + deleted

        all_entries = []

        # --- UP ---
        ct_up = ContentType.objects.get_for_model(UnitePastorale)
        for e in LogEntry.objects.filter(
            content_type=ct_up, object_pk=str(instance.pk)
        ).select_related("actor"):
            all_entries.append((e.timestamp, _serialize(e, "unitepastorale")))

        # --- GeometrieUnitePastorale ---
        ct_geom = ContentType.objects.get_for_model(GeometrieUnitePastorale)
        geom_pks = list(
            GeometrieUnitePastorale.objects.filter(
                unite_pastorale=instance
            ).values_list("pk", flat=True)
        )
        for e in _linked_log_entries(ct_geom, geom_pks, "unite_pastorale"):
            row = _serialize(
                e,
                "geometrieunitepastorale",
                strip_fields={"geom_active", "unite_pastorale"},
            )
            all_entries.append((e.timestamp, row))

        # --- ProprietaireUnitePastorale ---
        ct_proprio = ContentType.objects.get_for_model(ProprietaireUnitePastorale)
        proprio_pks = list(
            ProprietaireUnitePastorale.objects.filter(
                unite_pastorale=instance
            ).values_list("pk", flat=True)
        )
        # Table de résolution pk → "Nom Prénom"
        proprio_names = {
            str(p.pk): f"{p.nom_propr} {p.prenom_propr or ''}".strip()
            for p in ProprietaireFoncier.objects.all()
        }
        for e in _linked_log_entries(ct_proprio, proprio_pks, "unite_pastorale"):
            row = _serialize(
                e,
                "proprietaireunitepastorale",
                strip_fields={"unite_pastorale"},
                replace_fields={"proprietaire": proprio_names},
            )
            all_entries.append((e.timestamp, row))

        all_entries.sort(key=lambda x: x[0], reverse=True)
        return Response([row for _, row in all_entries[:200]])


class GeometrieUnitePastoraleViewset(BaseModelViewSet):
    serializer_class = GeometrieUnitePastoraleSerializer

    def get_queryset(self):
        queryset = GeometrieUnitePastorale.objects.all()
        id_up = self.request.GET.get("unite_pastorale")
        if id_up is not None:
            queryset = queryset.filter(unite_pastorale_id=id_up)
        return queryset

    @transaction.atomic
    def perform_destroy(self, instance):
        from auditlog.context import set_actor

        with set_actor(self._get_auditlog_actor()):
            up = instance.unite_pastorale
            instance.delete()
            _refresh_geom_active(up)


class ProprietaireFoncierViewset(BaseModelViewSet):
    serializer_class = ProprietaireFoncierSerializer

    def get_queryset(self):
        queryset = ProprietaireFoncier.objects.all().order_by("id_proprietaire")
        return queryset


class TypeDeMesureViewset(BaseModelViewSet):
    serializer_class = TypeDeMesureSerializer

    def get_queryset(self):
        queryset = TypeDeMesure.objects.all().order_by("id_type_mesure")
        return queryset


class EnjeuViewset(BaseModelViewSet):
    serializer_class = EnjeuSerializer

    def get_queryset(self):
        return Enjeu.objects.all().order_by("description")


class MesureDePlanViewset(BaseModelViewSet):
    serializer_class = MesureDePlanSerializer

    def get_queryset(self):
        queryset = (
            MesureDePlan.objects.all()
            .select_related("type_mesure")
            .select_related("plan_suivi__unite_pastorale")
            .prefetch_related("enjeux")
            .order_by("id_mesure_plan")
        )
        plan_suivi = self.request.GET.get("plan_suivi")
        if plan_suivi is not None:
            queryset = queryset.filter(plan_suivi_id=plan_suivi)
        unite_pastorale = self.request.GET.get("unite_pastorale")
        if unite_pastorale is not None:
            queryset = queryset.filter(plan_suivi__unite_pastorale_id=unite_pastorale)
        situation_id = self.request.GET.get("situation")
        if situation_id is not None:
            try:
                situ = SituationDExploitation.objects.get(pk=situation_id)
                if situ.date_fin:
                    queryset = queryset.filter(
                        Q(date_debut_validite__isnull=True)
                        | Q(date_debut_validite__lte=situ.date_fin)
                    )
                if situ.date_debut:
                    queryset = queryset.filter(
                        Q(date_fin_validite__isnull=True)
                        | Q(date_fin_validite__gte=situ.date_debut)
                    )
            except SituationDExploitation.DoesNotExist:
                pass
        return queryset


class RealisationMesureViewset(BaseModelViewSet):
    serializer_class = RealisationMesureSerializer

    def get_queryset(self):
        queryset = (
            RealisationMesure.objects.all()
            .select_related("mesure_plan", "situation")
            .order_by("id_realisation_mesure")
        )
        mesure_plan = self.request.GET.get("mesure_plan")
        if mesure_plan is not None:
            queryset = queryset.filter(mesure_plan_id=mesure_plan)
        situation = self.request.GET.get("situation")
        if situation is not None:
            queryset = queryset.filter(situation_id=situation)
        plan_suivi = self.request.GET.get("plan_suivi")
        if plan_suivi is not None:
            queryset = queryset.filter(mesure_plan__plan_suivi_id=plan_suivi)
        return queryset


# Bloc exploitation
class TypeConventionViewset(BaseModelViewSet):
    serializer_class = TypeConventionSerializer

    def get_queryset(self):
        queryset = TypeConvention.objects.all().order_by("id_type_convention")
        return queryset


class ConventionDExploitationViewset(BaseModelViewSet):
    serializer_class = ConventionDExploitationSerializer

    def get_queryset(self):
        queryset = (
            ConventionDExploitation.objects.all()
            .select_related("type_convention")
            .order_by("id_convention")
        )
        up_id = self.request.GET.get("unite_pastorale")
        if up_id is not None:
            queryset = queryset.filter(unite_pastorale_id=up_id)
        return queryset


class SituationDExploitationViewset(BaseModelViewSet):
    serializer_class = SituationDExploitationSerializer

    def get_queryset(self):
        queryset = SituationDExploitation.objects.all().order_by("id_situation")

        id_up_filter = self.request.GET.get("id_up")
        if id_up_filter is not None:
            queryset = queryset.filter(unite_pastorale_id=id_up_filter)
        return queryset

    @staticmethod
    def _remove_small_holes(geom, area_threshold=1.0):
        """Supprime les trous (anneaux intérieurs) dont la surface est < area_threshold m²."""

        def clean_polygon(poly):
            if poly.num_interior_rings == 0:
                return poly
            kept = [
                poly[i + 1]
                for i in range(poly.num_interior_rings)
                if GEOSPolygon(poly[i + 1]).area >= area_threshold
            ]
            return GEOSPolygon(poly[0], *kept, srid=poly.srid)

        if geom.geom_type == "Polygon":
            return clean_polygon(geom)
        if geom.geom_type == "MultiPolygon":
            return MultiPolygon(*[clean_polygon(p) for p in geom], srid=geom.srid)
        return geom

    def _ensure_multipolygon(self, geometry):
        """Force une géométrie en MultiPolygon (SRID 2154)."""
        if geometry is None or geometry.empty:
            return None

        if geometry.srid != 2154:
            geometry.transform(2154)

        if geometry.geom_type == "Polygon":
            return MultiPolygon(geometry, srid=2154)

        return geometry

    def _replace_year_safe(self, value, new_year):
        """Replace year while preserving month/day, clamping invalid month-end dates."""
        if value is None:
            return None

        max_day = monthrange(new_year, value.month)[1]
        return value.replace(year=new_year, day=min(value.day, max_day))

    @action(detail=True, methods=["post"], url_path="mettre-a-jour-geometrie")
    def mettre_a_jour_geometrie(self, request, pk=None):
        with transaction.atomic():
            situation = (
                SituationDExploitation.objects.select_for_update().filter(pk=pk).first()
            )
            if situation is None:
                return Response(
                    {"detail": "Situation introuvable."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            old_up = situation.unite_pastorale
            if old_up is None:
                return Response(
                    {"detail": "La situation n'est rattachée à aucune UP."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            quartier_qs = QuartierPasto.objects.filter(
                situation_exploitation=situation,
                geometry__isnull=False,
            )

            if not quartier_qs.exists():
                return Response(
                    {
                        "detail": "Aucune géométrie de quartier disponible pour cette situation."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # UNION EN BASE (PostGIS)
            agg = quartier_qs.aggregate(
                geom=Union(MakeValid(SnapToGrid(Transform("geometry", 2154), 0.01)))
            )

            union_geometry = agg["geom"]

            if union_geometry:
                union_geometry = union_geometry.buffer(0)
                union_geometry.srid = 2154
                union_geometry = self._remove_small_holes(
                    union_geometry, area_threshold=1.0
                )

            if union_geometry is None or union_geometry.empty:
                return Response(
                    {
                        "detail": "L'union des quartiers ne produit pas de géométrie exploitable."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            union_multipolygon = self._ensure_multipolygon(union_geometry)
            if union_multipolygon is None:
                return Response(
                    {"detail": "Impossible de générer un MultiPolygon valide."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            default_debut = situation.date_debut or date.today()
            debut_str = request.data.get("date_debut_validite")
            fin_str = request.data.get("date_fin_validite")
            fermer = request.data.get("fermer_geometrie_en_cours", True)

            try:
                debut = date.fromisoformat(debut_str) if debut_str else default_debut
            except ValueError:
                return Response(
                    {
                        "detail": "Format de date de début invalide (attendu AAAA-MM-JJ)."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            fin = None
            if fin_str:
                try:
                    fin = date.fromisoformat(fin_str)
                except ValueError:
                    return Response(
                        {
                            "detail": "Format de date de fin invalide (attendu AAAA-MM-JJ)."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if fin < debut:
                    return Response(
                        {
                            "detail": "La date de fin doit être postérieure ou égale à la date de début."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if fermer:
                GeometrieUnitePastorale.objects.filter(
                    unite_pastorale=old_up,
                    date_fin_validite__isnull=True,
                ).update(date_fin_validite=debut - timezone.timedelta(days=1))

            new_geom = GeometrieUnitePastorale.objects.create(
                unite_pastorale=old_up,
                geometry=union_multipolygon,
                date_debut_validite=debut,
                date_fin_validite=fin,
            )

            return Response(
                {
                    "id_situation": situation.id_situation,
                    "up_id": old_up.id_unite_pastorale,
                    "id_geometrie_up": new_geom.id_geometrie_up,
                    "quartiers_count": quartier_qs.count(),
                },
                status=status.HTTP_201_CREATED,
            )

    @action(detail=True, methods=["post"], url_path="duplicate")
    def duplicate(self, request, pk=None):
        with transaction.atomic():
            source = (
                SituationDExploitation.objects.select_for_update(of=("self",))
                .select_related("unite_pastorale", "exploitant")
                .filter(pk=pk)
                .first()
            )
            if source is None:
                return Response(
                    {"detail": "Situation introuvable."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            source_year = (
                source.date_debut.year if source.date_debut else date.today().year
            )
            target_year = source_year + 1

            nom_up = source.unite_pastorale.nom_up if source.unite_pastorale else ""
            nom_exploitant = (
                source.exploitant.nom_exploitant if source.exploitant else ""
            )
            nom_situation = " - ".join(
                filter(None, [nom_up, str(target_year), nom_exploitant])
            )

            new_situation = SituationDExploitation.objects.create(
                nom_situation=nom_situation,
                date_debut=self._replace_year_safe(source.date_debut, target_year),
                date_fin=self._replace_year_safe(source.date_fin, target_year),
                unite_pastorale=source.unite_pastorale,
                exploitant=source.exploitant,
            )

            # 1) Quartiers: clone and map old->new
            quartier_map = {}
            for old_quartier in source.quartiers.all().order_by("id_quartier"):
                new_quartier = QuartierPasto.objects.create(
                    code_quartier=old_quartier.code_quartier,
                    nom_quartier=old_quartier.nom_quartier,
                    geometry=old_quartier.geometry,
                    situation_exploitation=new_situation,
                )
                quartier_map[old_quartier.id_quartier] = new_quartier

            # 2) Cheptels: clone with full-year dates and map old->new
            cheptel_map = {}
            for old_cheptel in source.cheptels.all().order_by("id_cheptel"):
                new_cheptel = Cheptel.objects.create(
                    description=old_cheptel.description,
                    eleveur=old_cheptel.eleveur,
                    exploitant_proprietaire=old_cheptel.exploitant_proprietaire,
                    situation_exploitation=new_situation,
                    nombre_animaux=old_cheptel.nombre_animaux,
                    coefficient_UGB=old_cheptel.coefficient_UGB,
                    production=old_cheptel.production,
                    pension=old_cheptel.pension,
                    race=old_cheptel.race,
                    categorie_animaux=old_cheptel.categorie_animaux,
                    date_debut=date(target_year, 1, 1),
                    date_fin=date(target_year, 12, 31),
                )
                cheptel_map[old_cheptel.id_cheptel] = new_cheptel

            # 3) Parcours: clone with year-shifted dates and remap quartier/cheptel
            source_parcours_qs = (
                Exploiter.objects.filter(
                    Q(cheptel__situation_exploitation=source)
                    | Q(quartier__situation_exploitation=source)
                )
                .distinct()
                .order_by("id_exploiter")
            )

            for old_parcours in source_parcours_qs:
                new_cheptel = cheptel_map.get(old_parcours.cheptel_id)
                new_quartier = quartier_map.get(old_parcours.quartier_id)
                if new_cheptel is None and new_quartier is None:
                    continue

                Exploiter.objects.create(
                    cheptel=new_cheptel,
                    quartier=new_quartier,
                    date_debut=self._replace_year_safe(
                        old_parcours.date_debut, target_year
                    ),
                    date_fin=self._replace_year_safe(
                        old_parcours.date_fin, target_year
                    ),
                    nombre_animaux=old_parcours.nombre_animaux,
                    mode_conduite=old_parcours.mode_conduite,
                    commentaire=old_parcours.commentaire,
                )

            # 4) Equipements exploitant: clone and reattach to new situation
            for old_eq in source.eqptsExploitant.all():
                EquipementExploitant.objects.create(
                    commentaire=old_eq.commentaire,
                    etat=old_eq.etat,
                    geometry=old_eq.geometry,
                    type_equipement=old_eq.type_equipement,
                    situation_exploitation=new_situation,
                )

            serializer = self.get_serializer(new_situation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class RaceViewset(BaseModelViewSet):
    serializer_class = RaceSerializer

    def get_queryset(self):
        queryset = Race.objects.all().order_by("id_race")
        id_race = self.request.GET.get("id_race")
        if id_race is not None:
            queryset = queryset.filter(id_race=id_race)

        return queryset


class BergerViewset(BaseModelViewSet):
    serializer_class = BergerSerializer

    def get_queryset(self):
        queryset = Berger.objects.all().order_by("id_berger")
        return queryset


class GardeSituationViewset(BaseModelViewSet):
    serializer_class = GardeSituationSerializer

    def get_queryset(self):
        queryset = GardeSituation.objects.all().order_by("id_garde_situation")
        id_situation = self.request.GET.get("id_situation")
        if id_situation is not None:
            queryset = queryset.filter(situation_exploitation_id=id_situation)
        return queryset


# Evenements
class TypeEvenementViewset(BaseModelViewSet):
    serializer_class = TypeEvenementSerializer

    def get_queryset(self):
        queryset = TypeEvenement.objects.all().order_by("id_type_evenement")
        return queryset


class EvenementViewset(BaseModelViewSet):
    serializer_class = EvenementSerializer

    def get_queryset(self):
        queryset = Evenement.objects.all().order_by("id_evenement")

        situation_id = self.request.GET.get("situation") or self.request.GET.get(
            "id_situation"
        )
        if situation_id is not None:
            queryset = queryset.filter(situation_id=situation_id)

        return queryset


class LogementViewset(BaseModelViewSet):
    serializer_class = LogementSerializer

    def get_queryset(self):
        queryset = Logement.objects.all().order_by("id_logement")

        logement_code = self.request.GET.get("logement_code")
        if logement_code is not None:
            queryset = queryset.filter(logement_code=logement_code)

        return queryset


class CommoditeViewset(BaseModelViewSet):
    serializer_class = CommoditeSerializer

    def get_queryset(self):
        queryset = Commodite.objects.all().order_by("id_commodite")

        return queryset


class AbriDUrgenceCommoditeViewset(BaseModelViewSet):
    serializer_class = AbriDUrgenceCommoditeSerializer

    def get_queryset(self):
        queryset = AbriDUrgenceCommodite.objects.all().order_by(
            "id_abri_urgence_commodite"
        )
        abri_id = self.request.GET.get("abriId")
        if abri_id is not None:
            queryset = queryset.filter(abri_urgence=abri_id)
        return queryset


class TypeDeSuiviViewset(BaseModelViewSet):
    serializer_class = TypeDeSuiviSerializer

    def get_queryset(self):
        queryset = TypeDeSuivi.objects.all().order_by("id_type_suivi")
        return queryset


class TypeEquipementViewset(BaseModelViewSet):
    serializer_class = TypeEquipementSerializer

    def get_queryset(self):
        queryset = TypeEquipement.objects.all()
        categorie = self.request.GET.get("categorie")
        if categorie is not None:
            categorie = categorie.strip()
            if categorie:
                queryset = queryset.filter(categorie__iexact=categorie)
        return queryset


class EquipementAlpageViewset(BaseModelViewSet):
    serializer_class = EquipementAlpageSerializer

    def get_queryset(self):
        queryset = EquipementAlpage.objects.all().order_by("id_equipement_alpage")

        up_id_raw = (
            self.request.GET.get("unite_pastorale")
            or self.request.GET.get("id_up")
            or self.request.GET.get("up_id")
        )

        if up_id_raw is not None:
            up_id_str = str(up_id_raw).strip()
            if up_id_str:
                queryset = queryset.filter(
                    Q(unite_pastorale_id=up_id_str)
                    | Q(unite_pastorale__id_unite_pastorale=up_id_str)
                )

        return queryset


class EquipementExploitantViewset(BaseModelViewSet):
    serializer_class = EquipementExploitantSerializer

    def get_queryset(self):
        queryset = EquipementExploitant.objects.all().order_by(
            "id_equipement_exploitant"
        )

        id_situation = self.request.GET.get("id_situation") or self.request.GET.get(
            "situation_exploitation"
        )
        if id_situation is not None:
            queryset = queryset.filter(situation_exploitation_id=id_situation)

        return queryset

    @transaction.atomic
    def perform_destroy(self, instance):
        from auditlog.context import set_actor

        with set_actor(self._get_auditlog_actor()):
            bd = instance.beneficier_de
            instance.beneficier_de = None
            instance.save(update_fields=["beneficier_de"])
            instance.delete()
            if bd:
                bd.delete()

    @transaction.atomic
    def perform_create(self, serializer):
        save_kwargs = self._audit_save_kwargs(serializer, is_create=True)
        equipement = serializer.save(**save_kwargs)
        self._sync_beneficier_de(equipement)

    @transaction.atomic
    def perform_update(self, serializer):
        save_kwargs = self._audit_save_kwargs(serializer, is_create=False)
        equipement = serializer.save(**save_kwargs)
        self._sync_beneficier_de(equipement)

    def _sync_beneficier_de(self, equipement):
        is_abri = (
            equipement.type_equipement is not None
            and equipement.type_equipement.description.lower() == "abri héliportable"
        )

        if not is_abri:
            if equipement.beneficier_de_id:
                old_bd = equipement.beneficier_de
                equipement.beneficier_de = None
                equipement.save(update_fields=["beneficier_de"])
                old_bd.delete()
            return

        props = self.request.data.get("properties", {})
        abri_urgence_id = props.get("abri_urgence")
        date_debut = props.get("date_debut")
        date_fin = props.get("date_fin") or None

        if not abri_urgence_id or not date_debut:
            return

        try:
            abri_urgence = AbriDUrgence.objects.get(pk=abri_urgence_id)
        except AbriDUrgence.DoesNotExist:
            return

        actor = self._get_actor_name()
        exploitant = (
            equipement.situation_exploitation.exploitant
            if equipement.situation_exploitation
            else None
        )

        if equipement.beneficier_de_id:
            bd = equipement.beneficier_de
            bd.exploitant = exploitant
            bd.abri_urgence = abri_urgence
            bd.date_debut = date_debut
            bd.date_fin = date_fin
            bd.geometry = equipement.geometry
            bd.modified_by = actor
            bd.modified_on = timezone.now()
            bd.save()
        else:
            bd = BeneficierDe.objects.create(
                exploitant=exploitant,
                abri_urgence=abri_urgence,
                date_debut=date_debut,
                date_fin=date_fin,
                geometry=equipement.geometry,
                created_by=actor,
            )
            equipement.beneficier_de = bd
            equipement.save(update_fields=["beneficier_de"])


class CheptelViewset(BaseModelViewSet):
    serializer_class = CheptelSerializer

    def get_queryset(self):
        queryset = Cheptel.objects.all().order_by("id_cheptel")
        id_cheptel = self.request.GET.get("id_cheptel")
        if id_cheptel is not None:
            queryset = queryset.filter(id_cheptel=id_cheptel)

        id_situation = self.request.GET.get("id_situation")
        if id_situation is not None:
            queryset = queryset.filter(situation_exploitation_id=id_situation)

        return queryset


class CategoriePensionViewset(BaseModelViewSet):
    serializer_class = CategoriePensionSerializer

    def get_queryset(self):
        queryset = CategoriePension.objects.all().order_by("id_categorie_pension")
        id_categorie_pension = self.request.GET.get("id_categorie_pension")
        if id_categorie_pension is not None:
            queryset = queryset.filter(id_categorie_pension=id_categorie_pension)

        return queryset


class EspeceViewset(BaseModelViewSet):
    serializer_class = EspeceSerializer

    def get_queryset(self):
        queryset = Espece.objects.all().order_by("id_espece")
        id_espece = self.request.GET.get("id_espece")
        if id_espece is not None:
            queryset = queryset.filter(id_espece=id_espece)
        return queryset


class CategorieAnimauxViewset(BaseModelViewSet):
    serializer_class = CategorieAnimauxSerializer

    def get_queryset(self):
        queryset = CategorieAnimaux.objects.all().order_by("id_categorie_animaux")
        return queryset


class ProprietaireUnitePastoraleViewset(BaseModelViewSet):
    serializer_class = ProprietaireUnitePastoraleSerializer

    def get_queryset(self):
        queryset = ProprietaireUnitePastorale.objects.all()
        return queryset


class QuartierPastoViewset(BaseModelViewSet):
    serializer_class = QuartierPastoSerializer

    def get_queryset(self):
        queryset = QuartierPasto.objects.all().order_by("code_quartier")

        id_situation = self.request.GET.get("id_situation")
        if id_situation is not None:
            queryset = queryset.filter(situation_exploitation_id=id_situation)

        return queryset

    @action(detail=True, methods=["post"], url_path="split")
    def split(self, request, pk=None):
        quartier = self.get_object()

        line_geojson = request.data.get("line")
        if not line_geojson:
            return Response(
                {"detail": "Le paramètre 'line' (GeoJSON LineString) est requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not quartier.geometry:
            return Response(
                {"detail": "Ce quartier n'a pas de géométrie à découper."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        line_geojson_str = (
            json.dumps(line_geojson) if isinstance(line_geojson, dict) else line_geojson
        )

        sql = """
            WITH
            q AS (
                SELECT (ST_Dump(geometry)).geom AS geom
                FROM suivi_pasto_quartierpasto WHERE id_quartier = %(id)s
            ),
            blade AS (
                SELECT ST_Transform(ST_GeomFromGeoJSON(%(line)s), 2154) AS geom
            ),
            parts AS (
                SELECT
                    (ST_Dump(
                        ST_CollectionExtract(
                            ST_Split(
                                ST_Snap(q.geom, blade.geom, 0.001),
                                blade.geom
                            ),
                            3
                        )
                    )).geom AS part_geom
                FROM q, blade
            )
            SELECT ST_AsGeoJSON(ST_Transform(part_geom, 4326)) AS geojson
            FROM parts
            ORDER BY ST_Area(part_geom) DESC
        """

        with connection.cursor() as cursor:
            cursor.execute(sql, {"id": quartier.pk, "line": line_geojson_str})
            rows = cursor.fetchall()

        original_num_geoms = quartier.geometry.num_geom if quartier.geometry else 1
        if len(rows) <= original_num_geoms:
            return Response(
                {
                    "detail": "La ligne ne traverse pas entièrement le quartier. Assurez-vous qu'elle entre et sort du polygone."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Convert back to SRID 2154 for storage via GeoJSON round-trip through PostGIS
        def geojson_4326_to_2154(geojson_dict):
            sql_convert = "SELECT ST_AsText(ST_Transform(ST_GeomFromGeoJSON(%s), 2154))"
            with connection.cursor() as cur:
                cur.execute(sql_convert, [json.dumps(geojson_dict)])
                return cur.fetchone()[0]

        def rows_to_multi(geojson_dicts, srid=2154):
            from django.contrib.gis.geos import GEOSGeometry

            polys = [
                GEOSGeometry(geojson_4326_to_2154(g), srid=srid) for g in geojson_dicts
            ]
            return MultiPolygon(*polys, srid=srid)

        # quartier1 = largest part + any remaining parts not assigned to quartier2
        # quartier2 = second largest part (the split-off piece)
        q1_geojsons = [json.loads(rows[0][0])] + [json.loads(r[0]) for r in rows[2:]]
        q2_geojsons = [json.loads(rows[1][0])]

        with transaction.atomic():
            quartier.geometry = rows_to_multi(q1_geojsons)
            quartier.save(update_fields=["geometry", "modified_by", "modified_on"])

            new_quartier = QuartierPasto.objects.create(
                code_quartier=(
                    f"{quartier.code_quartier}_2" if quartier.code_quartier else None
                ),
                nom_quartier=(
                    f"{quartier.nom_quartier} (2)" if quartier.nom_quartier else None
                ),
                geometry=rows_to_multi(q2_geojsons),
                situation_exploitation=quartier.situation_exploitation,
            )

        q1 = QuartierPasto.objects.get(pk=quartier.pk)
        q2 = QuartierPasto.objects.get(pk=new_quartier.pk)

        return Response(
            {
                "quartier1": self.get_serializer(q1).data,
                "quartier2": self.get_serializer(q2).data,
            },
            status=status.HTTP_200_OK,
        )


class PlanDeSuiviViewset(BaseModelViewSet):
    serializer_class = PlanDeSuiviSerializer

    def get_queryset(self):
        queryset = (
            PlanDeSuivi.objects.all()
            .select_related("type_suivi")
            .select_related("unite_pastorale")
            .order_by("id_plan_suivi")
        )
        unite_pastorale = self.request.GET.get("unite_pastorale")
        if unite_pastorale is not None:
            queryset = queryset.filter(unite_pastorale_id=unite_pastorale)
        return queryset


class ExploiterViewset(BaseModelViewSet):
    serializer_class = ExploiterSerializer

    def get_queryset(self):
        queryset = Exploiter.objects.all().order_by("id_exploiter")

        id_situation = self.request.GET.get("id_situation")
        if id_situation is not None:
            # Un parcours est lié à une situation via le cheptel et/ou le quartier.
            queryset = queryset.filter(
                Q(cheptel__situation_exploitation_id=id_situation)
                | Q(quartier__situation_exploitation_id=id_situation)
            ).distinct()

        return queryset


class EleveurViewset(BaseModelViewSet):
    serializer_class = EleveurSerializer

    def get_queryset(self):
        queryset = Eleveur.objects.all().order_by("nom_eleveur")
        return queryset

    @action(detail=False, methods=["get"], url_path="by-exploitant/(?P<expl_id>[^/.]+)")
    def by_exploitant(self, request, expl_id=None):
        # Récupérer tous les EtreCompose pour l'exploitant
        compositions = EtreCompose.objects.filter(exploitant_id=expl_id).select_related(
            "eleveur"
        )
        eleveurs = [c.eleveur for c in compositions if c.eleveur is not None]

        # Sérialiser manuellement
        data = [
            {
                "id_eleveur": e.id_eleveur,
                "nom_eleveur": e.nom_eleveur,
                "prenom_eleveur": e.prenom_eleveur,
            }
            for e in eleveurs
        ]
        return Response(data)

    @action(
        detail=False, methods=["get"], url_path="by-unite-pastorale/(?P<up_id>[^/.]+)"
    )
    def by_unite_pastorale(self, request, up_id=None):
        eleveur_ids = (
            EtreCompose.objects.filter(exploitant__situations__unite_pastorale_id=up_id)
            .values_list("eleveur_id", flat=True)
            .distinct()
        )
        eleveurs = Eleveur.objects.filter(id_eleveur__in=eleveur_ids).order_by(
            "nom_eleveur"
        )
        return Response(EleveurSerializer(eleveurs, many=True).data)


class TypeDExploitantViewset(BaseModelViewSet):
    serializer_class = TypeDExploitantSerializer

    def get_queryset(self):
        queryset = TypeDExploitant.objects.all().order_by("id_type_exploitant")
        return queryset


class ExploitantViewset(BaseModelViewSet):
    serializer_class = ExploitantSerializer

    def get_queryset(self):
        queryset = (
            Exploitant.objects.all()
            .select_related("type_exploitant")
            .order_by("id_exploitant")
        )
        return queryset

    @action(detail=True, methods=["get"], url_path="proprietaires")
    def proprietaires(self, request, pk=None):
        compositions = EtreCompose.objects.filter(exploitant_id=pk).select_related(
            "eleveur", "exploitant_membre"
        )
        data = []
        for c in compositions:
            if c.eleveur_id:
                nom = (c.eleveur.nom_eleveur or "").upper()
                prenom = c.eleveur.prenom_eleveur or ""
                label = f"{nom} {prenom}".strip()
                data.append(
                    {
                        "type": "eleveur",
                        "id": c.eleveur_id,
                        "label": label,
                    }
                )
            elif c.exploitant_membre_id:
                data.append(
                    {
                        "type": "exploitant",
                        "id": c.exploitant_membre_id,
                        "label": c.exploitant_membre.nom_exploitant,
                    }
                )
        data.sort(key=lambda x: x["label"].lower())
        return Response(data)


class EtreComposeViewset(BaseModelViewSet):
    serializer_class = EtreComposeSerializer

    def get_queryset(self):
        return EtreCompose.objects.select_related(
            "exploitant", "eleveur", "exploitant_membre"
        ).order_by("id_etre_compose")


class SubventionPNVViewset(BaseModelViewSet):
    serializer_class = SubventionPNVSerializer

    def get_queryset(self):
        queryset = (
            SubventionPNV.objects.all()
            .select_related("exploitant")
            .order_by("id_subvention")
        )
        return queryset


class AbriDUrgenceViewset(BaseModelViewSet):
    serializer_class = AbriDUrgenceSerializer

    def get_queryset(self):
        queryset = AbriDUrgence.objects.all().order_by("id_abri_urgence")
        return queryset


class BeneficierDeViewset(BaseModelViewSet):
    serializer_class = BeneficierDeSerializer

    def get_queryset(self):
        queryset = BeneficierDe.objects.all().order_by("id_beneficier_de")
        return queryset


class RucheViewset(BaseModelViewSet):
    serializer_class = RucheSerializer

    def get_queryset(self):
        queryset = Ruche.objects.all().order_by("id_ruche")
        return queryset


class ProductionViewset(BaseModelViewSet):
    serializer_class = ProductionSerializer

    def get_queryset(self):
        queryset = Production.objects.all().order_by("id_production")
        return queryset


class VisiteViewset(BaseModelViewSet):
    serializer_class = VisiteSerializer

    def get_queryset(self):
        qs = (
            Visite.objects.select_related("unite_pastorale")
            .prefetch_related("observateurs", "contacts_alpagistes")
            .order_by("-date_visite")
        )
        up = self.request.query_params.get("unite_pastorale")
        if up:
            qs = qs.filter(unite_pastorale=up)
        return qs
