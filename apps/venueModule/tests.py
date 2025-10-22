from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.venueModule.models import Venue
import uuid
import json


class VenueViewsTestCase(TestCase):
	def setUp(self):
		self.client = Client()
		User = get_user_model()
		self.user = User.objects.create_user(username='vtestuser', password='testpass')
		self.venue = Venue.objects.create(
			name='Test Venue',
			description='A test venue',
			location='Test City',
			thumbnail='',
			category='other',
			owner=self.user,
		)

	def test_show_venue_renders_template(self):
		resp = self.client.get(reverse('venue:show_venue'))
		self.assertEqual(resp.status_code, 200)
		self.assertTemplateUsed(resp, 'venue.html')

	def test_show_json_venue_returns_list(self):
		resp = self.client.get(reverse('venue:show_json_venue'))
		self.assertEqual(resp.status_code, 200)
		data = json.loads(resp.content)
		self.assertIsInstance(data, list)
		self.assertGreaterEqual(len(data), 1)
		# check keys
		self.assertIn('id', data[0])
		self.assertIn('name', data[0])

	def test_show_json_by_id_success(self):
		resp = self.client.get(reverse('venue:show_json_by_id_venue', args=[str(self.venue.id)]))
		self.assertEqual(resp.status_code, 200)
		data = json.loads(resp.content)
		# API returns object
		self.assertEqual(data.get('id') or data.get('data', {}).get('id'), str(self.venue.id))

	def test_show_json_by_id_not_found(self):
		random_id = uuid.uuid4()
		resp = self.client.get(reverse('venue:show_json_by_id_venue', args=[str(random_id)]))
		self.assertEqual(resp.status_code, 404)

	def test_venue_detail_page_renders(self):
		resp = self.client.get(reverse('venue:venue_detail', args=[str(self.venue.id)]))
		self.assertEqual(resp.status_code, 200)
		self.assertTemplateUsed(resp, 'venue_detail.html')

	def test_add_venue_entry_ajax_requires_login(self):
		resp = self.client.post(reverse('venue:add_venue_entry_ajax'), {})
		self.assertEqual(resp.status_code, 401)

	def test_add_venue_entry_ajax_success(self):
		self.client.login(username='vtestuser', password='testpass')
		resp = self.client.post(reverse('venue:add_venue_entry_ajax'), {
			'name': 'Created Venue',
			'description': 'desc',
			'location': 'loc',
			'thumbnail': '',
			'category': 'other',
			'is_accepted': '1'
		})
		self.assertEqual(resp.status_code, 201)
		data = json.loads(resp.content)
		self.assertIn('id', data)
		self.assertEqual(data.get('name'), 'Created Venue')

	def test_show_xml_venue_returns_xml(self):
		resp = self.client.get(reverse('venue:show_xml_venue'))
		self.assertEqual(resp.status_code, 200)
		self.assertIn(b'<?xml', resp.content[:20])

	def test_show_xml_by_id_returns_xml_or_404(self):
		resp = self.client.get(reverse('venue:show_xml_by_id_venue', args=[str(self.venue.id)]))
		self.assertIn(resp.status_code, (200, 404))

	def test_detail_template_includes_js_var(self):
		resp = self.client.get(reverse('venue:venue_detail', args=[str(self.venue.id)]))
		self.assertEqual(resp.status_code, 200)
		content = resp.content.decode('utf-8')
		# ensure VENUE_ID is present in the rendered JS
		self.assertIn(f'const VENUE_ID = "{self.venue.id}"', content)

	def test_add_venue_validation_missing_name(self):
		self.client.login(username='vtestuser', password='testpass')
		resp = self.client.post(reverse('venue:add_venue_entry_ajax'), {
			'name': '',
			'description': 'no name',
		})
		self.assertEqual(resp.status_code, 400)

	def test_add_venue_is_accepted_parsing(self):
		self.client.login(username='vtestuser', password='testpass')
		resp = self.client.post(reverse('venue:add_venue_entry_ajax'), {
			'name': 'Flagged Venue',
			'is_accepted': 'true'
		})
		self.assertEqual(resp.status_code, 201)
		data = json.loads(resp.content)
		self.assertIn('id', data)
