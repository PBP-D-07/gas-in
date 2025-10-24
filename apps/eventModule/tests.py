from django.test import TestCase, Client
from django.urls import reverse
from apps.main.models import User
from apps.eventMakerModule.models import Event
from datetime import datetime, timedelta
import json


class EventModuleViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        
        # Buat event di berbagai lokasi dan kategori
        self.event_jakarta_running = Event.objects.create(
            name="Jakarta Marathon",
            description="Lari pagi di Jakarta",
            date=datetime.now() + timedelta(days=7),
            location="Jakarta Pusat",
            category="running",
            is_accepted=True,
            owner=self.user
        )
        
        self.event_bogor_futsal = Event.objects.create(
            name="Bogor Futsal Cup",
            description="Turnamen futsal di Bogor",
            date=datetime.now() + timedelta(days=10),
            location="Bogor",
            category="futsal",
            is_accepted=True,
            owner=self.user
        )
        
        self.event_depok_badminton = Event.objects.create(
            name="Depok Badminton Championship",
            description="Lomba badminton di Depok",
            date=datetime.now() + timedelta(days=14),
            location="Depok",
            category="badminton",
            is_accepted=True,
            owner=self.user
        )
        
        self.event_tangerang_basketball = Event.objects.create(
            name="Tangerang Basketball League",
            description="Liga basket di Tangerang",
            date=datetime.now() + timedelta(days=21),
            location="Tangerang Selatan",
            category="basketball",
            is_accepted=True,
            owner=self.user
        )
        
        self.event_bekasi_cycling = Event.objects.create(
            name="Bekasi Bike Tour",
            description="Gowes bareng di Bekasi",
            date=datetime.now() + timedelta(days=28),
            location="Bekasi",
            category="cycling",
            is_accepted=True,
            owner=self.user
        )
        
        # Event yang belum diterima (tidak akan muncul di discovery)
        self.event_not_accepted = Event.objects.create(
            name="Pending Event",
            description="Event yang belum disetujui",
            date=datetime.now() + timedelta(days=30),
            location="Jakarta",
            category="running",
            is_accepted=False,
            owner=self.user
        )

    # Test view render
    def test_show_discover_renders_template(self):
        """Test halaman discovery render dengan benar"""
        response = self.client.get(reverse("eventModule:show_discover"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events_filter.html")

    # Test get_filtered_events - tanpa filter
    def test_get_filtered_events_no_filter(self):
        """Test mendapatkan semua event tanpa filter"""
        response = self.client.get(reverse("eventModule:get_filtered_events"))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data["message"], "Events retrieved successfully")
        self.assertIsInstance(data["data"], list)
        # Hanya event yang is_accepted=True yang muncul (5 event)
        self.assertEqual(data["total"], 5)
        self.assertEqual(len(data["data"]), 5)

    # Test filter by location
    def test_get_filtered_events_by_location_jakarta(self):
        """Test filter event berdasarkan lokasi Jakarta"""
        response = self.client.get(reverse("eventModule:get_filtered_events") + "?location=Jakarta")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["data"][0]["name"], "Jakarta Marathon")
        self.assertEqual(data["filters_applied"]["location"], "Jakarta")

    def test_get_filtered_events_by_location_bogor(self):
        """Test filter event berdasarkan lokasi Bogor"""
        response = self.client.get(reverse("eventModule:get_filtered_events") + "?location=Bogor")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["data"][0]["name"], "Bogor Futsal Cup")
        self.assertIn("Bogor", data["data"][0]["location"])

    def test_get_filtered_events_by_location_depok(self):
        """Test filter event berdasarkan lokasi Depok"""
        response = self.client.get(reverse("eventModule:get_filtered_events") + "?location=Depok")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["data"][0]["name"], "Depok Badminton Championship")

    def test_get_filtered_events_by_location_tangerang(self):
        """Test filter event berdasarkan lokasi Tangerang"""
        response = self.client.get(reverse("eventModule:get_filtered_events") + "?location=Tangerang")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["data"][0]["name"], "Tangerang Basketball League")

    def test_get_filtered_events_by_location_bekasi(self):
        """Test filter event berdasarkan lokasi Bekasi"""
        response = self.client.get(reverse("eventModule:get_filtered_events") + "?location=Bekasi")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["data"][0]["name"], "Bekasi Bike Tour")

    def test_get_filtered_events_location_case_insensitive(self):
        """Test filter lokasi case-insensitive"""
        response = self.client.get(reverse("eventModule:get_filtered_events") + "?location=jakarta")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["data"][0]["name"], "Jakarta Marathon")

    def test_get_filtered_events_location_not_found(self):
        """Test filter dengan lokasi yang tidak ada"""
        response = self.client.get(reverse("eventModule:get_filtered_events") + "?location=Bandung")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data["total"], 0)
        self.assertEqual(len(data["data"]), 0)

    # Test filter by category
    def test_get_filtered_events_by_category_running(self):
        """Test filter event berdasarkan kategori running"""
        response = self.client.get(reverse("eventModule:get_filtered_events") + "?category=running")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["data"][0]["category"], "running")
        self.assertEqual(data["data"][0]["category_display"], "Lari")
        self.assertEqual(data["filters_applied"]["category"], "running")

    def test_get_filtered_events_by_category_futsal(self):
        """Test filter event berdasarkan kategori futsal"""
        response = self.client.get(reverse("eventModule:get_filtered_events") + "?category=futsal")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["data"][0]["category"], "futsal")

    def test_get_filtered_events_by_category_badminton(self):
        """Test filter event berdasarkan kategori badminton"""
        response = self.client.get(reverse("eventModule:get_filtered_events") + "?category=badminton")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["data"][0]["category"], "badminton")

    def test_get_filtered_events_by_category_basketball(self):
        """Test filter event berdasarkan kategori basketball"""
        response = self.client.get(reverse("eventModule:get_filtered_events") + "?category=basketball")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["data"][0]["category"], "basketball")

    def test_get_filtered_events_by_category_cycling(self):
        """Test filter event berdasarkan kategori cycling"""
        response = self.client.get(reverse("eventModule:get_filtered_events") + "?category=cycling")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["data"][0]["category"], "cycling")

    def test_get_filtered_events_category_not_found(self):
        """Test filter dengan kategori yang tidak ada eventnya"""
        response = self.client.get(reverse("eventModule:get_filtered_events") + "?category=yoga")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data["total"], 0)
        self.assertEqual(len(data["data"]), 0)

    # Test kombinasi filter
    def test_get_filtered_events_combined_location_and_category(self):
        """Test filter kombinasi lokasi dan kategori"""
        response = self.client.get(
            reverse("eventModule:get_filtered_events") + "?location=Jakarta&category=running"
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["data"][0]["name"], "Jakarta Marathon")
        self.assertEqual(data["filters_applied"]["location"], "Jakarta")
        self.assertEqual(data["filters_applied"]["category"], "running")

    def test_get_filtered_events_combined_no_match(self):
        """Test filter kombinasi yang tidak ada hasilnya"""
        response = self.client.get(
            reverse("eventModule:get_filtered_events") + "?location=Jakarta&category=futsal"
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data["total"], 0)
        self.assertEqual(len(data["data"]), 0)

    # Test event yang tidak accepted tidak muncul
    def test_get_filtered_events_only_accepted(self):
        """Test hanya event yang is_accepted=True yang muncul"""
        response = self.client.get(reverse("eventModule:get_filtered_events"))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        # Pastikan event "Pending Event" tidak muncul
        event_names = [event["name"] for event in data["data"]]
        self.assertNotIn("Pending Event", event_names)
        self.assertEqual(data["total"], 5)  # Hanya 5 event yang accepted

    # Test response structure
    def test_get_filtered_events_response_structure(self):
        """Test struktur response API"""
        response = self.client.get(reverse("eventModule:get_filtered_events"))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        
        # Check top level keys
        self.assertIn("message", data)
        self.assertIn("data", data)
        self.assertIn("total", data)
        self.assertIn("filters_applied", data)
        
        # Check event data structure
        if len(data["data"]) > 0:
            event = data["data"][0]
            self.assertIn("id", event)
            self.assertIn("name", event)
            self.assertIn("description", event)
            self.assertIn("date", event)
            self.assertIn("location", event)
            self.assertIn("category", event)
            self.assertIn("category_display", event)
            self.assertIn("thumbnail", event)
            self.assertIn("owner", event)
            self.assertIn("participants_count", event)
            
            # Check owner structure
            self.assertIn("id", event["owner"])
            self.assertIn("username", event["owner"])

    # Test get_filter_options
    def test_get_filter_options_success(self):
        """Test mendapatkan opsi filter"""
        response = self.client.get(reverse("eventModule:get_filter_options"))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data["message"], "Filter options retrieved successfully")
        self.assertIn("data", data)
        self.assertIn("locations", data["data"])
        self.assertIn("categories", data["data"])

    def test_get_filter_options_locations(self):
        """Test opsi lokasi sesuai JABODETABEK"""
        response = self.client.get(reverse("eventModule:get_filter_options"))
        data = json.loads(response.content)
        
        locations = data["data"]["locations"]
        self.assertEqual(len(locations), 5)
        self.assertIn("Jakarta", locations)
        self.assertIn("Bogor", locations)
        self.assertIn("Depok", locations)
        self.assertIn("Tangerang", locations)
        self.assertIn("Bekasi", locations)

    def test_get_filter_options_categories(self):
        """Test opsi kategori sesuai dengan model Event"""
        response = self.client.get(reverse("eventModule:get_filter_options"))
        data = json.loads(response.content)
        
        categories = data["data"]["categories"]
        self.assertEqual(len(categories), 10)
        
        # Check struktur kategori
        category_values = [cat["value"] for cat in categories]
        category_labels = [cat["label"] for cat in categories]
        
        self.assertIn("running", category_values)
        self.assertIn("badminton", category_values)
        self.assertIn("futsal", category_values)
        self.assertIn("football", category_values)
        self.assertIn("basketball", category_values)
        self.assertIn("cycling", category_values)
        self.assertIn("volleyball", category_values)
        self.assertIn("yoga", category_values)
        self.assertIn("padel", category_values)
        self.assertIn("other", category_values)
        
        # Check label dalam bahasa Indonesia
        self.assertIn("Lari", category_labels)
        self.assertIn("Badminton", category_labels)
        self.assertIn("Futsal", category_labels)

    # Test edge cases
    def test_get_filtered_events_empty_params(self):
        """Test dengan query params kosong"""
        response = self.client.get(reverse("eventModule:get_filtered_events") + "?location=&category=")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data["total"], 5)  # Semua event muncul

    def test_get_filtered_events_whitespace_params(self):
        """Test dengan query params berisi whitespace"""
        response = self.client.get(reverse("eventModule:get_filtered_events") + "?location=  &category=  ")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data["total"], 5)  # Semua event muncul

    def test_get_filtered_events_partial_location_match(self):
        """Test filter lokasi dengan partial match"""
        response = self.client.get(reverse("eventModule:get_filtered_events") + "?location=Tang")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        # Harus menemukan "Tangerang Selatan"
        self.assertEqual(data["total"], 1)
        self.assertIn("Tangerang", data["data"][0]["location"])