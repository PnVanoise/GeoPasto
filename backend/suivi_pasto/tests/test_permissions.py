from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from suivi_pasto.models import Commodite, SituationDExploitation, UnitePastorale


class PermissionsSmokeTest(APITestCase):

    def test_unauthenticated_cannot_list_commodite(self):
        url = reverse("commodite-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

User = get_user_model()


def _make_user(username, *perm_codenames):
    """Create a user and grant it the listed permission codenames."""
    user = User.objects.create_user(username=username, password="x")
    perms = Permission.objects.filter(codename__in=perm_codenames)
    user.user_permissions.set(perms)
    return user


def _client_for(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


# ---------------------------------------------------------------------------
# Tests : vérifier que le back respecte les mêmes droits que le front
# ---------------------------------------------------------------------------


class ModelPermissionsEnforcedTest(APITestCase):
    """
    Vérifie que DjangoModelPermissions est bien actif :
    ce que le front cache est aussi bloqué par l'API.
    """

    # --- lecture ---------------------------------------------------------

    def test_view_only_user_can_get_list(self):
        user = _make_user("obs", "view_commodite")
        resp = _client_for(user).get(reverse("commodite-list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_no_permission_user_cannot_get_list(self):
        user = _make_user("noperm")
        resp = _client_for(user).get(reverse("commodite-list"))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # --- création --------------------------------------------------------

    def test_view_only_user_cannot_post(self):
        """Un observateur (vue seule) ne peut pas créer via l'API directement."""
        user = _make_user("obs2", "view_commodite")
        resp = _client_for(user).post(
            reverse("commodite-list"),
            {"description": "injection directe"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_with_add_perm_can_post(self):
        user = _make_user("writer", "view_commodite", "add_commodite")
        resp = _client_for(user).post(
            reverse("commodite-list"),
            {"description": "OK"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    # --- modification ----------------------------------------------------

    def test_view_only_user_cannot_put(self):
        from suivi_pasto.models import Commodite

        c = Commodite.objects.create(id_commodite=500, description="C500")
        user = _make_user("obs3", "view_commodite")
        resp = _client_for(user).put(
            reverse("commodite-detail", kwargs={"pk": c.pk}),
            {"description": "tentative"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_with_change_perm_can_put(self):
        from suivi_pasto.models import Commodite

        c = Commodite.objects.create(id_commodite=501, description="C501")
        user = _make_user("editor", "view_commodite", "change_commodite")
        resp = _client_for(user).put(
            reverse("commodite-detail", kwargs={"pk": c.pk}),
            {"description": "modifié"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # --- suppression -----------------------------------------------------

    def test_view_only_user_cannot_delete(self):
        from suivi_pasto.models import Commodite

        c = Commodite.objects.create(id_commodite=502, description="C502")
        user = _make_user("obs4", "view_commodite")
        resp = _client_for(user).delete(
            reverse("commodite-detail", kwargs={"pk": c.pk})
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_with_delete_perm_can_delete(self):
        c = Commodite.objects.create(id_commodite=503, description="C503")
        user = _make_user("admin", "view_commodite", "delete_commodite")
        resp = _client_for(user).delete(
            reverse("commodite-detail", kwargs={"pk": c.pk})
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Actions custom : mettre-a-jour-geometrie et duplicate
# Ces actions POST héritent des permissions du viewset (change_situationdexploitation).
# ---------------------------------------------------------------------------


class CustomActionPermissionsTest(APITestCase):

    def setUp(self):
        self.up = UnitePastorale.objects.create(
            id_unite_pastorale=600,
            code_up="UP600",
            nom_up="UP 600",
            geom_active="SRID=2154;MULTIPOLYGON(((0 0,0 1,1 1,1 0,0 0)))",
        )
        self.situation = SituationDExploitation.objects.create(
            id_situation=600,
            nom_situation="Sit600",
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 12, 31),
            unite_pastorale=self.up,
        )

    def _url_maj(self):
        return reverse(
            "situationexploitation-mettre-a-jour-geometrie",
            kwargs={"pk": self.situation.pk},
        )

    def _url_dup(self):
        return reverse(
            "situationexploitation-duplicate",
            kwargs={"pk": self.situation.pk},
        )

    # mettre-a-jour-geometrie ------------------------------------------------

    def test_unauthenticated_cannot_call_mettre_a_jour(self):
        resp = self.client.post(self._url_maj(), {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_view_only_cannot_call_mettre_a_jour(self):
        user = _make_user("obs_maj", "view_situationdexploitation")
        resp = _client_for(user).post(self._url_maj(), {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_perm_can_call_mettre_a_jour(self):
        # DRF mappe POST → add_* quelle que soit la sémantique de l'action.
        user = _make_user(
            "editor_maj",
            "view_situationdexploitation",
            "add_situationdexploitation",
        )
        resp = _client_for(user).post(self._url_maj(), {}, format="json")
        # La situation n'a pas de quartiers → 400, mais pas 401/403
        self.assertNotIn(
            resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        )

    # duplicate --------------------------------------------------------------

    def test_unauthenticated_cannot_duplicate(self):
        resp = self.client.post(self._url_dup(), {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_view_only_cannot_duplicate(self):
        user = _make_user("obs_dup", "view_situationdexploitation")
        resp = _client_for(user).post(self._url_dup(), {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_perm_can_duplicate(self):
        # DRF mappe POST → add_* quelle que soit la sémantique de l'action.
        user = _make_user(
            "editor_dup",
            "view_situationdexploitation",
            "add_situationdexploitation",
        )
        resp = _client_for(user).post(self._url_dup(), {}, format="json")
        self.assertNotIn(
            resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        )


# ---------------------------------------------------------------------------
# Endpoints accounts : /api/userpermissions/ et /api/users/
# Ces APIView utilisent IsAuthenticated (pas de modèle Django associé).
# ---------------------------------------------------------------------------


class AccountsEndpointsTest(APITestCase):

    def test_unauthenticated_cannot_get_userpermissions(self):
        resp = self.client.get(reverse("userpermissions"))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_get_userpermissions(self):
        user = _make_user("any_user")
        resp = _client_for(user).get(reverse("userpermissions"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("username", resp.data)
        self.assertIn("permissions_by_model", resp.data)

    def test_userpermissions_returns_own_username(self):
        user = _make_user("jdupont")
        resp = _client_for(user).get(reverse("userpermissions"))
        self.assertEqual(resp.data["username"], "jdupont")

    def test_unauthenticated_cannot_get_user_list(self):
        resp = self.client.get(reverse("user-list"))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_get_user_list(self):
        user = _make_user("any_user2")
        resp = _client_for(user).get(reverse("user-list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)

    def test_user_list_contains_id_username_full_name(self):
        User = get_user_model()
        User.objects.create_user(
            username="alice", first_name="Alice", last_name="Martin", password="x"
        )
        user = _make_user("any_user3")
        resp = _client_for(user).get(reverse("user-list"))
        usernames = [u["username"] for u in resp.data]
        self.assertIn("alice", usernames)
        alice = next(u for u in resp.data if u["username"] == "alice")
        self.assertEqual(alice["full_name"], "Alice Martin")
        self.assertIn("id", alice)
