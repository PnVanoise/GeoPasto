from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import F, Q, Sum

from .choices_logement import LST_STATUT, LST_ACCES_FINAL, LST_PROPRIETE, LST_TYPE_LOGEMENT, LST_MULTIUSAGE, \
                              LST_ACTIVITE_LAITIERE, LST_ETAT_BATIMENT, LST_ACCUEIL_PUBLIC, LST_SURFACE_LOGEMENT, \
                              LST_WC, LST_ALIM_ELECTRIQUE, LST_ALIM_EAU, LST_ORIGINE_EAU, LST_QUALITE_EAU, \
                              LST_DISPO_EAU, LST_ASSAINISSEMENT, LST_CHAUFFE_EAU, LST_OUI_NON, LST_OUI_NON_INC


class AuditFieldsMixin(models.Model):
    """
    Champs de traçabilité réutilisables.
    """

    created_by = models.CharField(max_length=150, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified_by = models.CharField(max_length=150, null=True, blank=True)
    modified_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

# Bloc administratif (orange)
class UnitePastorale(AuditFieldsMixin, models.Model):
    """
    Unité pastorales
    """

    id_unite_pastorale = models.BigIntegerField(primary_key=True)  
    code_up = models.CharField(max_length=50, null=False, blank=False)
    nom_up = models.CharField(max_length=50, null=False, blank=False)
    annee_version = models. BigIntegerField(null=False, blank=False)
    geometry = models.MultiPolygonField(srid=2154, null=False, blank=False)
    version_active = models.BooleanField(null=False, blank=False)
    secteur = models.CharField(max_length=50, null=True, blank=True)
    # proprietaire = models.ForeignKey('alpages.ProprietaireFoncier', on_delete=models.SET_NULL, blank=True, null=True, related_name='unites_pastorales')
    
    def __str__(self):
        return str(self.nom_up)
    
class ProprietaireFoncier(AuditFieldsMixin, models.Model):
    """
    Proprétaire foncier
    """

    id_proprietaire = models.BigIntegerField(primary_key=True)  
    nom_propr = models.CharField(max_length=50, null=False, blank=False)
    prenom_propr = models.CharField(max_length=50, null=True, blank=True)
    tel_propr = models. CharField(max_length=30, null=True, blank=True)
    mail_propr = models.CharField(max_length=50, null=True, blank=True)
    adresse_propr = models.CharField(max_length=100, null=True, blank=True)
    commentaire = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return str(self.nom_propr)
    
class ProprietaireUnitePastorale(AuditFieldsMixin, models.Model):
    """
    Association Propriétaire foncier / Unité pastorale
    """
    
    proprietaire = models.ForeignKey('alpages.ProprietaireFoncier', on_delete=models.SET_NULL, blank=True, null=True, related_name='unites_pastorales_proprietaire')
    unite_pastorale = models.ForeignKey('alpages.UnitePastorale', on_delete=models.SET_NULL, blank=True, null=True, related_name='proprietaires_unite_pastorale')
    
    def __str__(self):
        return f"{self.proprietaire} est propriétaire de {self.unite_pastorale}"
    
class QuartierPasto(AuditFieldsMixin, models.Model):
    """
    Quartier d'alpage
    """

    id_quartier = models.BigIntegerField(primary_key=True)  
    code_quartier = models.CharField(max_length=50, null=True, blank=True)
    nom_quartier = models.CharField(max_length=50, null=True, blank=True)
    geometry = models.PolygonField(srid=2154, null=True, blank=True)

    situation_exploitation = models.ForeignKey(
        'alpages.SituationDExploitation',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='quartiers'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['situation_exploitation', 'code_quartier'],
                name='uniq_code_quartier_par_situation',
            ),
        ]
    
    def __str__(self):
        return str(self.nom_quartier)
    

# Bloc plans de suivi (bleu)
class TypeDeSuivi(AuditFieldsMixin, models.Model):
    """
    Type de Suivi
    """

    id_type_suivi = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    
    def __str__(self):
        return str(self.description)

class PlanDeSuivi(AuditFieldsMixin, models.Model):
    """
    Plan de Suivi
    """

    id_plan_suivi = models.BigIntegerField(primary_key=True)  
    description = models.CharField(max_length=50, null=False, blank=False)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    type_suivi = models.ForeignKey('alpages.TypeDeSuivi', on_delete=models.SET_NULL, blank=True, null=True, related_name='plans_de_suivi')
    unite_pastorale = models.ForeignKey('alpages.UnitePastorale', on_delete=models.SET_NULL, blank=True, null=True, related_name='plans_de_suivi')
    
    def __str__(self):
        return str(self.description)
    
# Type_de_mesure
class TypeDeMesure(AuditFieldsMixin, models.Model):
    """
    Type de mesure
    """

    id_type_mesure = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return str(self.description)


# Mesure_de_plan
class MesureDePlan(AuditFieldsMixin, models.Model):
    """
    Mesure de plan
    """

    id_mesure_plan = models.BigIntegerField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    commentaire = models.CharField(max_length=50, null=True, blank=True)
    debut_periode = models.DateField(null=True, blank=True)
    fin_periode = models.DateField(null=True, blank=True)
    # geometry = models.TextField(null=True, blank=True)
    type_mesure = models.ForeignKey('alpages.TypeDeMesure', on_delete=models.SET_NULL, blank=True, null=True, related_name='mesures_de_plan')
    plan_suivi = models.ForeignKey('alpages.PlanDeSuivi', on_delete=models.SET_NULL, blank=True, null=True, related_name='mesures_de_plan')

    def __str__(self):
        return str(self.description)


# Bloc exploitation
class TypeConvention(AuditFieldsMixin, models.Model):
    """
    Type de convention
    """
    
    id_type_convention = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return str(self.description)


class ConventionDExploitation(AuditFieldsMixin, models.Model):
    """
    Convention d'exploitation
    """
    
    id_convention = models.BigIntegerField(primary_key=True)
    surface_location = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    surface_exploitable = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    effectif_bovin = models.IntegerField(null=True, blank=True)
    effectif_ovin = models.IntegerField(null=True, blank=True)
    effectif_caprin = models.IntegerField(null=True, blank=True)
    effectif_porcin = models.IntegerField(null=True, blank=True)
    debut_periode_expl = models.DateField(null=True, blank=True)
    fin_periode_expl = models.DateField(null=True, blank=True)
    geometry = models.PolygonField(srid=2154, null=True, blank=True)
    unite_pastorale = models.ForeignKey('alpages.UnitePastorale', on_delete=models.SET_NULL, blank=True, null=True, related_name='conventions')
    exploitant = models.ForeignKey('alpages.Exploitant', on_delete=models.SET_NULL, blank=True, null=True, related_name='conventions')
    type_convention = models.ForeignKey('alpages.TypeConvention', on_delete=models.SET_NULL, blank=True, null=True, related_name='conventions')
    
    def __str__(self):
        return str(self.id_convention)
    

class SituationDExploitation(AuditFieldsMixin, models.Model):
    """
    Situation d'exploitation
    """
    
    id_situation = models.BigIntegerField(primary_key=True)
    annee = models.PositiveSmallIntegerField()
    nom_situation = models.CharField(max_length=150, null=False, blank=False)
    situation_active = models.BooleanField(null=False, blank=False)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)

    unite_pastorale = models.ForeignKey(
        'alpages.UnitePastorale',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='situations'
    )
    exploitant = models.ForeignKey(
        'alpages.Exploitant',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='situations'
    )
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['unite_pastorale', 'annee'],
                name='uniq_situation_up_annee'
            ),
            models.CheckConstraint(
                check=Q(date_fin__isnull=True) | Q(date_debut__lte=F("date_fin")),
                name='chk_situation_dates_coherentes',
            ),
        ]

    def __str__(self):
        return str(self.nom_situation)

# Exploiter = (#id_quartier, #id_situation, date_debut DATE, date_fin DATE, commmentaire VARCHAR(500));
class Exploiter(AuditFieldsMixin, models.Model):
    """
    Exploiter
    """
    
    id_exploiter = models.BigIntegerField(primary_key=True)

    cheptel = models.ForeignKey(
        'alpages.Cheptel',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='parcours'
    )
    quartier = models.ForeignKey(
        'alpages.QuartierPasto',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='parcours')
    
    date_debut = models.DateField()
    date_fin = models.DateField()
    nombre_animaux = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    mode_conduite = models.CharField(max_length=50, null=True, blank=True)
    commentaire = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(date_fin__isnull=True) | Q(date_debut__lte=F("date_fin")),
                name='chk_parcours_dates_coherentes',
            ),
            models.UniqueConstraint(
                fields=['cheptel', 'quartier', 'date_debut'],
                name='uniq_parcours_cheptel_quartier_debut',
            )
        ]

    def clean(self):
        # Cohérence métier: cheptel et quartier doivent être dans la même situation
        if (
            self.cheptel_id
            and self.quartier_id
            and self.cheptel.situation_exploitation_id
            != self.quartier.situation_exploitation_id
        ):
            raise ValidationError(
                "Le cheptel et le quartier doivent appartenir à la même situation."
            )

        if self.nombre_animaux is None:
            return

        if self.cheptel_id:
            max_animaux = getattr(self.cheptel, 'nombre_animaux', 0) or 0
        else:
            situation_id = None
            if self.quartier_id and getattr(self.quartier, 'situation_exploitation_id', None):
                situation_id = self.quartier.situation_exploitation_id

            if not situation_id:
                raise ValidationError({
                    'nombre_animaux': (
                        "Impossible de valider nombre_animaux sans cheptel: "
                        "le quartier doit être renseigné et lié à une situation."
                    )
                })

            max_animaux = (
                Cheptel.objects
                .filter(situation_exploitation_id=situation_id)
                .aggregate(total=Sum('nombre_animaux'))
                .get('total')
                or 0
            )

        if self.nombre_animaux > max_animaux:
            raise ValidationError({
                'nombre_animaux': (
                    f"nombre_animaux ({self.nombre_animaux}) dépasse le maximum autorisé ({max_animaux})."
                )
            })

    
    def __str__(self):
        return f"{self.cheptel} exploite {self.quartier}"


class Eleveur(AuditFieldsMixin, models.Model):
    """
    Eleveur
    """
    
    id_eleveur = models.AutoField(primary_key=True)  # Migration vers AutoField pour id_eleveur, dlg 10/2/26
    nom_eleveur = models.CharField(max_length=50, null=False, blank=False)
    prenom_eleveur = models.CharField(max_length=50, null=True, blank=True)
    tel_eleveur = models.CharField(max_length=50, null=True, blank=True)
    mail_eleveur = models.CharField(max_length=50, null=True, blank=True)
    adresse_eleveur = models.CharField(max_length=50, null=True, blank=True)
    commentaire = models.CharField(max_length=500, null=True, blank=True)
    
    def __str__(self):
        return str(self.nom_eleveur)

class TypeDExploitant(AuditFieldsMixin, models.Model):
    """
    Type d'exploitant
    """

    id_type_exploitant = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    
    def __str__(self):
        return str(self.description) 


class Exploitant(AuditFieldsMixin, models.Model):
    """
    Exploitant
    """
    
    # id_exploitant = models.BigIntegerField(primary_key=True)
    id_exploitant = models.AutoField(primary_key=True)  # Migration vers AutoField pour id_exploitant, dlg 10/2/26
    nom_exploitant = models.CharField(max_length=50, null=False, blank=False)
    type_exploitant = models.ForeignKey('alpages.TypeDExploitant', on_delete=models.SET_NULL, blank=True, null=True, related_name='exploitants')
    president = models.ForeignKey('alpages.Eleveur', on_delete=models.SET_NULL, blank=True, null=True, related_name='exploitants')
    
    def __str__(self):
        return str(self.nom_exploitant)

class EtreCompose(AuditFieldsMixin, models.Model):
    """
    EtreCompose (association exploitant / éleveurs)
    """
    exploitant = models.ForeignKey(Exploitant, on_delete=models.SET_NULL, blank=True, null=True, )
    eleveur = models.ForeignKey(Eleveur, on_delete=models.SET_NULL, blank=True, null=True, )

    class Meta:
        unique_together = ('exploitant', 'eleveur')
    
    def __str__(self):
        return f"{self.eleveur} est membre de {self.exploitant}"
    
class SubventionPNV(AuditFieldsMixin, models.Model):
    """
    Subvention PNV
    """
    
    id_subvention = models.BigIntegerField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    montant = models.DecimalField(max_digits=15, decimal_places=2, null=False, blank=False)
    engage = models.BooleanField(null=False, blank=False, default=False)
    paye = models.BooleanField(null=False, blank=False, default=False)
    exploitant = models.ForeignKey('alpages.Exploitant', on_delete=models.SET_NULL, blank=True, null=True, related_name='subventions')
    
    def __str__(self):
        return str(self.description)

class Logement(AuditFieldsMixin, models.Model):
    """
    Classe Logement
    Champs et valeurs issues des échanges avec la SEA73
    """
    
    logement_code = models.CharField(max_length=10)
    # Ajouté le 28/10/2025
    nom_logement = models.CharField(max_length=50, null=True, blank=True)
    unite_pastorale = models.ForeignKey('alpages.UnitePastorale', on_delete=models.SET_NULL, blank=True, null=True, related_name='logements')
    # Fin 28/10/2025
    statut = models.CharField(max_length=50, choices=LST_STATUT, null=True, blank=True)
    acces_final = models.CharField(max_length=50, choices=LST_ACCES_FINAL, null=True, blank=True)
    propriete = models.CharField(max_length=50, choices=LST_PROPRIETE, null=True, blank=True)
    type_logement = models.CharField(max_length=50, choices=LST_TYPE_LOGEMENT, null=True, blank=True)
    multiusage = models.CharField(max_length=50, choices=LST_MULTIUSAGE, null=True, blank=True)
    activite_laitiere = models.CharField(max_length=50, choices=LST_ACTIVITE_LAITIERE, null=True, blank=True)
    etat_batiment = models.CharField(max_length=50, choices=LST_ETAT_BATIMENT, null=True, blank=True)
    accueil_public = models.CharField(max_length=50, choices=LST_ACCUEIL_PUBLIC, null=True, blank=True)
    mixite_possible = models.CharField(max_length=50, choices=LST_OUI_NON_INC, null=True, blank=True)
    surface_logement = models.CharField(max_length=50, choices=LST_SURFACE_LOGEMENT, null=True, blank=True)
    presence_douche = models.CharField(max_length=50, choices=LST_OUI_NON_INC, null=True, blank=True)
    type_wc = models.CharField(max_length=50, choices=LST_WC, null=True, blank=True)
    alim_elec = models.CharField(max_length=50, choices=LST_ALIM_ELECTRIQUE, null=True, blank=True)
    alim_eau = models.CharField(max_length=50, choices=LST_ALIM_EAU, null=True, blank=True)
    origine_eau = models.CharField(max_length=50, choices=LST_ORIGINE_EAU, null=True, blank=True)
    qualite_eau = models.CharField(max_length=50, choices=LST_QUALITE_EAU, null=True, blank=True)
    dispo_eau = models.CharField(max_length=50, choices=LST_DISPO_EAU, null=True, blank=True)
    assainissement = models.CharField(max_length=50, choices=LST_ASSAINISSEMENT, null=True, blank=True)
    chauffe_eau = models.CharField(max_length=50, choices=LST_CHAUFFE_EAU, null=True, blank=True)
    chauffage = models.CharField(max_length=50, choices=LST_OUI_NON, null=True, blank=True)
    stockage_indep = models.CharField(max_length=50, choices=LST_OUI_NON, null=True, blank=True)
    
    geom = models.PointField(srid=2154, null=True)


class Commodite(AuditFieldsMixin, models.Model):
    """
    Commodite
    """
    
    id_commodite = models.BigIntegerField(primary_key=True)
    description = models.CharField(max_length=100, null=False, blank=False)
    
    def __str__(self):
        return str(self.description)
    

class LogementCommodite(AuditFieldsMixin, models.Model):
    """
    Association Logement / Commodite
    """
    
    id_logement_commodite = models.BigIntegerField(primary_key=True)
    logement = models.ForeignKey('alpages.Logement', on_delete=models.SET_NULL, blank=True, null=True, related_name='commodites')
    commodite = models.ForeignKey('alpages.Commodite', on_delete=models.SET_NULL, blank=True, null=True, related_name='logements')
    etat = models.CharField(max_length=50, null=False, blank=False)
    commentaire = models.CharField(max_length=50, null=True, blank=True)
    quantite = models.CharField(max_length=50, null=True, blank=True)
    
    
    def __str__(self):
        return f"{self.logement} a {self.quantite} de {self.commodite}"


class AbriDUrgence(AuditFieldsMixin, models.Model):
    """
    Abri d'urgence
    """
    
    id_abri_urgence = models.BigIntegerField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    etat = models.CharField(max_length=50, null=False, blank=False)
    
    
    def __str__(self):
        return str(self.description)


class AbriDUrgenceCommodite(AuditFieldsMixin, models.Model):
    """
    Association Abri d'urgence / Commodite
    """
    
    id_abri_urgence_commodite = models.BigIntegerField(primary_key=True)
    abri_urgence = models.ForeignKey('alpages.AbriDUrgence', on_delete=models.SET_NULL, blank=True, null=True, related_name='commodites')
    commodite = models.ForeignKey('alpages.Commodite', on_delete=models.SET_NULL, blank=True, null=True, related_name='abris_urgence')
    etat = models.CharField(max_length=50, null=False, blank=False)
    commentaire = models.CharField(max_length=50, null=True, blank=True)
    quantite = models.CharField(max_length=50, null=True, blank=True)
    
    
    def __str__(self):
        return f"{self.abri_urgence} a {self.quantite} de {self.commodite}"



class BeneficierDe(AuditFieldsMixin, models.Model):
    """
    Association Exploitant / Abri d'urgence
    """
    
    id_beneficier_de = models.BigIntegerField(primary_key=True)  
    exploitant = models.ForeignKey('alpages.Exploitant', on_delete=models.SET_NULL, blank=True, null=True, related_name='beneficiaires')
    abri_urgence = models.ForeignKey('alpages.AbriDUrgence', on_delete=models.SET_NULL, blank=True, null=True, related_name='beneficiaires')
    date_debut = models.DateField(null=False, blank=False)
    date_fin = models.DateField(null=True, blank=True)
    geometry = models.PointField(srid=2154, null=True, blank=True)
    
    def __str__(self):
        return f"{self.exploitant} bénéficie de {self.abri_urgence}"
    
# Ruche / Berger / Type Cheptel
class Ruche(AuditFieldsMixin, models.Model):
    """
    Ruche
    """
    
    id_ruche = models.BigIntegerField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    geometry = models.PointField(srid=2154, null=False, blank=False)
    situation_exploitation = models.ForeignKey('alpages.SituationDExploitation', on_delete=models.SET_NULL, blank=True, null=True, related_name='ruches')
    
    def __str__(self):
        return str(self.description)

class Berger(AuditFieldsMixin, models.Model):
    """
    Berger
    """
    
    id_berger = models.BigIntegerField(primary_key=True)
    nom_berger = models.CharField(max_length=50, null=False, blank=False)
    prenom_berger = models.CharField(max_length=50, null=False, blank=False)
    tel_berger = models.CharField(max_length=50, null=True, blank=True)
    adresse_berger = models.CharField(max_length=50, null=True, blank=True)
    commentaire = models.CharField(max_length=500, null=True, blank=True)
    
    def __str__(self):
        return str(self.nom_berger)

class GardeSituation(AuditFieldsMixin, models.Model):
    """
    Garde situation
    """
    
    id_garde_situation = models.BigIntegerField(primary_key=True)
    date_debut = models.DateField(null=False, blank=False)
    date_fin = models.DateField(null=True, blank=True)
    commentaire = models.CharField(max_length=500, null=True, blank=True)
    situation_exploitation = models.ForeignKey('alpages.SituationDExploitation', on_delete=models.SET_NULL, blank=True, null=True, related_name='gardes_situation')
    berger = models.ForeignKey('alpages.Berger', on_delete=models.SET_NULL, blank=True, null=True, related_name='gardes_situation')
    
    def __str__(self):
        return str(self.id_garde_situation)

##################
# Mise à jour Cheptels / types de cheptel
# le 9/2/26
class Production(AuditFieldsMixin, models.Model):
    """
    Production
    """
    
    id_production = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    
    def __str__(self):
        return str(self.description)

class Categorie_pension(AuditFieldsMixin, models.Model):
    """
    Catégorie de pension
    """
    
    id_categorie_pension = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    
    def __str__(self):
        return str(self.description)

class Espece(AuditFieldsMixin, models.Model):
    """
    Espèce
    """
    
    id_espece  = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    
    def __str__(self):
        return str(self.description)

class Race(AuditFieldsMixin, models.Model):
    """
    Race
    """

    id_race = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    espece = models.ForeignKey('alpages.Espece', on_delete=models.SET_NULL, blank=True, null=True, related_name='races')

    def __str__(self):
        return str(self.description)

class Categorie_animaux(AuditFieldsMixin, models.Model):
    """
    Catégorie d'animaux
    """
    
    id_categorie_animaux = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    espece = models.ForeignKey('alpages.Espece', on_delete=models.SET_NULL, blank=True, null=True, related_name='categories_animaux')
    
    def __str__(self):
        return str(self.description)

class Cheptel(AuditFieldsMixin, models.Model):
    """
    Cheptel
    """
    
    id_cheptel = models.BigIntegerField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)

    eleveur = models.ForeignKey('alpages.Eleveur', on_delete=models.SET_NULL, blank=True, null=True, related_name='cheptels')
    situation_exploitation = models.ForeignKey('alpages.SituationDExploitation', on_delete=models.SET_NULL, blank=True, null=True, related_name='cheptels')
    type_cheptel = models.ForeignKey('alpages.Type_cheptel', on_delete=models.SET_NULL, blank=True, null=True, related_name='cheptels')
    
    nombre_animaux = models.IntegerField(null=False, blank=False)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.eleveur} élève {self.type_cheptel} dans la situation {self.situation_exploitation}"

class Type_cheptel(AuditFieldsMixin, models.Model):
    """
    Type de cheptel
    """
    
    id_type_cheptel = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    coefficient_UGB = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=False,
        blank=False,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )
    production = models.ForeignKey('alpages.Production', on_delete=models.SET_NULL, blank=True, null=True, related_name='types_cheptel')
    pension = models.ForeignKey('alpages.Categorie_pension', on_delete=models.SET_NULL, blank=True, null=True, related_name='types_cheptel')
    race = models.ForeignKey('alpages.Race', on_delete=models.SET_NULL, blank=True, null=True, related_name='types_cheptel')
    categorie_animaux = models.ForeignKey('alpages.Categorie_animaux', on_delete=models.SET_NULL, blank=True, null=True, related_name='types_cheptel')

    def __str__(self):
        return str(self.description)


# FIN Mise à jour Cheptels / types de cheptel
##################

# Evénements
class TypeEvenement(AuditFieldsMixin, models.Model):
    """
    Type d'événement
    """
    
    id_type_evenement = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    
    def __str__(self):
        return str(self.description)

class Evenement(AuditFieldsMixin, models.Model):
    """
    Evenement
    """
    
    id_evenement = models.BigIntegerField(primary_key=True)
    date_evenement = models.DateField(null=False, blank=False)
    observateur = models.CharField(max_length=50, null=False, blank=False)
    date_observation = models.DateField(null=False, blank=False)
    source = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    geometry = models.GeometryField(srid=2154, null=True, blank=True)
    # equipement_exploitant = models.ForeignKey('alpages.EquipementExploitant', on_delete=models.SET_NULL, blank=True, null=True, related_name='evenements')
    # situation = models.ForeignKey('alpages.SituationDExploitation', on_delete=models.SET_NULL, blank=True, null=True, related_name='evenements')
    mesure_plan = models.ForeignKey('alpages.MesureDePlan', on_delete=models.SET_NULL, blank=True, null=True, related_name='evenements')
    # logement = models.ForeignKey('alpages.Logement', on_delete=models.CASCADE, related_name='evenements')
    # equipement_alpage = models.ForeignKey('alpages.EquipementAlpage', on_delete=models.SET_NULL, blank=True, null=True, related_name='evenements')
    unite_pastorale = models.ForeignKey('alpages.UnitePastorale', on_delete=models.SET_NULL, blank=True, null=True, related_name='evenements')
    type_evenement = models.ForeignKey('alpages.TypeEvenement', on_delete=models.SET_NULL, blank=True, null=True, related_name='evenements')
    
    def __str__(self):
        return str(self.description)


# EQUIPEMENTS
class TypeEquipement(AuditFieldsMixin, models.Model):
    """
    Type d'équipement
    """
    
    id_type_equipement = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    categorie = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return str(self.description)

class EquipementAlpage(AuditFieldsMixin, models.Model):
    """
    Equipement d'alpage (lié à l'UP)
    """

    id_equipement_alpage = models.BigIntegerField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    etat = models.CharField(max_length=50, null=False, blank=False)
    geometry = models.GeometryField(srid=2154, null=True, blank=True)
    type_equipement = models.ForeignKey('alpages.TypeEquipement', on_delete=models.SET_NULL, blank=True, null=True, related_name='eqptsAlpage')
    unite_pastorale = models.ForeignKey('alpages.UnitePastorale', on_delete=models.SET_NULL, blank=True, null=True, related_name='eqptsAlpage')

class EquipementExploitant(AuditFieldsMixin, models.Model):
    """
    Equipement d'exploitant
    """

    id_equipement_exploitant = models.BigIntegerField(primary_key=True)
    description = models.CharField(max_length=50, null=False, blank=False)
    etat = models.CharField(max_length=50, null=False, blank=False)
    geometry = models.GeometryField(srid=2154, null=True, blank=True)
    type_equipement = models.ForeignKey('alpages.TypeEquipement', on_delete=models.SET_NULL, blank=True, null=True, related_name='eqptsExploitant')
    situation_exploitation = models.ForeignKey('alpages.SituationDExploitation', on_delete=models.SET_NULL, blank=True, null=True, related_name='eqptsExploitant')
