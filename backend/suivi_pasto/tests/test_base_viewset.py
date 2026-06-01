from django.test import TestCase
from rest_framework.test import APIRequestFactory

from suivi_pasto.views import UnitePastoraleViewset
from suivi_pasto.models import UnitePastorale


class BaseModelViewSetTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_get_pk_field_name_unitepastorale(self):
        viewset = UnitePastoraleViewset()
        viewset.queryset = UnitePastorale.objects.all()
        self.assertEqual(viewset.get_pk_field_name(), "id_unite_pastorale")
