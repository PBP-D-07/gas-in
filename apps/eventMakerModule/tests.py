from django.test import TestCase, Client
from django.urls import reverse
from apps.main.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.eventMakerModule.models import Event
from datetime import date
import json
import uuid

class EventViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.event = Event.objects.create(
            name="Test Event",
            description="Test Description",
            date=date.today(),
            location="Jakarta",
            category="running",
            owner=self.user
        )
        
    # Event Model
    def test_event_name(self):
        response = str(self.event)
        self.assertEqual(response, "Test Event")

    # View render
    def test_show_create_renders_template(self):
        response = self.client.get(reverse("eventMakerModule:show_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_event.html")

    def test_show_edit_renders_template(self):
        response = self.client.get(reverse("eventMakerModule:show_edit", args=[self.event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_event.html")

    def test_show_detail_renders_template(self):
        response = self.client.get(reverse("eventMakerModule:show_detail", args=[self.event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "event_detail.html")

    # create_event
    def test_create_event_requires_login(self):
        response = self.client.post(reverse("eventMakerModule:create_event"), {
            "name": "New Event",
            "description": "New Desc",
            "date": "2025-10-21T08:23",
            "location": "Bandung",
            "category": "running",
            "thumbnail": ""
        })
        data = json.loads(response.content)
        self.assertIn("You must be logged in to create an event", data["message"])
        self.assertEqual(response.status_code, 401)

    def test_create_event_success(self):
        self.client.login(username="testuser", password="testpass")
        image = SimpleUploadedFile("thumb.jpg", b"file_content", content_type="image/jpeg")

        response = self.client.post(reverse("eventMakerModule:create_event"), {
            "name": "New Event",
            "description": "New Desc",
            "date": "2025-10-21T09:12",
            "location": "Bandung",
            "category": "running",
            "thumbnail": image
        })

        data = json.loads(response.content)
        self.assertIn("Event created successfully", data["message"])
        self.assertEqual(response.status_code, 201)

    def test_create_event_invalid_method(self):
        response = self.client.get(reverse("eventMakerModule:create_event"))
        self.assertEqual(response.status_code, 405)

    # get_all_event
    def test_get_all_event_returns_list(self):
        response = self.client.get(reverse("eventMakerModule:get_all_event"))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsInstance(data["data"], list)
        self.assertGreaterEqual(len(data["data"]), 1)

    # get_event_by_id
    def test_get_event_by_id_success(self):
        response = self.client.get(reverse("eventMakerModule:get_event_by_id", args=[self.event.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["data"]["id"], str(self.event.id))

    def test_get_event_by_id_not_found(self):
        invalid_id = uuid.uuid4()  # generate UUID acak
        response = self.client.get(reverse("eventMakerModule:get_event_by_id", args=[str(invalid_id)]))
        self.assertEqual(response.status_code, 404)

    # delete_event
    def test_delete_event_invalid_method(self):
        response = self.client.get(reverse("eventMakerModule:delete_event", args=[self.event.id]))
        self.assertEqual(response.status_code, 405)

    def test_delete_event_success(self):
        response = self.client.post(reverse("eventMakerModule:delete_event", args=[self.event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Event.objects.filter(pk=self.event.id).exists())

    # join_event
    def test_join_event_requires_login(self):
        response = self.client.post(reverse("eventMakerModule:join_event", args=[self.event.id]))
        self.assertEqual(response.status_code, 401)

    def test_join_event_success(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(reverse("eventMakerModule:join_event", args=[self.event.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("joined", data["message"])

    def test_join_event_already_joined(self):
        self.client.login(username="testuser", password="testpass")
        self.event.participants.add(self.user)
        response = self.client.post(reverse("eventMakerModule:join_event", args=[self.event.id]))
        self.assertEqual(response.status_code, 400)

    # edit_event
    def test_edit_event_invalid_method(self):
        response = self.client.get(reverse("eventMakerModule:edit_event", args=[self.event.id]))
        self.assertEqual(response.status_code, 405)

    def test_edit_event_success(self):
        response = self.client.post(reverse("eventMakerModule:edit_event", args=[self.event.id]), {
            "name": "Edited Event",
            "location": "Surabaya",
        })
        self.assertEqual(response.status_code, 200)
        self.event.refresh_from_db()
        self.assertEqual(self.event.name, "Edited Event")
        self.assertEqual(self.event.location, "Surabaya")
