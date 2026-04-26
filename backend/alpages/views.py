import logging
from calendar import monthrange
from datetime import date

from django.db import transaction
from django.db.models import Q

from django.contrib.gis.geos import MultiPolygon
from django.contrib.gis.db.models import Union
from django.contrib.gis.db.models.functions import Transform, MakeValid, SnapToGrid

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, action

from .pagination import DefaultPagination
from .viewsets_base import BaseModelViewSet

from alpages.models import Logement, Commodite, LogementCommodite
from alpages.models import UnitePastorale, ProprietaireFoncier, QuartierPasto, ProprietaireUnitePastorale
from alpages.models import TypeDeSuivi, PlanDeSuivi, TypeDeMesure, MesureDePlan
from alpages.models import TypeConvention, ConventionDExploitation, Eleveur, TypeDExploitant, Exploitant, EtreCompose, SubventionPNV, AbriDUrgence, AbriDUrgenceCommodite, BeneficierDe
from alpages.models import SituationDExploitation, Exploiter

from alpages.models import Cheptel, TypeCheptel, Production, CategoriePension, Espece, Race, CategorieAnimaux
from alpages.serializers import CheptelSerializer, TypeCheptelSerializer, ProductionSerializer, CategoriePensionSerializer, EspeceSerializer, RaceSerializer, CategorieAnimauxSerializer

from alpages.models import Ruche, Berger, GardeSituation
from alpages.serializers import RucheSerializer, BergerSerializer, GardeSituationSerializer

from alpages.models import TypeEvenement, Evenement
from alpages.serializers import TypeEvenementSerializer, EvenementSerializer

from alpages.serializers import LogementSerializer, CommoditeSerializer, LogementCommoditeSerializer
from alpages.serializers import UnitePastoraleSerializer, UnitePastoraleLSerializer, ProprietaireFoncierSerializer, QuartierPastoSerializer, ProprietaireUnitePastoraleSerializer
from alpages.serializers import TypeDeSuiviSerializer, PlanDeSuiviSerializer, TypeDeMesureSerializer, MesureDePlanSerializer
from alpages.serializers import TypeConventionSerializer, ConventionDExploitationSerializer, EleveurSerializer, TypeDExploitantSerializer, ExploitantSerializer, EtreComposeSerializer, SubventionPNVSerializer, AbriDUrgenceSerializer, AbriDUrgenceCommoditeSerializer, BeneficierDeSerializer
from alpages.serializers import SituationDExploitationSerializer, ExploiterSerializer

from alpages.models import TypeEquipement, EquipementExploitant, EquipementAlpage
from alpages.serializers import TypeEquipementSerializer, EquipementExploitantSerializer, EquipementAlpageSerializer

##########
# Refactoring Elever et TypeCheptel pour les fusionner en Cheptel et Type_cheptel
# dlg le 10/2/26
from alpages.models import Cheptel, TypeCheptel, Production, CategoriePension, Espece, Race, CategorieAnimaux
from alpages.serializers import CheptelSerializer, TypeCheptelSerializer, ProductionSerializer, CategoriePensionSerializer, EspeceSerializer, RaceSerializer, CategorieAnimauxSerializer
##########

from .choices_logement import LST_STATUT, LST_ACCES_FINAL, LST_PROPRIETE, LST_TYPE_LOGEMENT, LST_MULTIUSAGE, LST_ACCUEIL_PUBLIC,\
                              LST_ACTIVITE_LAITIERE, LST_ETAT_BATIMENT, LST_SURFACE_LOGEMENT, LST_WC, LST_ALIM_ELECTRIQUE, LST_ALIM_EAU,\
                              LST_ORIGINE_EAU, LST_QUALITE_EAU, LST_DISPO_EAU, LST_ASSAINISSEMENT, LST_CHAUFFE_EAU, LST_OUI_NON, LST_OUI_NON_INC

logger = logging.getLogger(__name__)




@api_view(['GET'])
def get_choices_logement(request):
    data = {
        'statut': [{'value': value, 'display': display} for value, display in LST_STATUT],
        'acces_final': [{'value': value, 'display': display} for value, display in LST_ACCES_FINAL],
        'propriete': [{'value': value, 'display': display} for value, display in LST_PROPRIETE],
        'type_logement': [{'value': value, 'display': display} for value, display in LST_TYPE_LOGEMENT],
        'multiusage': [{'value': value, 'display': display} for value, display in LST_MULTIUSAGE],
        'accueil_public': [{'value': value, 'display': display} for value, display in LST_ACCUEIL_PUBLIC],
        'activite_laitiere': [{'value': value, 'display': display} for value, display in LST_ACTIVITE_LAITIERE],
        'etat_batiment': [{'value': value, 'display': display} for value, display in LST_ETAT_BATIMENT],
        'mixite_possible': [{'value': value, 'display': display} for value, display in LST_OUI_NON_INC],
        'surface_logement': [{'value': value, 'display': display} for value, display in LST_SURFACE_LOGEMENT],
        'presence_douche': [{'value': value, 'display': display} for value, display in LST_OUI_NON_INC],
        'type_wc': [{'value': value, 'display': display} for value, display in LST_WC],
        'alim_elec': [{'value': value, 'display': display} for value, display in LST_ALIM_ELECTRIQUE],
        'alim_eau': [{'value': value, 'display': display} for value, display in LST_ALIM_EAU],
        'origine_eau': [{'value': value, 'display': display} for value, display in LST_ORIGINE_EAU],
        'qualite_eau': [{'value': value, 'display': display} for value, display in LST_QUALITE_EAU],
        'dispo_eau': [{'value': value, 'display': display} for value, display in LST_DISPO_EAU],
        'assainissement': [{'value': value, 'display': display} for value, display in LST_ASSAINISSEMENT],
        'chauffe_eau': [{'value': value, 'display': display} for value, display in LST_CHAUFFE_EAU],
        'chauffage': [{'value': value, 'display': display} for value, display in LST_OUI_NON],
        'stockage_indep': [{'value': value, 'display': display} for value, display in LST_OUI_NON]
    }
    return Response(data)


# Bloc administratif (orange)
class UnitePastoraleViewset(BaseModelViewSet):
    serializer_class = UnitePastoraleSerializer

    def get_queryset(self):
        queryset = UnitePastorale.objects.all().order_by('nom_up')
        
        nom_up_filter = self.request.GET.get('nom_up')
        if nom_up_filter is not None:
            queryset = queryset.filter(nom_up=nom_up_filter)
          
        return queryset

    # /unitePastorale/light/ → Serializer Light
    @action(detail=False, methods=['get'], url_path='light')
    def list_light(self, request):
        queryset = self.get_queryset()
        # Use the light serializer for this endpoint; enable pagination when
        # `page` param is present.
        self.pagination_class = DefaultPagination
        return self.conditional_list(request, serializer_class=UnitePastoraleLSerializer)


   
class ProprietaireFoncierViewset(BaseModelViewSet):
    serializer_class = ProprietaireFoncierSerializer

    def get_queryset(self):
        queryset = ProprietaireFoncier.objects.all().order_by('id_proprietaire')
        return queryset
    
    

class TypeDeMesureViewset(BaseModelViewSet):
    serializer_class = TypeDeMesureSerializer

    def get_queryset(self):
        queryset = TypeDeMesure.objects.all().order_by('id_type_mesure')
        return queryset


class MesureDePlanViewset(BaseModelViewSet):
    serializer_class = MesureDePlanSerializer

    def get_queryset(self):
        queryset = MesureDePlan.objects.all().select_related('type_mesure').select_related('plan_suivi').order_by('id_mesure_plan')
        return queryset
    

# Bloc exploitation
class TypeConventionViewset(BaseModelViewSet):
    serializer_class = TypeConventionSerializer

    def get_queryset(self):
        queryset = TypeConvention.objects.all().order_by('id_type_convention')
        return queryset

class ConventionDExploitationViewset(BaseModelViewSet):
    serializer_class = ConventionDExploitationSerializer

    def get_queryset(self):
        queryset = ConventionDExploitation.objects.all().select_related('type_convention').order_by('id_convention')
        return queryset

class SituationDExploitationViewset(BaseModelViewSet):
    serializer_class = SituationDExploitationSerializer

    def get_queryset(self):
        queryset = SituationDExploitation.objects.all().order_by('id_situation')

        id_up_filter = self.request.GET.get('id_up')
        if id_up_filter is not None:
            queryset = queryset.filter(unite_pastorale_id=id_up_filter)
        return queryset

    def _ensure_multipolygon(self, geometry):
        """Force une géométrie en MultiPolygon (SRID 2154)."""
        if geometry is None or geometry.empty:
            return None

        if geometry.srid != 2154:
            geometry.transform(2154)

        if geometry.geom_type == 'Polygon':
            return MultiPolygon(geometry, srid=2154)

        return geometry

    def _replace_year_safe(self, value, new_year):
        """Replace year while preserving month/day, clamping invalid month-end dates."""
        if value is None:
            return None

        max_day = monthrange(new_year, value.month)[1]
        return value.replace(year=new_year, day=min(value.day, max_day))

    @action(detail=True, methods=['post'], url_path='mettre-a-jour-up')
    def mettre_a_jour_up(self, request, pk=None):
        with transaction.atomic():
            situation = (
                SituationDExploitation.objects.select_for_update()
                .filter(pk=pk)
                .first()
            )
            if situation is None:
                return Response(
                    {'detail': 'Situation introuvable.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            old_up = situation.unite_pastorale
            if old_up is None:
                return Response(
                    {'detail': "La situation n'est rattachée à aucune UP."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            quartier_qs = QuartierPasto.objects.filter(
                situation_exploitation=situation,
                geometry__isnull=False,
            )

            if not quartier_qs.exists():
                return Response(
                    {'detail': 'Aucune géométrie de quartier disponible pour cette situation.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 🔥 UNION EN BASE (PostGIS)
            agg = quartier_qs.aggregate(
                geom=Union(
                    MakeValid(
                        SnapToGrid(
                            Transform('geometry', 2154),
                            0.01  # tolérance à ajuster
                        )
                    )
                )
            )
            

            union_geometry = agg['geom']

            if union_geometry:
                union_geometry = union_geometry.buffer(0)

            if union_geometry is None or union_geometry.empty:
                return Response(
                    {'detail': "L'union des quartiers ne produit pas de géométrie exploitable."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            union_multipolygon = self._ensure_multipolygon(union_geometry)
            if union_multipolygon is None:
                return Response(
                    {'detail': "Impossible de générer un MultiPolygon valide."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            new_up = UnitePastorale.objects.create(
                code_up=old_up.code_up,
                nom_up=old_up.nom_up,
                annee_version=situation.annee,
                geometry=union_multipolygon,
                version_active=True,
                secteur=old_up.secteur,
            )

            # duplication des propriétaires
            old_links = ProprietaireUnitePastorale.objects.filter(unite_pastorale=old_up)
            for old_link in old_links:
                ProprietaireUnitePastorale.objects.create(
                    proprietaire=old_link.proprietaire,
                    unite_pastorale=new_up,
                )

            # mise à jour situation
            situation.unite_pastorale = new_up
            situation.save(update_fields=['unite_pastorale'])

            # désactivation ancienne version
            UnitePastorale.objects.filter(
                code_up=old_up.code_up,
                version_active=True,
            ).exclude(pk=new_up.pk).update(version_active=False)

            return Response(
                {
                    'id_situation': situation.id_situation,
                    'old_up_id': old_up.id_unite_pastorale,
                    'new_up_id': new_up.id_unite_pastorale,
                    'new_up_annee_version': new_up.annee_version,
                    'quartiers_count': quartier_qs.count(),
                },
                status=status.HTTP_201_CREATED,
            )

    @action(detail=True, methods=['post'], url_path='duplicate')
    def duplicate(self, request, pk=None):
        with transaction.atomic():
            source = (
                SituationDExploitation.objects.select_for_update()
                .select_related('unite_pastorale', 'exploitant')
                .filter(pk=pk)
                .first()
            )
            if source is None:
                return Response(
                    {'detail': 'Situation introuvable.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            target_year = source.annee + 1
            if source.unite_pastorale_id and SituationDExploitation.objects.filter(
                unite_pastorale_id=source.unite_pastorale_id,
                annee=target_year,
            ).exists():
                return Response(
                    {'detail': "Une situation existe déjà pour cette UP et l'année suivante."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            nom_up = source.unite_pastorale.nom_up if source.unite_pastorale else ''
            nom_exploitant = source.exploitant.nom_exploitant if source.exploitant else ''
            nom_situation = ' - '.join(filter(None, [nom_up, str(target_year), nom_exploitant]))

            new_situation = SituationDExploitation.objects.create(
                annee=target_year,
                nom_situation=nom_situation,
                situation_active=source.situation_active,
                date_debut=self._replace_year_safe(source.date_debut, target_year),
                date_fin=self._replace_year_safe(source.date_fin, target_year),
                unite_pastorale=source.unite_pastorale,
                exploitant=source.exploitant,
            )

            # 1) Quartiers: clone and map old->new
            quartier_map = {}
            for old_quartier in source.quartiers.all().order_by('id_quartier'):
                new_quartier = QuartierPasto.objects.create(
                    code_quartier=old_quartier.code_quartier,
                    nom_quartier=old_quartier.nom_quartier,
                    geometry=old_quartier.geometry,
                    situation_exploitation=new_situation,
                )
                quartier_map[old_quartier.id_quartier] = new_quartier

            # 2) Cheptels: clone with full-year dates and map old->new
            cheptel_map = {}
            for old_cheptel in source.cheptels.all().order_by('id_cheptel'):
                new_cheptel = Cheptel.objects.create(
                    description=old_cheptel.description,
                    eleveur=old_cheptel.eleveur,
                    situation_exploitation=new_situation,
                    type_cheptel=old_cheptel.type_cheptel,
                    nombre_animaux=old_cheptel.nombre_animaux,
                    date_debut=date(target_year, 1, 1),
                    date_fin=date(target_year, 12, 31),
                )
                cheptel_map[old_cheptel.id_cheptel] = new_cheptel

            # 3) Parcours: clone with year-shifted dates and remap quartier/cheptel
            source_parcours_qs = Exploiter.objects.filter(
                Q(cheptel__situation_exploitation=source)
                | Q(quartier__situation_exploitation=source)
            ).distinct().order_by('id_exploiter')

            for old_parcours in source_parcours_qs:
                new_cheptel = cheptel_map.get(old_parcours.cheptel_id)
                new_quartier = quartier_map.get(old_parcours.quartier_id)
                if new_cheptel is None and new_quartier is None:
                    continue

                Exploiter.objects.create(
                    cheptel=new_cheptel,
                    quartier=new_quartier,
                    date_debut=self._replace_year_safe(old_parcours.date_debut, target_year),
                    date_fin=self._replace_year_safe(old_parcours.date_fin, target_year),
                    nombre_animaux=old_parcours.nombre_animaux,
                    mode_conduite=old_parcours.mode_conduite,
                    commentaire=old_parcours.commentaire,
                )

            # 4) Equipements exploitant: clone and reattach to new situation
            for old_eq in source.eqptsExploitant.all():
                EquipementExploitant.objects.create(
                    description=old_eq.description,
                    etat=old_eq.etat,
                    geometry=old_eq.geometry,
                    type_equipement=old_eq.type_equipement,
                    situation_exploitation=new_situation,
                )

            serializer = self.get_serializer(new_situation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class TypeCheptelViewset(BaseModelViewSet):
    serializer_class = TypeCheptelSerializer

    def get_queryset(self):
        queryset = TypeCheptel.objects.all().order_by('id_type_cheptel')
        id_type_cheptel = self.request.GET.get('id_type_cheptel')
        if id_type_cheptel is not None:
            queryset = queryset.filter(id_type_cheptel=id_type_cheptel)

        return queryset

class RaceViewset(BaseModelViewSet):
    serializer_class = RaceSerializer

    def get_queryset(self):
        queryset = Race.objects.all().order_by('id_race')
        id_race = self.request.GET.get('id_race')
        if id_race is not None:
            queryset = queryset.filter(id_race=id_race)

        return queryset

class BergerViewset(BaseModelViewSet):
    serializer_class = BergerSerializer

    def get_queryset(self):
        queryset = Berger.objects.all().order_by('id_berger')
        return queryset

class GardeSituationViewset(BaseModelViewSet):
    serializer_class = GardeSituationSerializer

    def get_queryset(self):
        queryset = GardeSituation.objects.all().order_by('id_garde_situation')
        return queryset
 
# Evenements
class TypeEvenementViewset(BaseModelViewSet):
    serializer_class = TypeEvenementSerializer

    def get_queryset(self):
        queryset = TypeEvenement.objects.all().order_by('id_type_evenement')
        return queryset

class EvenementViewset(BaseModelViewSet):
    serializer_class = EvenementSerializer

    def get_queryset(self):
        queryset = Evenement.objects.all().order_by('id_evenement')

        up_id = self.request.GET.get('unite_pastorale') or self.request.GET.get('id_up')
        if up_id is not None:
            queryset = queryset.filter(unite_pastorale_id=up_id)

        return queryset
    
class LogementViewset(BaseModelViewSet):
    serializer_class = LogementSerializer

    def get_queryset(self):
        queryset = Logement.objects.all().order_by('id_logement')

        logement_code = self.request.GET.get('logement_code')
        if logement_code is not None:
            queryset = queryset.filter(logement_code=logement_code)

        return queryset

class CommoditeViewset(BaseModelViewSet):
    serializer_class = CommoditeSerializer

    def get_queryset(self):
        queryset = Commodite.objects.all().order_by('id_commodite')

        return queryset
 
class LogementCommoditeViewset(BaseModelViewSet):
    serializer_class = LogementCommoditeSerializer

    def get_queryset(self):
        queryset = LogementCommodite.objects.all().order_by('id_logement_commodite')
        logement_id = self.request.GET.get('logementId')
        if logement_id is not None:
            queryset = queryset.filter(logement=logement_id)
        return queryset


class AbriDUrgenceCommoditeViewset(BaseModelViewSet):
    serializer_class = AbriDUrgenceCommoditeSerializer

    def get_queryset(self):
        queryset = AbriDUrgenceCommodite.objects.all().order_by('id_abri_urgence_commodite')
        abri_id = self.request.GET.get('abriId')
        if abri_id is not None:
            queryset =queryset.filter(abri_urgence=abri_id)
        return queryset



class TypeDeSuiviViewset(BaseModelViewSet):
    serializer_class = TypeDeSuiviSerializer

    def get_queryset(self):
        queryset = TypeDeSuivi.objects.all().order_by('id_type_suivi')
        return queryset
    
class TypeEquipementViewset(BaseModelViewSet):
    serializer_class = TypeEquipementSerializer
    
    def get_queryset(self):
        queryset = TypeEquipement.objects.all()
        categorie = self.request.GET.get('categorie')
        if categorie is not None:
            categorie = categorie.strip()
            if categorie:
                queryset = queryset.filter(categorie__iexact=categorie)
        return queryset

class EquipementAlpageViewset(BaseModelViewSet):
    serializer_class = EquipementAlpageSerializer

    def get_queryset(self):
        queryset = EquipementAlpage.objects.all().order_by('id_equipement_alpage')

        up_id_raw = (
            self.request.GET.get('unite_pastorale')
            or self.request.GET.get('id_up')
            or self.request.GET.get('up_id')
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
        queryset = EquipementExploitant.objects.all().order_by('id_equipement_exploitant')

        id_situation = self.request.GET.get('id_situation') or self.request.GET.get('situation_exploitation')
        if id_situation is not None:
            queryset = queryset.filter(situation_exploitation_id=id_situation)

        return queryset


###########
# Refactoring Elever et TypeCheptel pour les fusionner en Cheptel et Type_cheptel
# dlg le 10/2/26
class CheptelViewset(BaseModelViewSet):
    serializer_class = CheptelSerializer

    def get_queryset(self):
        queryset = Cheptel.objects.all().order_by('id_cheptel')
        id_cheptel = self.request.GET.get('id_cheptel')
        if id_cheptel is not None:
            queryset = queryset.filter(id_cheptel=id_cheptel)

        id_situation = self.request.GET.get('id_situation')
        if id_situation is not None:
            queryset = queryset.filter(situation_exploitation_id=id_situation)

        return queryset


class CategoriePensionViewset(BaseModelViewSet):
    serializer_class = CategoriePensionSerializer

    def get_queryset(self):
        queryset = CategoriePension.objects.all().order_by('id_categorie_pension')
        id_categorie_pension = self.request.GET.get('id_categorie_pension')
        if id_categorie_pension is not None:
            queryset = queryset.filter(id_categorie_pension=id_categorie_pension)

        return queryset


class EspeceViewset(BaseModelViewSet):
    serializer_class = EspeceSerializer

    def get_queryset(self):
        queryset = Espece.objects.all().order_by('id_espece')
        id_espece = self.request.GET.get('id_espece')
        if id_espece is not None:
            queryset = queryset.filter(id_espece=id_espece)
        return queryset



class CategorieAnimauxViewset(BaseModelViewSet):
    serializer_class = CategorieAnimauxSerializer

    def get_queryset(self):
        queryset = CategorieAnimaux.objects.all().order_by('id_categorie_animaux')
        return queryset
    
# Refactoring Elever et TypeCheptel pour les fusionner en Cheptel et Type_cheptel
# dlg le 10/2/26
###########


class ProprietaireUnitePastoraleViewset(BaseModelViewSet):
    serializer_class = ProprietaireUnitePastoraleSerializer

    def get_queryset(self):
        queryset = ProprietaireUnitePastorale.objects.all()
        return queryset


class QuartierPastoViewset(BaseModelViewSet):
    serializer_class = QuartierPastoSerializer

    def get_queryset(self):
        queryset = QuartierPasto.objects.all().order_by('code_quartier')

        id_situation = self.request.GET.get('id_situation')
        if id_situation is not None:
            queryset = queryset.filter(situation_exploitation_id=id_situation)

        return queryset
        
    # def get_queryset(self):
    #     queryset = QuartierPasto.objects.all().order_by('unite_pastorale', 'code_quartier')

    #     up_id = self.request.GET.get('up_id')
    #     if up_id is not None:
    #         queryset = queryset.filter(unite_pastorale=up_id)

    #     return queryset

class PlanDeSuiviViewset(BaseModelViewSet):
    serializer_class = PlanDeSuiviSerializer

    def get_queryset(self):
        queryset = PlanDeSuivi.objects.all().select_related('type_suivi').select_related('unite_pastorale').order_by('id_plan_suivi')
        return queryset

class ExploiterViewset(BaseModelViewSet):
    serializer_class = ExploiterSerializer

    def get_queryset(self):
        queryset = Exploiter.objects.all().order_by('id_exploiter')

        id_situation = self.request.GET.get('id_situation')
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
        queryset = Eleveur.objects.all().order_by('nom_eleveur')
        return queryset

    @action(detail=False, methods=['get'], url_path='by-exploitant/(?P<expl_id>[^/.]+)')
    def by_exploitant(self, request, expl_id=None):
        # Récupérer tous les EtreCompose pour l'exploitant
        compositions = EtreCompose.objects.filter(exploitant_id=expl_id).select_related('eleveur')
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

class TypeDExploitantViewset(BaseModelViewSet):
    serializer_class = TypeDExploitantSerializer

    def get_queryset(self):
        queryset = TypeDExploitant.objects.all().order_by('id_type_exploitant')
        return queryset

class ExploitantViewset(BaseModelViewSet):
    serializer_class = ExploitantSerializer

    def get_queryset(self):
        queryset = Exploitant.objects.all().select_related('type_exploitant').order_by('id_exploitant')
        return queryset

class EtreComposeViewset(BaseModelViewSet):
    serializer_class = EtreComposeSerializer

    def get_queryset(self):
        queryset = EtreCompose.objects.all()
        return queryset

class SubventionPNVViewset(BaseModelViewSet):
    serializer_class = SubventionPNVSerializer

    def get_queryset(self):
        queryset = SubventionPNV.objects.all().select_related('exploitant').order_by('id_subvention')
        return queryset

class AbriDUrgenceViewset(BaseModelViewSet):
    serializer_class = AbriDUrgenceSerializer

    def get_queryset(self):
        queryset = AbriDUrgence.objects.all().order_by('id_abri_urgence')
        return queryset

class BeneficierDeViewset(BaseModelViewSet):
    serializer_class = BeneficierDeSerializer

    def get_queryset(self):
        queryset = BeneficierDe.objects.all().order_by('id_beneficier_de')
        return queryset

class RucheViewset(BaseModelViewSet):
    serializer_class = RucheSerializer

    def get_queryset(self):
        queryset = Ruche.objects.all().order_by('id_ruche')
        return queryset

class ProductionViewset(BaseModelViewSet):
    serializer_class = ProductionSerializer

    def get_queryset(self):
        queryset = Production.objects.all().order_by('id_production')
        return queryset

