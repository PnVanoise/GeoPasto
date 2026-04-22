from datetime import date
from django.contrib.gis.geos import GEOSGeometry
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from django.contrib.auth import get_user_model

from alpages.models import (
    SituationDExploitation,
    Commodite,
    AbriDUrgence,
    UnitePastorale,
    QuartierPasto,
    Cheptel,
    Exploiter,
    EquipementExploitant,
    ProprietaireFoncier,
    ProprietaireUnitePastorale,
)


class ViewsetsSmokeTest(APITestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='vtest', password='vtest')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        # create a minimal UnitePastorale required by SituationDExploitation serializer
        UnitePastorale.objects.create(id_unite_pastorale=1, code_up='UP1', nom_up='UP1', annee_version=2025, geometry='MULTIPOLYGON(((0 0,0 1,1 1,1 0,0 0)))', version_active=True)

    def test_create_and_list_commodite(self):
        url = reverse('commodite-list')
        resp = self.client.post(url, {'id_commodite': 30, 'description': 'C30'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        list_resp = self.client.get(url)
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(list_resp.json()), 1)

    def test_create_situation_and_list(self):
        url = reverse('situationexploitation-list')
        # send date as ISO string for JSON payload
        payload = {
            'id_situation': 30,
            'annee': date.today().year,
            'nom_situation': 'S30',
            'situation_active': True,
            'date_debut': date.today().isoformat(),
            'unite_pastorale': 1,
        }
        resp = self.client.post(url, payload, format='json')
        # If creation fails, include response data in assertion message for easier debugging
        if resp.status_code != status.HTTP_201_CREATED:
            print('DEBUG create situation response:', resp.status_code, resp.content)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_cannot_create_duplicate_situation_same_up_and_year(self):
        url = reverse('situationexploitation-list')
        year = date.today().year
        payload1 = {
            'id_situation': 40,
            'annee': year,
            'nom_situation': 'S40',
            'situation_active': True,
            'date_debut': date.today().isoformat(),
            'unite_pastorale': 1,
        }
        resp1 = self.client.post(url, payload1, format='json')
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

        # attempt to create another situation for same UP and year
        payload2 = payload1.copy()
        payload2['id_situation'] = 41
        resp2 = self.client.post(url, payload2, format='json')
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_abri_endpoint_create(self):
        url = reverse('abridurgence-list')
        resp = self.client.post(url, {'id_abri_urgence': 30, 'description': 'A30', 'etat': 'OK'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data.get('created_by'), 'vtest')
        self.assertIsNone(resp.data.get('modified_by'))
        self.assertIsNone(resp.data.get('modified_on'))

    def test_type_evenement_endpoint_create_sets_audit_fields(self):
        url = reverse('typeevenement-list')
        resp = self.client.post(url, {'id_type_evenement': 30, 'description': 'Meteo'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data.get('created_by'), 'vtest')
        self.assertIsNone(resp.data.get('modified_by'))
        self.assertIsNone(resp.data.get('modified_on'))

    def test_type_equipement_endpoint_create_sets_audit_fields(self):
        url = reverse('typeequipement-list')
        payload = {'id_type_equipement': 30, 'description': 'Passerelle', 'categorie': 'Alpage'}
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data.get('created_by'), 'vtest')
        self.assertIsNone(resp.data.get('modified_by'))
        self.assertIsNone(resp.data.get('modified_on'))


class SituationUpdateUpActionTest(APITestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='updater', password='updater')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.old_up = UnitePastorale.objects.create(
            id_unite_pastorale=100,
            code_up='UP-Y',
            nom_up='UP Y',
            annee_version=2015,
            geometry='SRID=2154;MULTIPOLYGON(((0 0,0 4,4 4,4 0,0 0)))',
            version_active=True,
            secteur='Secteur Test',
        )

        self.situation = SituationDExploitation.objects.create(
            id_situation=100,
            annee=2026,
            nom_situation='Situation X',
            situation_active=True,
            unite_pastorale=self.old_up,
        )

        self.proprietaire = ProprietaireFoncier.objects.create(
            id_proprietaire=100,
            nom_propr='Durand',
        )
        ProprietaireUnitePastorale.objects.create(
            proprietaire=self.proprietaire,
            unite_pastorale=self.old_up,
        )

    def test_mettre_a_jour_up_creates_new_version_and_switches_active(self):
        QuartierPasto.objects.create(
            id_quartier=100,
            code_quartier='Q1',
            nom_quartier='Quartier 1',
            geometry='SRID=2154;POLYGON((0 0,0 2,2 2,2 0,0 0))',
            situation_exploitation=self.situation,
        )
        QuartierPasto.objects.create(
            id_quartier=101,
            code_quartier='Q2',
            nom_quartier='Quartier 2',
            geometry='SRID=2154;POLYGON((2 0,2 2,4 2,4 0,2 0))',
            situation_exploitation=self.situation,
        )

        url = reverse('situationexploitation-mettre-a-jour-up', kwargs={'pk': self.situation.id_situation})
        resp = self.client.post(url, {}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.old_up.refresh_from_db()
        self.situation.refresh_from_db()

        self.assertFalse(self.old_up.version_active)
        self.assertNotEqual(self.situation.unite_pastorale_id, self.old_up.id_unite_pastorale)

        new_up = UnitePastorale.objects.get(id_unite_pastorale=self.situation.unite_pastorale_id)
        self.assertEqual(new_up.code_up, self.old_up.code_up)
        self.assertEqual(new_up.nom_up, self.old_up.nom_up)
        self.assertEqual(new_up.annee_version, self.situation.annee)
        self.assertTrue(new_up.version_active)
        self.assertEqual(new_up.geometry.geom_type, 'MultiPolygon')
        self.assertEqual(new_up.geometry.srid, 2154)

        self.assertTrue(
            ProprietaireUnitePastorale.objects.filter(
                proprietaire=self.proprietaire,
                unite_pastorale=new_up,
            ).exists()
        )

        expected_union = GEOSGeometry(
            'SRID=2154;MULTIPOLYGON(((0 0,0 2,2 2,4 2,4 0,2 0,0 0)))'
        )
        self.assertTrue(new_up.geometry.equals(expected_union))

        self.assertEqual(resp.data['old_up_id'], self.old_up.id_unite_pastorale)
        self.assertEqual(resp.data['new_up_id'], new_up.id_unite_pastorale)
        self.assertEqual(resp.data['new_up_annee_version'], self.situation.annee)
        self.assertEqual(resp.data['quartiers_count'], 2)

    def test_mettre_a_jour_up_returns_400_when_no_quartier_geometry(self):
        url = reverse('situationexploitation-mettre-a-jour-up', kwargs={'pk': self.situation.id_situation})
        resp = self.client.post(url, {}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UnitePastorale.objects.filter(code_up='UP-Y').count(), 1)


class SituationDuplicateActionTest(APITestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='duplicator', password='duplicator')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.up = UnitePastorale.objects.create(
            id_unite_pastorale=200,
            code_up='UP-DUP',
            nom_up='UP DUP',
            annee_version=2026,
            geometry='SRID=2154;MULTIPOLYGON(((0 0,0 1,1 1,1 0,0 0)))',
            version_active=True,
            secteur='S1',
        )

        self.situation = SituationDExploitation.objects.create(
            id_situation=200,
            annee=2026,
            nom_situation='Situation Source',
            situation_active=True,
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 12, 31),
            unite_pastorale=self.up,
        )

    def test_duplicate_clones_related_entities_for_next_year(self):
        q_old = QuartierPasto.objects.create(
            id_quartier=200,
            code_quartier='QD1',
            nom_quartier='Quartier DUP',
            geometry='SRID=2154;POLYGON((0 0,0 2,2 2,2 0,0 0))',
            situation_exploitation=self.situation,
        )
        c_old = Cheptel.objects.create(
            id_cheptel=200,
            description='Cheptel DUP',
            situation_exploitation=self.situation,
            nombre_animaux=12,
            date_debut=date(2026, 5, 1),
            date_fin=date(2026, 10, 31),
        )
        Exploiter.objects.create(
            id_exploiter=200,
            cheptel=c_old,
            quartier=q_old,
            date_debut=date(2026, 6, 1),
            date_fin=date(2026, 9, 30),
            nombre_animaux=10,
            mode_conduite='libre',
            commentaire='Parcours test',
        )
        EquipementExploitant.objects.create(
            id_equipement_exploitant=200,
            description='Cloture mobile',
            etat='Bon',
            geometry='SRID=2154;POINT(1 1)',
            situation_exploitation=self.situation,
        )

        url = reverse('situationexploitation-duplicate', kwargs={'pk': self.situation.id_situation})
        resp = self.client.post(url, {}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_situation = SituationDExploitation.objects.get(id_situation=resp.data['id_situation'])
        self.assertEqual(new_situation.annee, 2027)
        self.assertEqual(new_situation.unite_pastorale_id, self.situation.unite_pastorale_id)

        new_quartiers = QuartierPasto.objects.filter(situation_exploitation=new_situation)
        self.assertEqual(new_quartiers.count(), 1)

        new_cheptels = Cheptel.objects.filter(situation_exploitation=new_situation)
        self.assertEqual(new_cheptels.count(), 1)
        new_cheptel = new_cheptels.first()
        self.assertEqual(new_cheptel.date_debut, date(2027, 1, 1))
        self.assertEqual(new_cheptel.date_fin, date(2027, 12, 31))

        new_parcours = Exploiter.objects.filter(
            cheptel__situation_exploitation=new_situation,
            quartier__situation_exploitation=new_situation,
        )
        self.assertEqual(new_parcours.count(), 1)
        new_parcours_obj = new_parcours.first()
        self.assertEqual(new_parcours_obj.date_debut, date(2027, 6, 1))
        self.assertEqual(new_parcours_obj.date_fin, date(2027, 9, 30))

        new_eq = EquipementExploitant.objects.filter(situation_exploitation=new_situation)
        self.assertEqual(new_eq.count(), 1)

    def test_duplicate_returns_400_when_next_year_exists(self):
        SituationDExploitation.objects.create(
            id_situation=201,
            annee=2027,
            nom_situation='Situation déjà existante',
            situation_active=True,
            unite_pastorale=self.up,
        )

        url = reverse('situationexploitation-duplicate', kwargs={'pk': self.situation.id_situation})
        resp = self.client.post(url, {}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
