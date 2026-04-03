from django.test import TestCase
from rest_framework.test import APIRequestFactory

from alpages.views import UnitePastoraleViewset
from alpages.models import UnitePastorale


class BaseModelViewSetTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_get_pk_field_name_unitepastorale(self):
        viewset = UnitePastoraleViewset()
        viewset.queryset = UnitePastorale.objects.all()
        self.assertEqual(viewset.get_pk_field_name(), 'id_unite_pastorale')

    def test_get_next_id_empty_queryset(self):
        viewset = UnitePastoraleViewset()
        viewset.queryset = UnitePastorale.objects.none()
        request = self.factory.get('/api/unitePastorale/getNextId')
        response = viewset.get_next_id(request)
        self.assertEqual(response.data.get('next_id'), 1)
