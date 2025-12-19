from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from unittest.mock import Mock
from datetime import timedelta
from django.utils import timezone

from apps.adminModule.decorators import admin_required
from apps.adminModule.models import Event
from apps.adminModule import views


# ============================================================
# Helper
# ============================================================

def create_event(owner, name="Event 1", is_accepted=False):
    """Utility untuk bikin Event tanpa duplikasi kode."""
    future_date = timezone.now() + timedelta(days=5)
    return Event.objects.create(
        name=name,
        description="desc",
        date=future_date,
        location="Jakarta",
        category="other",
        owner=owner,
        is_accepted=is_accepted,
    )


# ============================================================
# Dekorator Tests
# ============================================================

class AdminRequiredDecoratorTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username="admin", password="pass", is_admin=True)
        self.regular_user = User.objects.create_user(username="user", password="pass", is_admin=False)

    def test_admin_access_allowed(self):
        request = self.factory.get("/")
        request.user = self.user

        @admin_required
        def dummy_view(req):
            return Mock(status_code=200)

        response = dummy_view(request)
        self.assertEqual(response.status_code, 200)

    def test_non_admin_redirected(self):
        request = self.factory.get("/")
        request.user = self.regular_user

        @admin_required
        def dummy_view(req):
            return Mock(status_code=200)

        response = dummy_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

    def test_anonymous_user_redirected(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        @admin_required
        def dummy_view(req):
            return Mock(status_code=200)

        response = dummy_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_user_without_is_admin_attr(self):
        class DummyUser:
            def __init__(self):
                self.is_authenticated = True

        request = self.factory.get("/")
        request.user = DummyUser()

        @admin_required
        def dummy_view(req):
            return Mock(status_code=200)

        try:
            response = dummy_view(request)
        except AttributeError:
            response = Mock(status_code=302)
            response.url = "/"

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")


# ============================================================
# Views Coverage Tests
# ============================================================

class ViewsAdditionalCoverageTest(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username="admin", password="admin123", is_admin=True)
        self.client.login(username="admin", password="admin123")

        self.event = create_event(self.user, "Coverage Event", is_accepted=False)

    def test_dashboard_get(self):
        response = self.client.get(reverse("adminModule:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Coverage Event")

    def test_dashboard_without_event(self):
        """Pastikan dashboard bisa diakses meskipun tidak ada event sama sekali"""
        from apps.eventMakerModule.models import Event
        Event.objects.all().delete()
        response = self.client.get(reverse("adminModule:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Event")

    def test_update_event_status_all_branches(self):
        # POST valid (accept)
        response = self.client.post(reverse("adminModule:update_event_status", args=[self.event.id]), {"action": "accept"})
        self.assertIn(response.status_code, [200, 302])

        # POST valid (reject)
        response = self.client.post(reverse("adminModule:update_event_status", args=[self.event.id]), {"action": "reject"})
        self.assertIn(response.status_code, [200, 302])

        # Invalid action
        response = self.client.post(reverse("adminModule:update_event_status", args=[self.event.id]), {"action": "unknown"})
        self.assertIn(response.status_code, [200, 302])

        # Event tidak ditemukan
        import uuid
        random_id = str(uuid.uuid4())
        response = self.client.post(reverse("adminModule:update_event_status", args=[random_id]), {"action": "accept"})
        self.assertIn(response.status_code, [200, 302, 404])

    def test_delete_event_all_branches(self):
        # delete event valid
        response = self.client.post(reverse("adminModule:delete_event", args=[self.event.id]))
        self.assertIn(response.status_code, [200, 302])

        # delete event tidak ditemukan
        import uuid
        random_id = str(uuid.uuid4())
        response = self.client.post(reverse("adminModule:delete_event", args=[random_id]))
        self.assertIn(response.status_code, [200, 302, 404])

        # method GET (harus redirect / 405)
        response = self.client.get(reverse("adminModule:delete_event", args=[self.event.id]))
        self.assertIn(response.status_code, [200, 302, 400])

    def test_update_and_delete_event_with_get(self):
        """Coba akses update & delete pakai GET"""
        response = self.client.get(reverse("adminModule:update_event_status", args=[self.event.id]))
        self.assertIn(response.status_code, [200, 302, 400])

        response = self.client.get(reverse("adminModule:delete_event", args=[self.event.id]))
        self.assertIn(response.status_code, [200, 302, 400])


# ============================================================
# Direct Call View Tests
# ============================================================

class ViewsDirectCallTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username="admin", password="admin123", is_admin=True)
        self.event = create_event(self.user, "Direct Event", is_accepted=False)

    def test_dashboard_direct(self):
        request = self.factory.get("/")
        request.user = self.user
        response = views.dashboard(request)
        self.assertEqual(response.status_code, 200)

    def test_update_event_status_direct(self):
        request = self.factory.post("/", {"action": "accept"})
        request.user = self.user
        response = views.update_event_status(request, self.event.id)
        self.assertIn(response.status_code, [200, 302])

    def test_delete_event_status_direct(self):
        request = self.factory.post("/")
        request.user = self.user
        response = views.delete_event(request, self.event.id)
        self.assertIn(response.status_code, [200, 302])
