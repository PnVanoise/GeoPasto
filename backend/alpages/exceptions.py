from rest_framework.views import exception_handler
from django.db.models import ProtectedError
from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

from rest_framework.views import exception_handler
from django.db.models import ProtectedError
from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def api_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        if isinstance(exc, ProtectedError):
            view = context.get('view')
            protected_objects = exc.protected_objects
            child_model_meta = list(protected_objects)[0]._meta
            
            # --- Logique de comptage précis ---
            try:
                # 1. On récupère l'instance que l'on tentait de supprimer
                instance = view.get_object()
                
                # 2. On trouve le nom du champ dans le modèle enfant qui pointe vers le parent
                # On cherche une Foreign Key dont le modèle de destination est celui de l'instance
                related_field_name = next(
                    f.name for f in child_model_meta.get_fields() 
                    if hasattr(f, 'remote_field') and f.remote_field and f.remote_field.model == instance.__class__
                )

                # 3. On compte réellement en base pour éviter les faux positifs du QuerySet global
                count = child_model_meta.model.objects.filter(**{related_field_name: instance}).count()
            except Exception:
                # Fallback au compte global si la recherche dynamique échoue
                count = len(protected_objects)

            # --- Préparation des noms de modèles ---
            # Enfant (Bloquant)
            child_model_name = child_model_meta.verbose_name if count <= 1 else child_model_meta.verbose_name_plural

            # Parent (Cible)
            parent_model_name = "cet élément"
            if view and hasattr(view, 'get_queryset'):
                try:
                    parent_model_name = view.get_queryset().model._meta.verbose_name
                except Exception:
                    pass
            
            # Petit bonus : accord du déterminant (basique)
            determinant = "cette" if parent_model_name.lower().endswith('e') else "ce"

            return Response(
                {
                    "detail": f"Suppression impossible : {determinant} {parent_model_name} est lié à {count} {child_model_name}.",
                    "code": "PROTECTED_RELATION",
                    "meta": {
                        "count": count,
                        "target_model": parent_model_name,
                        "blocking_model_singular": child_model_meta.verbose_name,
                        "blocking_model_plural": child_model_meta.verbose_name_plural
                    }
                },
                status=status.HTTP_409_CONFLICT
            )

        if isinstance(exc, IntegrityError):
            return Response(
                {"detail": "Erreur d'intégrité en base de données."},
                status=status.HTTP_409_CONFLICT
            )
            
        # Log des autres erreurs 500
        logger.error(f"Unhandled Exception: {type(exc)} - {exc}")

    return response