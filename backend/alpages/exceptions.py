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

    if response is None and isinstance(exc, ProtectedError):
        view = context.get('view')
        instance = None
        try:
            instance = view.get_object()
        except Exception:
            pass

        # 1. On regroupe les objets protégés par modèle
        # Structure : { 'Equipement d'alpage': 3, 'Situation': 1 }
        stats = {}
        for obj in exc.protected_objects:
            # On vérifie si l'objet est bien lié à notre instance (sécurité)
            # Car ProtectedError peut parfois contenir des objets liés indirectement
            model_meta = obj._meta
            name = model_meta.verbose_name_plural if stats.get(model_meta.verbose_name) else model_meta.verbose_name
            
            # On utilise le verbose_name comme clé
            label = model_meta.verbose_name
            stats[label] = stats.get(label, 0) + 1

        # 2. Construction du message de détail
        # On transforme le dictionnaire en une liste de chaînes : ["3 équipements", "1 situation"]
        parts = []
        for label, count in stats.items():
            model_meta = None
            # Retrouver les meta pour le pluriel
            for obj in exc.protected_objects:
                if obj._meta.verbose_name == label:
                    model_meta = obj._meta
                    break
            
            name = model_meta.verbose_name if count <= 1 else model_meta.verbose_name_plural
            parts.append(f"{count} {name}")

        # On joint les parties avec des virgules et un "et" à la fin
        if len(parts) > 1:
            dependencies_str = ", ".join(parts[:-1]) + " et " + parts[-1]
        else:
            dependencies_str = parts[0]

        # 3. Infos sur le parent
        parent_name = "cet élément"
        if view and hasattr(view, 'get_queryset'):
            try:
                parent_name = view.get_queryset().model._meta.verbose_name
            except Exception: pass
        
        determinant = "cette" if parent_name.lower().endswith('e') else "ce"

        return Response(
            {
                "detail": f"Suppression impossible : {determinant} {parent_name} est lié à : {dependencies_str}.",
                "code": "PROTECTED_RELATION",
                "meta": {
                    "dependencies": stats,
                    "target_model": parent_name
                }
            },
            status=status.HTTP_409_CONFLICT
        )

    return response