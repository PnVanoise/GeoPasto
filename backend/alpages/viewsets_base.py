from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models.deletion import ProtectedError
from django.db.utils import IntegrityError

import logging

logger = logging.getLogger(__name__)
from .pagination import DefaultPagination


class BaseModelViewSet(ModelViewSet):
    """
    Standardized ModelViewSet with:
    - uniform create/update logging + error handling
    - generic getNextId action for models that use manual integer PKs
    """

    def _resolve_base_queryset(self):
        """Return an unfiltered queryset usable in tests and utility methods.

        In unit tests, viewsets are often instantiated without a request and
        with ``viewset.queryset`` set directly. Using this helper avoids
        accessing request-dependent ``get_queryset`` implementations.
        """
        qs = getattr(self, 'queryset', None)
        if qs is not None:
            return qs.all() if hasattr(qs, 'all') else qs
        return self.get_queryset()

    def _get_model_field_names(self, serializer):
        model = getattr(getattr(serializer, 'Meta', None), 'model', None)
        if model is None:
            return set()
        return {field.name for field in model._meta.concrete_fields}

    def _get_actor_name(self):
        request = getattr(self, 'request', None)
        user = getattr(request, 'user', None)
        if not user or not getattr(user, 'is_authenticated', False):
            return None
        if hasattr(user, 'get_username'):
            return user.get_username() or None
        return getattr(user, 'username', None)

    def _audit_save_kwargs(self, serializer, is_create):
        actor = self._get_actor_name()
        if not actor:
            return {}

        field_names = self._get_model_field_names(serializer)
        save_kwargs = {}

        if is_create and 'created_by' in field_names:
            save_kwargs['created_by'] = actor

        if (not is_create) and 'modified_by' in field_names:
            save_kwargs['modified_by'] = actor

        if (not is_create) and 'modified_on' in field_names:
            save_kwargs['modified_on'] = timezone.now()

        return save_kwargs

    def perform_create(self, serializer):
        save_kwargs = self._audit_save_kwargs(serializer, is_create=True)
        serializer.save(**save_kwargs)

    def perform_update(self, serializer):
        save_kwargs = self._audit_save_kwargs(serializer, is_create=False)
        serializer.save(**save_kwargs)

    def create(self, request, *args, **kwargs):
        logger.debug(f"BaseModelViewset {self.__class__.__name__} - Received data for creation: {request.data}")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            logger.debug(f"BaseModelViewset {self.__class__.__name__} - Created instance: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        logger.warning(f"BaseModelViewset {self.__class__.__name__} - Validation errors during creation: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ProtectedError:
            return Response(
                {"detail": "Suppression impossible : objet référencé."},
                status=status.HTTP_409_CONFLICT
            )

        except IntegrityError:
            return Response(
                {"detail": "Erreur d'intégrité en base."},
                status=status.HTTP_409_CONFLICT
            )

    def update(self, request, *args, **kwargs):
        logger.debug(f"BaseModelViewset {self.__class__.__name__} - Received data for update: {request.data}")
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            logger.debug(f"BaseModelViewset {self.__class__.__name__} - Updated instance: {serializer.data}")
            return Response(serializer.data)
        logger.warning(f"BaseModelViewset {self.__class__.__name__} - Validation errors during update: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='getNextId')
    def get_next_id(self, request):
        """
        Generic next-id endpoint. Only returns a next id when the model uses a
        manual integer PK. Uses DB-side ordering but still not safe under heavy concurrency—
        prefer migrating to AutoField/BigAutoField or UUIDs.
        """
        try:
            qs = self._resolve_base_queryset().order_by(self.get_pk_field_name())
        except Exception:
            logger.warning(f"BaseModelViewset {self.__class__.__name__} - Error occurred while fetching queryset for next ID")
            return Response({'next_id': None})
        last = qs.last()
        if not last:
            return Response({'next_id': 1})
        pk_name = self.get_pk_field_name()
        last_val = getattr(last, pk_name, None)
        try:
            next_id = int(last_val) + 1
        except Exception:
            logger.warning(f"BaseModelViewset {self.__class__.__name__} - Error occurred while calculating next ID")
            return Response({'next_id': None})
        return Response({'next_id': next_id})

    def list(self, request, *args, **kwargs):
        """
        Default `list` behaviour for all ModelViewSets inheriting from
        `BaseModelViewSet`. By default return the full list unless the
        client provides a `page` query parameter, in which case the
        `DefaultPagination` is used. Child viewsets may override `list`
        if they require a different behaviour.
        """
        self.pagination_class = DefaultPagination
        return self.conditional_list(request)

    def get_pk_field_name(self):
        # model PK attribute name (e.g. 'id', 'id_unite_pastorale', ...)
        return self._resolve_base_queryset().model._meta.pk.name

    def conditional_list(self, request, queryset=None, serializer_class=None):
        """
        Helper to return either a full list or a paginated response depending
        on whether the client provided a `page` query parameter.

        If `serializer_class` is provided it will be used to serialize the
        results (useful for light/detail serializers). Otherwise `get_serializer`
        is used so normal `serializer_class`/`get_serializer_class` behaviour
        (including context) is preserved.

        Usage: child viewsets can call `return self.conditional_list(request, serializer_class=MySerializer)`
        or override `self.pagination_class` before calling to select a
        pagination class.
        """
        qs = queryset if queryset is not None else self.filter_queryset(self.get_queryset())

        # If no `page` param, return full list
        if 'page' not in request.GET:
            if serializer_class is not None:
                serializer = serializer_class(qs, many=True, context=self.get_serializer_context())
            else:
                serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)

        # Otherwise rely on DRF pagination machinery (child may set pagination_class)
        page = self.paginate_queryset(qs)
        if page is not None:
            if serializer_class is not None:
                serializer = serializer_class(page, many=True, context=self.get_serializer_context())
            else:
                serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        if serializer_class is not None:
            serializer = serializer_class(qs, many=True, context=self.get_serializer_context())
        else:
            serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
