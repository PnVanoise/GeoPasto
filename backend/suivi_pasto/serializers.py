import re

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from suivi_pasto.models import Logement, Commodite
from suivi_pasto.models import (
    UnitePastorale,
    GeometrieUnitePastorale,
    ProprietaireFoncier,
    QuartierPasto,
    ProprietaireUnitePastorale,
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
from suivi_pasto.models import Ruche, Berger, GardeSituation
from suivi_pasto.models import TypeEvenement, Evenement, Visite
from suivi_pasto.models import TypeEquipement, EquipementAlpage, EquipementExploitant
from suivi_pasto.models import (
    Production,
    CategoriePension,
    Race,
    CategorieAnimaux,
    Espece,
    Cheptel,
)


AUDIT_FIELD_NAMES = (
    "created_by",
    "created_on",
    "modified_by",
    "modified_on",
)


class AuditReadOnlyFieldsMixin:
    """Expose and lock audit fields when they exist on the model."""

    def get_fields(self):
        fields = super().get_fields()
        model = getattr(getattr(self, "Meta", None), "model", None)
        if model is None:
            return fields

        model_field_names = {field.name for field in model._meta.concrete_fields}
        for field_name in AUDIT_FIELD_NAMES:
            if field_name not in model_field_names:
                continue
            if field_name in fields:
                fields[field_name].read_only = True
            else:
                fields[field_name] = serializers.ReadOnlyField()

        return fields


# Bloc administratif (orange)
class UnitePastoraleSerializer(AuditReadOnlyFieldsMixin, GeoFeatureModelSerializer):
    proprios = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    proprios_ids = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UnitePastorale
        geo_field = "geom_active"
        fields = [
            "id_unite_pastorale",
            "code_up",
            "nom_up",
            "geom_active",
            "secteur",
            "active",
            "proprios",
            "proprios_ids",
        ]

    def to_representation(self, instance):
        if hasattr(instance, "geom_4326") and instance.geom_4326 is not None:
            instance.geom_active = instance.geom_4326
        else:
            geom = getattr(instance, "geom_active", None)
            if geom is not None:
                try:
                    geom.transform(4326)
                except Exception:
                    pass

        return super().to_representation(instance)

    def to_internal_value(self, data):
        # on mappe les clés id et id_unite_pastorale à la clé properties.id_unite_pastorale
        # assure la compatibilité avec le format GeoJson
        data = dict(data)
        props = dict(data.get("properties") or {})

        # Map top-level "id" -> properties.id_unite_pastorale if missing
        if "id" in data and "id_unite_pastorale" not in props:
            props["id_unite_pastorale"] = data["id"]

        # Map top-level "id_unite_pastorale" -> properties.id_unite_pastorale if missing
        if "id_unite_pastorale" in data and "id_unite_pastorale" not in props:
            props["id_unite_pastorale"] = data["id_unite_pastorale"]

        data["properties"] = props
        return super().to_internal_value(data)

    def get_proprios_ids(self, obj):
        return [p.proprietaire_id for p in obj.proprietaires_unite_pastorale.all()]

    def create(self, validated_data):
        proprios_data = validated_data.pop("proprios", [])
        up = UnitePastorale.objects.create(**validated_data)
        for proprio_id in proprios_data:
            proprio = ProprietaireFoncier.objects.get(id_proprietaire=proprio_id)
            ProprietaireUnitePastorale.objects.create(
                unite_pastorale=up, proprietaire=proprio
            )
        return up

    def update(self, instance, validated_data):
        proprios_data = validated_data.pop("proprios", [])

        with transaction.atomic():
            # Apply incoming validated fields to the instance before saving
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            instance.save()

            # Récupérer les IDs actuels des propriétaires de l'unité pastorale
            proprios_actuels = set(
                ProprietaireUnitePastorale.objects.filter(
                    unite_pastorale=instance
                ).values_list("proprietaire_id", flat=True)
            )
            nouveaux_proprios = set(proprios_data)

            # Supprimer les proprios qui ne sont plus associés
            proprios_a_supprimer = proprios_actuels - nouveaux_proprios
            for proprio_up in ProprietaireUnitePastorale.objects.filter(
                unite_pastorale=instance, proprietaire_id__in=proprios_a_supprimer
            ):
                proprio_up.delete()

            # Ajouter les nouveaux proprios
            proprios_a_ajouter = nouveaux_proprios - proprios_actuels
            for proprio_id in proprios_a_ajouter:
                propr = ProprietaireFoncier.objects.get(id_proprietaire=proprio_id)
                ProprietaireUnitePastorale.objects.create(
                    unite_pastorale=instance, proprietaire=propr
                )

        return instance


# light serializer, pour les listes
class UnitePastoraleLSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = UnitePastorale
        fields = ["id_unite_pastorale", "nom_up", "secteur"]


class GeometrieUnitePastoraleSerializer(
    AuditReadOnlyFieldsMixin, GeoFeatureModelSerializer
):
    class Meta:
        model = GeometrieUnitePastorale
        geo_field = "geometry"
        fields = [
            "id_geometrie_up",
            "unite_pastorale",
            "geometry",
            "date_debut_validite",
            "date_fin_validite",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        date_debut = attrs.get(
            "date_debut_validite", getattr(self.instance, "date_debut_validite", None)
        )
        date_fin = attrs.get(
            "date_fin_validite", getattr(self.instance, "date_fin_validite", None)
        )
        if date_debut and date_fin and date_debut > date_fin:
            raise serializers.ValidationError(
                {
                    "date_fin_validite": "La date de fin doit être postérieure à la date de début."
                }
            )
        return attrs

    def to_representation(self, instance):
        geom = getattr(instance, "geometry", None)
        if geom is not None:
            try:
                geom.transform(4326)
            except Exception:
                pass
        return super().to_representation(instance)


class ProprietaireFoncierSerializer(
    AuditReadOnlyFieldsMixin, serializers.ModelSerializer
):
    unites_pastorales = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = ProprietaireFoncier
        fields = [
            "id_proprietaire",
            "nom_propr",
            "prenom_propr",
            "tel_propr",
            "mail_propr",
            "adresse_propr",
            "commentaire",
            "unites_pastorales",
        ]


class ProprietaireUnitePastoraleSerializer(
    AuditReadOnlyFieldsMixin, serializers.ModelSerializer
):
    up_nom = serializers.CharField(source="unite_pastorale.nom_up", read_only=True)
    proprietaire_nom = serializers.SerializerMethodField()

    def get_proprietaire_nom(self, obj):
        if obj.proprietaire:
            prenom = obj.proprietaire.prenom_propr or ""
            return f"{obj.proprietaire.nom_propr} {prenom}".strip()
        return ""

    class Meta:
        model = ProprietaireUnitePastorale
        fields = [
            "id_proprietaire_up",
            "proprietaire",
            "unite_pastorale",
            "up_nom",
            "proprietaire_nom",
        ]


class QuartierPastoSerializer(AuditReadOnlyFieldsMixin, GeoFeatureModelSerializer):

    class Meta:
        model = QuartierPasto
        geo_field = "geometry"
        auto_bbox = True
        fields = [
            "id_quartier",
            "code_quartier",
            "nom_quartier",
            "geometry",
            "situation_exploitation",
        ]

    def to_internal_value(self, data):
        geometry = data.get("geometry", None)
        if geometry:
            geom_type = geometry.get("type")
            coords = geometry.get("coordinates")
            if geom_type in ("Polygon", "MultiPolygon") and not coords:
                data["geometry"] = None
        return super().to_internal_value(data)

    def to_representation(self, instance):
        if instance.geometry is not None:
            instance.geometry.transform(4326)

        data = super().to_representation(instance)

        if instance.geometry is None:
            data["geometry"] = {"type": "MultiPolygon", "coordinates": []}

        return data


# Bloc plans de suivi (bleu)
class TypeDeSuiviSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = TypeDeSuivi
        fields = ["id_type_suivi", "description"]


class PlanDeSuiviSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):
    unite_pastorale = serializers.PrimaryKeyRelatedField(
        queryset=UnitePastorale.objects.all(), allow_null=True
    )
    unite_pastorale_detail = UnitePastoraleLSerializer(
        source="unite_pastorale", read_only=True
    )
    type_suivi = serializers.PrimaryKeyRelatedField(
        queryset=TypeDeSuivi.objects.all(), allow_null=True
    )
    type_suivi_detail = TypeDeSuiviSerializer(source="type_suivi", read_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        date_debut = attrs.get("date_debut", getattr(self.instance, "date_debut", None))
        date_fin = attrs.get("date_fin", getattr(self.instance, "date_fin", None))
        if date_debut and date_fin and date_debut > date_fin:
            raise serializers.ValidationError(
                {"date_fin": "La date de fin doit être postérieure à la date de début."}
            )
        return attrs

    class Meta:
        model = PlanDeSuivi
        fields = [
            "id_plan_suivi",
            "description",
            "commentaire",
            "plan_de_gestion",
            "date_debut",
            "date_fin",
            "type_suivi",
            "type_suivi_detail",
            "unite_pastorale",
            "unite_pastorale_detail",
        ]


class TypeDeMesureSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):
    types_suivi = serializers.PrimaryKeyRelatedField(
        queryset=TypeDeSuivi.objects.all(), many=True, required=False
    )

    class Meta:
        model = TypeDeMesure
        fields = ["id_type_mesure", "description", "types_suivi"]


class EnjeuSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Enjeu
        fields = ["id_enjeu", "description"]


class MesureDePlanSerializer(AuditReadOnlyFieldsMixin, GeoFeatureModelSerializer):
    plan_suivi = serializers.PrimaryKeyRelatedField(
        queryset=PlanDeSuivi.objects.all(), allow_null=True
    )
    plan_suivi_detail = PlanDeSuiviSerializer(source="plan_suivi", read_only=True)
    unite_pastorale_detail = UnitePastoraleLSerializer(
        source="plan_suivi.unite_pastorale", read_only=True
    )
    type_mesure = serializers.PrimaryKeyRelatedField(
        queryset=TypeDeMesure.objects.all(),
        allow_null=True,
    )
    type_mesure_detail = TypeDeMesureSerializer(source="type_mesure", read_only=True)
    enjeu_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    enjeux = serializers.SerializerMethodField()

    class Meta:
        model = MesureDePlan
        geo_field = "geometry"
        fields = [
            "id_mesure_plan",
            "code",
            "description",
            "commentaire",
            "date_debut_validite",
            "date_fin_validite",
            "debut_periode_realisation",
            "fin_periode_realisation",
            "type_mesure",
            "type_mesure_detail",
            "plan_suivi",
            "plan_suivi_detail",
            "unite_pastorale_detail",
            "geometry",
            "obligation",
            "enjeu_ids",
            "enjeux",
        ]

    def get_enjeux(self, obj):
        return [
            {"id": e.id_enjeu, "description": e.description} for e in obj.enjeux.all()
        ]

    @staticmethod
    def _validate_periode_mm_jj(value, field_name):
        import re

        if value and not re.match(r"^\d{2}-\d{2}$", value):
            raise serializers.ValidationError(
                {field_name: "Format attendu : MM-JJ (ex: 07-15)."}
            )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        debut = attrs.get(
            "date_debut_validite", getattr(self.instance, "date_debut_validite", None)
        )
        fin = attrs.get(
            "date_fin_validite", getattr(self.instance, "date_fin_validite", None)
        )
        if debut and fin and debut > fin:
            raise serializers.ValidationError(
                {
                    "date_fin_validite": "La fin de validité doit être postérieure au début de validité."
                }
            )
        debut_r = attrs.get("debut_periode_realisation")
        fin_r = attrs.get("fin_periode_realisation")
        self._validate_periode_mm_jj(debut_r, "debut_periode_realisation")
        self._validate_periode_mm_jj(fin_r, "fin_periode_realisation")
        if debut_r and fin_r and fin_r < debut_r:
            raise serializers.ValidationError(
                {
                    "fin_periode_realisation": "La fin de période de réalisation doit être postérieure au début."
                }
            )
        return attrs

    def create(self, validated_data):
        enjeu_ids = validated_data.pop("enjeu_ids", [])
        instance = super().create(validated_data)
        if enjeu_ids:
            instance.enjeux.set(enjeu_ids)
        return instance

    def update(self, instance, validated_data):
        enjeu_ids = validated_data.pop("enjeu_ids", None)
        instance = super().update(instance, validated_data)
        if enjeu_ids is not None:
            instance.enjeux.set(enjeu_ids)
        return instance

    def to_representation(self, instance):
        if instance.geometry is not None:
            instance.geometry.transform(4326)
        return super().to_representation(instance)


class MesureDePlanSimpleSerializer(
    AuditReadOnlyFieldsMixin, serializers.ModelSerializer
):
    type_mesure_detail = TypeDeMesureSerializer(source="type_mesure", read_only=True)

    class Meta:
        model = MesureDePlan
        fields = [
            "id_mesure_plan",
            "code",
            "description",
            "commentaire",
            "date_debut_validite",
            "date_fin_validite",
            "debut_periode_realisation",
            "fin_periode_realisation",
            "type_mesure",
            "type_mesure_detail",
            "plan_suivi",
            "obligation",
        ]


class RealisationMesureSerializer(
    AuditReadOnlyFieldsMixin, serializers.ModelSerializer
):
    mesure_plan = serializers.PrimaryKeyRelatedField(
        queryset=MesureDePlan.objects.all()
    )
    situation = serializers.PrimaryKeyRelatedField(
        queryset=SituationDExploitation.objects.all()
    )
    mesure_plan_detail = MesureDePlanSimpleSerializer(
        source="mesure_plan", read_only=True
    )

    class Meta:
        model = RealisationMesure
        fields = [
            "id_realisation_mesure",
            "mesure_plan",
            "mesure_plan_detail",
            "situation",
            "statut",
            "commentaire",
            "date_realisation",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        mesure = attrs.get("mesure_plan", getattr(self.instance, "mesure_plan", None))
        situation = attrs.get("situation", getattr(self.instance, "situation", None))
        if mesure and situation:
            md = mesure.date_debut_validite
            mf = mesure.date_fin_validite
            sd = situation.date_debut
            sf = situation.date_fin
            if md and sf and md > sf:
                raise serializers.ValidationError(
                    "Cette mesure n'est pas applicable sur la période de cette situation."
                )
            if mf and sd and mf < sd:
                raise serializers.ValidationError(
                    "Cette mesure n'est pas applicable sur la période de cette situation."
                )
        return attrs


# Bloc expoitation
class TypeConventionSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = TypeConvention
        fields = ["id_type_convention", "description"]


class ConventionDExploitationSerializer(
    AuditReadOnlyFieldsMixin, GeoFeatureModelSerializer
):
    type_convention = serializers.PrimaryKeyRelatedField(
        queryset=TypeConvention.objects.all(), allow_null=True
    )
    type_convention_detail = TypeConventionSerializer(
        source="type_convention", read_only=True
    )

    exploitant_nom = serializers.CharField(
        source="exploitant.nom_exploitant", read_only=True
    )
    up_nom = serializers.CharField(source="unite_pastorale.nom_up", read_only=True)

    class Meta:
        model = ConventionDExploitation
        geo_field = "geometry"
        auto_bbox = True
        fields = "__all__"

    def validate(self, attrs):
        attrs = super().validate(attrs)

        date_debut = attrs.get("date_debut", getattr(self.instance, "date_debut", None))
        date_fin = attrs.get("date_fin", getattr(self.instance, "date_fin", None))
        if date_debut and date_fin and date_debut > date_fin:
            raise serializers.ValidationError(
                {"date_fin": "La date de fin doit être postérieure à la date de début."}
            )

        _MM_DD_RE = re.compile(r"^\d{2}-\d{2}$")
        debut_expl = attrs.get(
            "debut_periode_expl", getattr(self.instance, "debut_periode_expl", None)
        )
        fin_expl = attrs.get(
            "fin_periode_expl", getattr(self.instance, "fin_periode_expl", None)
        )
        for field, val in [
            ("debut_periode_expl", debut_expl),
            ("fin_periode_expl", fin_expl),
        ]:
            if val and not _MM_DD_RE.match(val):
                raise serializers.ValidationError(
                    {field: "Format attendu : MM-JJ (ex: 06-15)."}
                )
        if debut_expl and fin_expl and debut_expl > fin_expl:
            raise serializers.ValidationError(
                {
                    "fin_periode_expl": "La fin de période doit être postérieure au début de période."
                }
            )

        return attrs

    def to_representation(self, instance):
        if instance.geometry is not None:
            instance.geometry.transform(4326)
        return super().to_representation(instance)


class SituationDExploitationSerializer(
    AuditReadOnlyFieldsMixin, serializers.ModelSerializer
):

    unite_pastorale = serializers.PrimaryKeyRelatedField(
        queryset=UnitePastorale.objects.all(),
        allow_null=True,
    )
    unite_pastorale_detail = UnitePastoraleLSerializer(
        source="unite_pastorale",
        read_only=True,
    )

    exploitant_nom = serializers.SerializerMethodField()

    def get_exploitant_nom(self, obj):
        return obj.exploitant.nom_exploitant if obj.exploitant else None

    def to_internal_value(self, data):
        # Accept frontend payloads that send `id` instead of `id_situation`.
        data = dict(data)
        if "id" in data and "id_situation" not in data:
            data["id_situation"] = data["id"]
        return super().to_internal_value(data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        date_debut = attrs.get("date_debut", getattr(self.instance, "date_debut", None))
        date_fin = attrs.get("date_fin", getattr(self.instance, "date_fin", None))
        if date_debut and date_fin and date_debut > date_fin:
            raise serializers.ValidationError(
                {"date_fin": "La date de fin doit être postérieure à la date de début."}
            )
        return attrs

    class Meta:
        model = SituationDExploitation
        fields = [
            "id_situation",
            "nom_situation",
            "date_debut",
            "date_fin",
            "exploitant",
            "exploitant_nom",
            "unite_pastorale",
            "unite_pastorale_detail",
            "sans_gardiennage",
        ]


class ExploiterSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):

    nombre_animaux = serializers.IntegerField(
        required=False, allow_null=True, min_value=0
    )
    quartier_nom = serializers.CharField(source="quartier.nom_quartier", read_only=True)
    situation_exploitation = serializers.SerializerMethodField(read_only=True)
    cheptel_nom = serializers.SerializerMethodField(read_only=True)
    cheptel_nombre_animaux = serializers.SerializerMethodField(read_only=True)
    tous_troupeaux = serializers.SerializerMethodField(read_only=True)

    def get_cheptel_nom(self, obj):
        if obj.cheptel_id is None:
            return "Tous les troupeaux"

        if getattr(obj.cheptel, "description", None):
            return obj.cheptel.description

        return f"Troupeau #{obj.cheptel_id}"

    def get_tous_troupeaux(self, obj):
        return obj.cheptel_id is None

    def get_cheptel_nombre_animaux(self, obj):
        if obj.cheptel_id is None:
            return None
        return getattr(obj.cheptel, "nombre_animaux", None)

    def get_situation_exploitation(self, obj):
        if obj.cheptel_id and getattr(obj.cheptel, "situation_exploitation_id", None):
            return obj.cheptel.situation_exploitation_id
        if obj.quartier_id and getattr(obj.quartier, "situation_exploitation_id", None):
            return obj.quartier.situation_exploitation_id
        return None

    def validate(self, attrs):
        attrs = super().validate(attrs)

        date_debut = attrs.get("date_debut", getattr(self.instance, "date_debut", None))
        date_fin = attrs.get("date_fin", getattr(self.instance, "date_fin", None))
        if date_debut and date_fin and date_debut > date_fin:
            raise serializers.ValidationError(
                {"date_fin": "La date de fin doit être postérieure à la date de début."}
            )

        # Cohérence avec la situation parente (dérivée du cheptel ou du quartier)
        cheptel_obj = attrs.get("cheptel", getattr(self.instance, "cheptel", None))
        quartier_obj = attrs.get("quartier", getattr(self.instance, "quartier", None))
        situation = None
        try:
            if cheptel_obj is not None:
                situation = cheptel_obj.situation_exploitation
            elif quartier_obj is not None:
                situation = quartier_obj.situation_exploitation
        except Exception:
            pass
        if situation:
            errors = {}
            situ_debut = situation.date_debut
            situ_fin = situation.date_fin
            if situ_debut and date_debut and date_debut < situ_debut:
                errors["date_debut"] = (
                    f"Date antérieure au début de la situation ({situ_debut})."
                )
            elif situ_fin and date_debut and date_debut > situ_fin:
                errors["date_debut"] = (
                    f"Date postérieure à la fin de la situation ({situ_fin})."
                )
            if situ_debut and date_fin and date_fin < situ_debut:
                errors["date_fin"] = (
                    f"Date antérieure au début de la situation ({situ_debut})."
                )
            elif situ_fin and date_fin and date_fin > situ_fin:
                errors["date_fin"] = (
                    f"Date postérieure à la fin de la situation ({situ_fin})."
                )
            if errors:
                raise serializers.ValidationError(errors)

        if "nombre_animaux" not in attrs and self.instance is not None:
            return attrs

        declared_animaux = attrs.get("nombre_animaux", None)
        if declared_animaux is None:
            return attrs

        cheptel = attrs.get("cheptel", getattr(self.instance, "cheptel", None))
        quartier = attrs.get("quartier", getattr(self.instance, "quartier", None))

        if cheptel is not None:
            max_animaux = getattr(cheptel, "nombre_animaux", 0) or 0
        else:
            situation_id = getattr(quartier, "situation_exploitation_id", None)
            if not situation_id:
                raise serializers.ValidationError(
                    {
                        "nombre_animaux": (
                            "Impossible de valider nombre_animaux sans cheptel: "
                            "le quartier doit être renseigné et lié à une situation."
                        )
                    }
                )

            max_animaux = (
                Cheptel.objects.filter(situation_exploitation_id=situation_id)
                .aggregate(total=Sum("nombre_animaux"))
                .get("total")
                or 0
            )

        if declared_animaux > max_animaux:
            raise serializers.ValidationError(
                {"nombre_animaux": (f"La valeur maximale autorisée est {max_animaux}.")}
            )

        return attrs

    class Meta:
        model = Exploiter
        fields = [
            "id_exploiter",
            "date_debut",
            "date_fin",
            "quartier",
            "cheptel",
            "nombre_animaux",
            "commentaire",
            "quartier_nom",
            "cheptel_nom",
            "cheptel_nombre_animaux",
            "tous_troupeaux",
            "situation_exploitation",
        ]


class EleveurSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):

    nom_complet = serializers.SerializerMethodField()

    class Meta:
        model = Eleveur
        read_only_fields = ["id_eleveur"]
        fields = [
            "id_eleveur",
            "nom_eleveur",
            "prenom_eleveur",
            "adresse_eleveur",
            "tel_eleveur",
            "mail_eleveur",
            "commentaire",
            "nom_complet",
        ]

    def get_nom_complet(self, obj):
        nom = (obj.nom_eleveur or "").upper()
        prenom = obj.prenom_eleveur or ""
        return f"{nom} {prenom}".strip()


class TypeDExploitantSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = TypeDExploitant
        fields = ["id_type_exploitant", "description"]


class ExploitantSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):
    membres = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    membres_ids = serializers.SerializerMethodField(read_only=True)
    membres_exploitants = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    membres_exploitants_ids = serializers.SerializerMethodField(read_only=True)

    type_exploitant = serializers.PrimaryKeyRelatedField(
        queryset=TypeDExploitant.objects.all(), allow_null=True
    )
    type_exploitant_detail = TypeDExploitantSerializer(
        source="type_exploitant", read_only=True
    )

    president = serializers.PrimaryKeyRelatedField(
        queryset=Eleveur.objects.all(), allow_null=True
    )

    class Meta:
        model = Exploitant
        read_only_fields = ["id_exploitant"]
        fields = [
            "id_exploitant",
            "nom_exploitant",
            "president",
            "membres",
            "membres_ids",
            "membres_exploitants",
            "membres_exploitants_ids",
            "type_exploitant",
            "type_exploitant_detail",
        ]

    def get_membres_ids(self, obj):
        return list(
            EtreCompose.objects.filter(
                exploitant=obj, eleveur__isnull=False
            ).values_list("eleveur_id", flat=True)
        )

    def get_membres_exploitants_ids(self, obj):
        return list(
            EtreCompose.objects.filter(
                exploitant=obj, exploitant_membre__isnull=False
            ).values_list("exploitant_membre_id", flat=True)
        )

    def validate(self, attrs):
        membres_exploitants = attrs.get("membres_exploitants", [])
        instance_id = self.instance.id_exploitant if self.instance else None

        if instance_id and instance_id in membres_exploitants:
            raise serializers.ValidationError(
                {
                    "membres_exploitants": "Un alpagiste ne peut pas être membre de lui-même."
                }
            )

        if instance_id and membres_exploitants:
            # Détection de cycle : vérifier que self n'apparaît pas dans la
            # fermeture transitive des ancêtres des membres-exploitants proposés.
            ancetres = set()
            a_visiter = list(membres_exploitants)
            while a_visiter:
                courant = a_visiter.pop()
                if courant in ancetres:
                    continue
                ancetres.add(courant)
                parents = EtreCompose.objects.filter(
                    exploitant_membre_id=courant
                ).values_list("exploitant_id", flat=True)
                for parent_id in parents:
                    if parent_id and parent_id not in ancetres:
                        a_visiter.append(parent_id)
            if instance_id in ancetres:
                raise serializers.ValidationError(
                    {
                        "membres_exploitants": (
                            "Cycle détecté : cet alpagiste est déjà (directement ou "
                            "indirectement) membre de l'un des alpagistes sélectionnés."
                        )
                    }
                )

        return attrs

    def _sync_membres(self, exploitant, membres_eleveurs, membres_exploitants):
        actuels_eleveurs = set(
            EtreCompose.objects.filter(
                exploitant=exploitant, eleveur__isnull=False
            ).values_list("eleveur_id", flat=True)
        )
        nouveaux_eleveurs = set(membres_eleveurs)
        a_supprimer = actuels_eleveurs - nouveaux_eleveurs
        if a_supprimer:
            EtreCompose.objects.filter(
                exploitant=exploitant, eleveur_id__in=a_supprimer
            ).delete()
        for eleveur_id in nouveaux_eleveurs - actuels_eleveurs:
            EtreCompose.objects.create(exploitant=exploitant, eleveur_id=eleveur_id)

        actuels_expl = set(
            EtreCompose.objects.filter(
                exploitant=exploitant, exploitant_membre__isnull=False
            ).values_list("exploitant_membre_id", flat=True)
        )
        nouveaux_expl = set(membres_exploitants)
        a_supprimer_expl = actuels_expl - nouveaux_expl
        if a_supprimer_expl:
            EtreCompose.objects.filter(
                exploitant=exploitant, exploitant_membre_id__in=a_supprimer_expl
            ).delete()
        for expl_id in nouveaux_expl - actuels_expl:
            EtreCompose.objects.create(
                exploitant=exploitant, exploitant_membre_id=expl_id
            )

    def create(self, validated_data):
        membres_eleveurs = validated_data.pop("membres", [])
        membres_exploitants = validated_data.pop("membres_exploitants", [])
        with transaction.atomic():
            exploitant = Exploitant.objects.create(**validated_data)
            self._sync_membres(exploitant, membres_eleveurs, membres_exploitants)
        return exploitant

    def update(self, instance, validated_data):
        membres_eleveurs = validated_data.pop("membres", None)
        membres_exploitants = validated_data.pop("membres_exploitants", None)
        instance.nom_exploitant = validated_data.get(
            "nom_exploitant", instance.nom_exploitant
        )
        instance.president = validated_data.get("president", instance.president)
        instance.type_exploitant = validated_data.get(
            "type_exploitant", instance.type_exploitant
        )

        with transaction.atomic():
            instance.save()
            if membres_eleveurs is None and membres_exploitants is None:
                return instance
            current_eleveurs = (
                membres_eleveurs
                if membres_eleveurs is not None
                else list(
                    EtreCompose.objects.filter(
                        exploitant=instance, eleveur__isnull=False
                    ).values_list("eleveur_id", flat=True)
                )
            )
            current_exploitants = (
                membres_exploitants
                if membres_exploitants is not None
                else list(
                    EtreCompose.objects.filter(
                        exploitant=instance, exploitant_membre__isnull=False
                    ).values_list("exploitant_membre_id", flat=True)
                )
            )
            self._sync_membres(instance, current_eleveurs, current_exploitants)

        return instance


class EtreComposeSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = EtreCompose
        fields = ["id_etre_compose", "exploitant", "eleveur", "exploitant_membre"]


class SubventionPNVSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):

    exploitant = serializers.PrimaryKeyRelatedField(
        queryset=Exploitant.objects.all(), allow_null=True
    )
    exploitant_detail = ExploitantSerializer(
        source="exploitant",
        read_only=True,
    )

    class Meta:
        model = SubventionPNV
        fields = [
            "id_subvention",
            "commentaire",
            "montant",
            "engage",
            "paye",
            "exploitant",
            "exploitant_detail",
        ]


class LogementSerializer(AuditReadOnlyFieldsMixin, GeoFeatureModelSerializer):
    unite_pastorale = serializers.PrimaryKeyRelatedField(
        queryset=UnitePastorale.objects.all(), allow_null=True
    )
    unite_pastorale_detail = UnitePastoraleLSerializer(
        source="unite_pastorale",
        read_only=True,
    )

    class Meta:
        model = Logement
        geo_field = "geom"
        auto_bbox = True
        fields = "__all__"

    def to_representation(self, instance):
        if instance.geom != None:
            instance.geom.transform(4326)

        return super().to_representation(instance)


class CommoditeSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = Commodite
        fields = ["id_commodite", "description"]


class AbriDUrgenceSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = AbriDUrgence
        fields = [
            "id_abri_urgence",
            "description",
            "etat",
            "commentaire",
            "created_by",
            "created_on",
            "modified_by",
            "modified_on",
        ]
        read_only_fields = ["created_by", "created_on", "modified_by", "modified_on"]


class AbriDUrgenceCommoditeSerializer(
    AuditReadOnlyFieldsMixin, serializers.ModelSerializer
):
    abri_urgence_description = serializers.CharField(
        source="abri_urgence.description", read_only=True
    )
    commodite_desc = serializers.CharField(
        source="commodite.description", read_only=True
    )

    class Meta:
        model = AbriDUrgenceCommodite
        fields = [
            "id_abri_urgence_commodite",
            "abri_urgence",
            "commodite",
            "etat",
            "commentaire",
            "quantite",
            "abri_urgence_description",
            "commodite_desc",
        ]


class BeneficierDeSerializer(AuditReadOnlyFieldsMixin, GeoFeatureModelSerializer):

    exploitant_nom = (
        serializers.SerializerMethodField()
    )  # CharField(source='exploitant.nom_exploitant', read_only=True)
    abri_description = (
        serializers.SerializerMethodField()
    )  # CharField(source='abri_urgence.description', read_only=True)

    def get_exploitant_nom(self, obj):
        return obj.exploitant.nom_exploitant if obj.exploitant else None

    def get_abri_description(self, obj):
        return obj.abri_urgence.description if obj.abri_urgence else None

    class Meta:
        model = BeneficierDe
        geo_field = "geometry"
        auto_bbox = True
        fields = [
            "id_beneficier_de",
            "exploitant",
            "abri_urgence",
            "date_debut",
            "date_fin",
            "geometry",
            "exploitant_nom",
            "abri_description",
        ]

    def to_internal_value(self, data):
        geometry = data.get("geometry", None)
        if (
            geometry
            and geometry.get("type") == "Point"
            and not geometry.get("coordinates")
        ):
            data["geometry"] = None
        return super().to_internal_value(data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        date_debut = attrs.get("date_debut", getattr(self.instance, "date_debut", None))
        date_fin = attrs.get("date_fin", getattr(self.instance, "date_fin", None))
        if date_debut and date_fin and date_debut > date_fin:
            raise serializers.ValidationError(
                {"date_fin": "La date de fin doit être postérieure à la date de début."}
            )
        return attrs

    def to_representation(self, instance):
        if instance.geometry is not None:
            instance.geometry.transform(4326)
        return super().to_representation(instance)


# Ruche / Berger / Cheptel
class RucheSerializer(AuditReadOnlyFieldsMixin, GeoFeatureModelSerializer):

    class Meta:
        model = Ruche
        geo_field = "geometry"
        auto_bbox = True
        fields = "__all__"

    def to_representation(self, instance):
        if instance.geometry != None:
            instance.geometry.transform(4326)

        return super().to_representation(instance)


class BergerSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = Berger
        fields = [
            "id_berger",
            "nom_berger",
            "prenom_berger",
            "adresse_berger",
            "tel_berger",
            "commentaire",
        ]


class GardeSituationSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):

    berger_nom = serializers.CharField(source="berger.nom_berger", read_only=True)
    berger_prenom = serializers.CharField(source="berger.prenom_berger", read_only=True)
    situation_nom = serializers.CharField(
        source="situation_exploitation.nom_situation", read_only=True
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        date_debut = attrs.get("date_debut", getattr(self.instance, "date_debut", None))
        date_fin = attrs.get("date_fin", getattr(self.instance, "date_fin", None))
        if date_debut and date_fin and date_debut > date_fin:
            raise serializers.ValidationError(
                {"date_fin": "La date de fin doit être postérieure à la date de début."}
            )
        situation = attrs.get(
            "situation_exploitation",
            (
                getattr(self.instance, "situation_exploitation", None)
                if self.instance
                else None
            ),
        )
        if situation:
            errors = {}
            situ_debut = situation.date_debut
            situ_fin = situation.date_fin
            if situ_debut and date_debut and date_debut < situ_debut:
                errors["date_debut"] = (
                    f"Date antérieure au début de la situation ({situ_debut})."
                )
            elif situ_fin and date_debut and date_debut > situ_fin:
                errors["date_debut"] = (
                    f"Date postérieure à la fin de la situation ({situ_fin})."
                )
            if situ_debut and date_fin and date_fin < situ_debut:
                errors["date_fin"] = (
                    f"Date antérieure au début de la situation ({situ_debut})."
                )
            elif situ_fin and date_fin and date_fin > situ_fin:
                errors["date_fin"] = (
                    f"Date postérieure à la fin de la situation ({situ_fin})."
                )
            if errors:
                raise serializers.ValidationError(errors)
        return attrs

    class Meta:
        model = GardeSituation
        fields = [
            "id_garde_situation",
            "date_debut",
            "date_fin",
            "commentaire",
            "situation_exploitation",
            "berger",
            "situation_nom",
            "berger_nom",
            "berger_prenom",
        ]


##################
# Mise à jour Cheptels / types de cheptel
# le 9/2/26
class ProductionSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):
    """
    Production
    """

    class Meta:
        model = Production
        fields = ["id_production", "description"]


class CategoriePensionSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):
    """
    Catégorie de pension
    """

    class Meta:
        model = CategoriePension
        fields = ["id_categorie_pension", "description"]


class EspeceSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):
    """
    Espèce
    """

    class Meta:
        model = Espece
        fields = ["id_espece", "description"]


class RaceSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):
    """
    Race
    """

    espece_description = serializers.CharField(
        source="espece.description", read_only=True
    )

    class Meta:
        model = Race
        fields = ["id_race", "description", "espece", "espece_description"]


class CategorieAnimauxSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):
    """
    Catégorie d'animaux
    """

    espece_description = serializers.CharField(
        source="espece.description", read_only=True
    )

    class Meta:
        model = CategorieAnimaux
        fields = [
            "id_categorie_animaux",
            "description",
            "coefficient_UGB",
            "espece",
            "espece_description",
        ]


class CheptelSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):
    """
    Cheptel
    """

    # Année
    annee = serializers.SerializerMethodField()

    # Eleveur
    eleveur = serializers.PrimaryKeyRelatedField(
        queryset=Eleveur.objects.all(),
        allow_null=True,
        required=False,
    )
    eleveur_detail = EleveurSerializer(
        source="eleveur",
        read_only=True,
    )

    # Exploitant propriétaire (alternative à eleveur)
    exploitant_proprietaire = serializers.PrimaryKeyRelatedField(
        queryset=Exploitant.objects.all(),
        allow_null=True,
        required=False,
    )
    exploitant_proprietaire_detail = serializers.SerializerMethodField(read_only=True)
    proprietaire_label = serializers.SerializerMethodField(read_only=True)

    # Situation d'exploitation
    situation_exploitation = serializers.PrimaryKeyRelatedField(
        queryset=SituationDExploitation.objects.all(),
        allow_null=True,
    )
    situation_detail = SituationDExploitationSerializer(
        source="situation_exploitation", read_only=True
    )

    # Production
    production = serializers.PrimaryKeyRelatedField(
        queryset=Production.objects.all(),
        allow_null=True,
    )
    production_detail = ProductionSerializer(source="production", read_only=True)

    # Catégorie de pension
    pension = serializers.PrimaryKeyRelatedField(
        queryset=CategoriePension.objects.all(),
        allow_null=True,
    )
    pension_detail = CategoriePensionSerializer(source="pension", read_only=True)

    # Race
    race = serializers.PrimaryKeyRelatedField(
        queryset=Race.objects.all(),
        allow_null=True,
    )
    race_detail = RaceSerializer(source="race", read_only=True)

    # Catégorie d'animaux
    categorie_animaux = serializers.PrimaryKeyRelatedField(
        queryset=CategorieAnimaux.objects.all(),
        allow_null=True,
    )
    categorie_animaux_detail = CategorieAnimauxSerializer(
        source="categorie_animaux", read_only=True
    )

    class Meta:
        model = Cheptel
        fields = [
            "id_cheptel",
            "date_debut",
            "annee",
            "date_fin",
            "nombre_animaux",
            "nombre_animaux_exact",
            "eleveur",
            "eleveur_detail",
            "exploitant_proprietaire",
            "exploitant_proprietaire_detail",
            "proprietaire_label",
            "situation_exploitation",
            "situation_detail",
            "description",
            "commentaire",
            "coefficient_UGB",
            "production",
            "production_detail",
            "pension",
            "pension_detail",
            "race",
            "race_detail",
            "categorie_animaux",
            "categorie_animaux_detail",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        date_debut = attrs.get("date_debut", getattr(self.instance, "date_debut", None))
        date_fin = attrs.get("date_fin", getattr(self.instance, "date_fin", None))
        if date_debut and date_fin and date_debut > date_fin:
            raise serializers.ValidationError(
                {"date_fin": "La date de fin doit être postérieure à la date de début."}
            )
        situation = attrs.get(
            "situation_exploitation",
            (
                getattr(self.instance, "situation_exploitation", None)
                if self.instance
                else None
            ),
        )
        if situation:
            errors = {}
            situ_debut = situation.date_debut
            situ_fin = situation.date_fin
            if situ_debut and date_debut and date_debut < situ_debut:
                errors["date_debut"] = (
                    f"Date antérieure au début de la situation ({situ_debut})."
                )
            elif situ_fin and date_debut and date_debut > situ_fin:
                errors["date_debut"] = (
                    f"Date postérieure à la fin de la situation ({situ_fin})."
                )
            if situ_debut and date_fin and date_fin < situ_debut:
                errors["date_fin"] = (
                    f"Date antérieure au début de la situation ({situ_debut})."
                )
            elif situ_fin and date_fin and date_fin > situ_fin:
                errors["date_fin"] = (
                    f"Date postérieure à la fin de la situation ({situ_fin})."
                )
            if errors:
                raise serializers.ValidationError(errors)
        eleveur = attrs.get(
            "eleveur",
            getattr(self.instance, "eleveur", None) if self.instance else None,
        )
        exploitant_proprietaire = attrs.get(
            "exploitant_proprietaire",
            (
                getattr(self.instance, "exploitant_proprietaire", None)
                if self.instance
                else None
            ),
        )
        if eleveur and exploitant_proprietaire:
            raise serializers.ValidationError(
                {
                    "exploitant_proprietaire": (
                        "Le propriétaire doit être soit un éleveur, soit un alpagiste, "
                        "mais pas les deux."
                    )
                }
            )
        if not eleveur and not exploitant_proprietaire:
            raise serializers.ValidationError(
                {"eleveur": "Un propriétaire (éleveur ou alpagiste) est obligatoire."}
            )
        return attrs

    def get_annee(self, obj):
        if obj.date_debut:
            return obj.date_debut.year
        return None

    def get_exploitant_proprietaire_detail(self, obj):
        if not obj.exploitant_proprietaire_id:
            return None
        expl = obj.exploitant_proprietaire
        return {
            "id_exploitant": expl.id_exploitant,
            "nom_exploitant": expl.nom_exploitant,
        }

    def get_proprietaire_label(self, obj):
        if obj.eleveur_id:
            nom = (obj.eleveur.nom_eleveur or "").upper()
            prenom = obj.eleveur.prenom_eleveur or ""
            return f"{nom} {prenom}".strip()
        if obj.exploitant_proprietaire_id:
            return obj.exploitant_proprietaire.nom_exploitant or ""
        return ""


# FIN Mise à jour Cheptels / types de cheptel
##################


# Evenements
class TypeEvenementSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = TypeEvenement
        fields = [
            "id_type_evenement",
            "description",
            "created_by",
            "created_on",
            "modified_by",
            "modified_on",
        ]
        read_only_fields = ["created_by", "created_on", "modified_by", "modified_on"]


class EvenementSerializer(AuditReadOnlyFieldsMixin, GeoFeatureModelSerializer):
    type_evenement_label = serializers.SerializerMethodField()
    nom_situation = serializers.SerializerMethodField()

    class Meta:
        model = Evenement
        geo_field = "geometry"
        auto_bbox = True
        fields = "__all__"

    def get_type_evenement_label(self, obj):
        try:
            return obj.type_evenement.description if obj.type_evenement else None
        except Exception:
            return None

    def get_nom_situation(self, obj):
        try:
            return obj.situation.nom_situation if obj.situation else None
        except Exception:
            return None

    def to_representation(self, instance):
        if instance.geometry != None:
            instance.geometry.transform(4326)

        return super().to_representation(instance)


class TypeEquipementSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = TypeEquipement
        fields = [
            "id_type_equipement",
            "description",
            "categorie",
            "created_by",
            "created_on",
            "modified_by",
            "modified_on",
        ]
        read_only_fields = ["created_by", "created_on", "modified_by", "modified_on"]


class EquipementAlpageSerializer(AuditReadOnlyFieldsMixin, GeoFeatureModelSerializer):
    type_equipement = serializers.PrimaryKeyRelatedField(
        queryset=TypeEquipement.objects.filter(categorie__iexact="Alpage"),
        allow_null=True,
    )
    type_equipement_detail = TypeEquipementSerializer(
        source="type_equipement", read_only=True
    )
    unite_pastorale = serializers.PrimaryKeyRelatedField(
        queryset=UnitePastorale.objects.all(),
        allow_null=True,
    )
    unite_pastorale_detail = UnitePastoraleLSerializer(
        source="unite_pastorale", read_only=True
    )

    class Meta:
        model = EquipementAlpage
        geo_field = "geometry"
        auto_bbox = True
        fields = "__all__"

    def to_representation(self, instance):
        if instance.geometry != None:
            instance.geometry.transform(4326)

        return super().to_representation(instance)


class EquipementExploitantSerializer(
    AuditReadOnlyFieldsMixin, GeoFeatureModelSerializer
):
    type_equipement = serializers.PrimaryKeyRelatedField(
        queryset=TypeEquipement.objects.filter(categorie__iexact="Exploitant"),
        allow_null=True,
    )
    type_equipement_detail = TypeEquipementSerializer(
        source="type_equipement", read_only=True
    )
    situation_exploitation = serializers.PrimaryKeyRelatedField(
        queryset=SituationDExploitation.objects.all(),
        allow_null=True,
    )
    situation_exploitation_detail = serializers.SerializerMethodField()
    beneficier_de = serializers.PrimaryKeyRelatedField(
        queryset=BeneficierDe.objects.all(),
        allow_null=True,
        required=False,
    )
    beneficier_de_detail = serializers.SerializerMethodField()

    class Meta:
        model = EquipementExploitant
        geo_field = "geometry"
        auto_bbox = True
        fields = "__all__"

    def get_situation_exploitation_detail(self, obj):
        if not obj.situation_exploitation:
            return None
        return {
            "id_situation": obj.situation_exploitation.id_situation,
            "nom_situation": obj.situation_exploitation.nom_situation,
        }

    def get_beneficier_de_detail(self, obj):
        bd = obj.beneficier_de
        if not bd:
            return None
        return {
            "abri_urgence": bd.abri_urgence_id,
            "date_debut": bd.date_debut,
            "date_fin": bd.date_fin,
        }

    def to_representation(self, instance):
        if instance.geometry is not None:
            instance.geometry.transform(4326)
        return super().to_representation(instance)


class VisiteSerializer(AuditReadOnlyFieldsMixin, serializers.ModelSerializer):
    contact_alpagiste_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    contacts_alpagistes = serializers.SerializerMethodField()
    observateur_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    observateurs = serializers.SerializerMethodField()
    unite_pastorale_nom = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Visite
        fields = [
            "id_visite",
            "date_visite",
            "description",
            "commentaire",
            "unite_pastorale",
            "unite_pastorale_nom",
            "contact_alpagiste_ids",
            "contacts_alpagistes",
            "observateur_ids",
            "observateurs",
        ]

    def get_unite_pastorale_nom(self, obj):
        if obj.unite_pastorale_id:
            return obj.unite_pastorale.nom_up
        return None

    def get_contacts_alpagistes(self, obj):
        return [
            {
                "id": e.id_eleveur,
                "full_name": f"{e.nom_eleveur} {e.prenom_eleveur or ''}".strip(),
            }
            for e in obj.contacts_alpagistes.all()
        ]

    def get_observateurs(self, obj):
        return [
            {
                "id": u.id,
                "full_name": f"{u.first_name} {u.last_name}".strip() or u.username,
            }
            for u in obj.observateurs.all()
        ]

    def create(self, validated_data):
        alpagiste_ids = validated_data.pop("contact_alpagiste_ids", [])
        observateur_ids = validated_data.pop("observateur_ids", [])
        visite = Visite.objects.create(**validated_data)
        if alpagiste_ids:
            visite.contacts_alpagistes.set(alpagiste_ids)
        if observateur_ids:
            visite.observateurs.set(observateur_ids)
        return visite

    def update(self, instance, validated_data):
        alpagiste_ids = validated_data.pop("contact_alpagiste_ids", None)
        observateur_ids = validated_data.pop("observateur_ids", None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if alpagiste_ids is not None:
            instance.contacts_alpagistes.set(alpagiste_ids)
        if observateur_ids is not None:
            instance.observateurs.set(observateur_ids)
        return instance
