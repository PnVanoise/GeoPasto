from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from datetime import date

from alpages.models import (
    SituationDExploitation,
    Exploiter,
    Ruche,
    GardeSituation,
    QuartierPasto,
    Berger,
    Eleveur,
)


class DuplicateSituationTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        # create and authenticate a test user because the API requires authentication
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)
        # create a situation
        self.orig = SituationDExploitation.objects.create(
            id_situation=1,
            nom_situation="Origine",
            situation_active=True,
            date_debut=date(2020, 1, 1),
            date_fin=None,
        )
        # create related objects
        # Create required related FK objects
        quartier = QuartierPasto.objects.create(
            id_quartier=1, code_quartier="Q1", nom_quartier="Q1"
        )
        berger = Berger.objects.create(id_berger=1, nom_berger="B", prenom_berger="B")
        eleveur = Eleveur.objects.create(id_eleveur=1, nom_eleveur="E")

        Exploiter.objects.create(
            id_exploiter=1,
            quartier=quartier,
            situation_exploitation=self.orig,
            date_debut=date(2020, 1, 1),
            commentaire="c",
        )
        Ruche.objects.create(
            id_ruche=1,
            description="R1",
            geometry="POINT(0 0)",
            situation_exploitation=self.orig,
        )
        GardeSituation.objects.create(
            id_garde_situation=1,
            date_debut=date(2020, 1, 1),
            commentaire="g",
            situation_exploitation=self.orig,
            berger=berger,
        )
