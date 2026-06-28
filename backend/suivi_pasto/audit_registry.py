from auditlog.registry import auditlog

from suivi_pasto.models import (
    AbriDUrgence,
    AbriDUrgenceCommodite,
    BeneficierDe,
    Berger,
    Cheptel,
    ConventionDExploitation,
    Eleveur,
    Evenement,
    Exploitant,
    Exploiter,
    EquipementAlpage,
    EquipementExploitant,
    EtreCompose,
    GardeSituation,
    GeometrieUnitePastorale,
    Logement,
    MesureDePlan,
    PlanDeSuivi,
    ProprietaireFoncier,
    ProprietaireUnitePastorale,
    QuartierPasto,
    RealisationMesure,
    Ruche,
    SituationDExploitation,
    SubventionPNV,
    UnitePastorale,
    Visite,
)

_AUDIT_FIELDS = ["created_by", "created_on", "modified_by", "modified_on"]

for _model in [
    ProprietaireFoncier,
    ProprietaireUnitePastorale,
    Eleveur,
    Exploitant,
    EtreCompose,
    Berger,
    SituationDExploitation,
    Exploiter,
    GardeSituation,
    SubventionPNV,
    Cheptel,
    PlanDeSuivi,
    RealisationMesure,
    Visite,
    AbriDUrgence,
    AbriDUrgenceCommodite,
]:
    auditlog.register(_model, exclude_fields=_AUDIT_FIELDS)

for _model in [
    UnitePastorale,
    QuartierPasto,
    ConventionDExploitation,
    Ruche,
    MesureDePlan,
    Evenement,
    EquipementAlpage,
    EquipementExploitant,
    Logement,
    BeneficierDe,
]:
    # geom_active exclu (cache calculé par signal) ; geom inclus pour tracer les changements
    auditlog.register(_model, exclude_fields=_AUDIT_FIELDS + ["geom_active"])

# GeometrieUnitePastorale : geom est l'objet même, on le conserve dans le diff
auditlog.register(GeometrieUnitePastorale, exclude_fields=_AUDIT_FIELDS)
