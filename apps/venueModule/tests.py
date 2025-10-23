from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.venueModule.models import Venue, VenueImage
import uuid
import json


class BaseVenueTestCase(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(username='tester', email='tester@example.com', password='pass')
		self.client = Client()


class VenueModelTests(BaseVenueTestCase):
	def test_create_venue_and_images_ordering(self):
		v = Venue.objects.create(
			name='My Venue',
			description='Desc',
			location='Loc',
			thumbnail='http://example.com/thumb.jpg',
			category='other',
			contact_number='0812345678',
			owner=self.user,
		)
		# create images out of order and ensure ordering by 'order' field
		VenueImage.objects.create(venue=v, image='http://example.com/1.jpg', order=2)
		VenueImage.objects.create(venue=v, image='http://example.com/0.jpg', order=0)
		VenueImage.objects.create(venue=v, image='http://example.com/2.jpg', order=1)

		imgs = list(v.images.all())
		self.assertEqual(len(imgs), 3)
		self.assertEqual(imgs[0].order, 0)
		self.assertEqual(imgs[1].order, 1)
		self.assertEqual(imgs[2].order, 2)


class VenueAPITests(BaseVenueTestCase):
	def setUp(self):
		super().setUp()
		# create a sample venue with images
		self.venue = Venue.objects.create(
			name='API Venue',
			description='API Desc',
			location='API Loc',
			thumbnail='http://example.com/thumb-api.jpg',
			category='football',
			contact_number='0812340000',
			owner=self.user,
		)
		VenueImage.objects.create(venue=self.venue, image='http://example.com/a.jpg', order=0)
		VenueImage.objects.create(venue=self.venue, image='http://example.com/b.jpg', order=1)

	def test_show_json_venue_returns_list(self):
		url = reverse('venue:show_json_venue')
		resp = self.client.get(url, HTTP_ACCEPT='application/json')
		self.assertEqual(resp.status_code, 200)
		data = json.loads(resp.content)
		# should be a list and contain our venue
		self.assertIsInstance(data, list)
		ids = [d.get('id') for d in data]
		self.assertIn(str(self.venue.id), ids)

		# find our venue payload and check images key
		payload = next((d for d in data if d.get('id') == str(self.venue.id)), None)
		self.assertIsNotNone(payload)
		self.assertIn('images', payload)
		self.assertEqual(len(payload['images']), 2)

	def test_show_json_by_id_venue_returns_detail(self):
		url = reverse('venue:show_json_by_id_venue', args=[self.venue.id])
		resp = self.client.get(url, HTTP_ACCEPT='application/json')
		self.assertEqual(resp.status_code, 200)
		payload = json.loads(resp.content)
		self.assertEqual(payload.get('id'), str(self.venue.id))
		self.assertEqual(payload.get('name'), self.venue.name)
		self.assertEqual(payload.get('category'), self.venue.category)

	def test_show_json_by_id_venue_not_found(self):
		fake = uuid.uuid4()
		url = reverse('venue:show_json_by_id_venue', args=[fake])
		resp = self.client.get(url, HTTP_ACCEPT='application/json')
		self.assertEqual(resp.status_code, 404)

class VenueViewTemplateTests(BaseVenueTestCase):
	def test_show_venue_page_renders(self):
		url = reverse('venue:show_venue')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		# ensure the template contains expected hero title text
		self.assertContains(resp, 'Found The Best Sports Venues', status_code=200)

	def test_venue_detail_page_renders(self):
		v = Venue.objects.create(
			name='Template Venue',
			description='TDesc',
			location='TLoc',
			thumbnail='',
			category='other',
			owner=self.user,
		)
		url = reverse('venue:venue_detail', args=[v.id])
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, 'Loading venue detail...', status_code=200)

class ExtendedVenueTests(BaseVenueTestCase):
	def test_show_json_fields_and_types(self):
		v = Venue.objects.create(
			name='Type Venue',
			description='D',
			location='L',
			thumbnail='http://ex/1.jpg',
			category='badminton',
			contact_number='081234567890',
			owner=self.user,
		)
		VenueImage.objects.create(venue=v, image='http://ex/a.jpg', order=0)
		url = reverse('venue:show_json_by_id_venue', args=[v.id])
		resp = self.client.get(url, HTTP_ACCEPT='application/json')
		self.assertEqual(resp.status_code, 200)
		payload = json.loads(resp.content)
		# check types
		self.assertIsInstance(payload.get('id'), str)
		self.assertIsInstance(payload.get('name'), str)
		self.assertIsInstance(payload.get('images'), list)
		# created_at must be present and ISO-like
		self.assertIn('created_at', payload)
		self.assertIsInstance(payload['created_at'], str)
		# owner_username should match
		self.assertEqual(payload.get('owner_username'), self.user.username)

	def test_images_order_in_json_matches_order_field(self):
		v = Venue.objects.create(name='Order Venue', location='O', category='other', owner=self.user)
		VenueImage.objects.create(venue=v, image='http://ex/1.jpg', order=2)
		VenueImage.objects.create(venue=v, image='http://ex/0.jpg', order=0)
		VenueImage.objects.create(venue=v, image='http://ex/2.jpg', order=1)
		url = reverse('venue:show_json_by_id_venue', args=[v.id])
		resp = self.client.get(url, HTTP_ACCEPT='application/json')
		payload = json.loads(resp.content)
		imgs = payload.get('images')
		# images in JSON should be ordered by order field defined in model Meta
		self.assertEqual(imgs, ['http://ex/0.jpg', 'http://ex/2.jpg', 'http://ex/1.jpg'])

	def test_venue_detail_view_context_has_venue(self):
		v = Venue.objects.create(name='Ctx Venue', location='C', category='other', owner=self.user)
		url = reverse('venue:venue_detail', args=[v.id])
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		# the view passes 'venue' in context
		self.assertIn('venue', resp.context)
		self.assertEqual(resp.context['venue'].id, v.id)

	def test_show_json_owner_none_when_no_owner(self):
		v = Venue.objects.create(name='NoOwner', location='N', category='other', owner=None)
		url = reverse('venue:show_json_by_id_venue', args=[v.id])
		resp = self.client.get(url, HTTP_ACCEPT='application/json')
		payload = json.loads(resp.content)
		self.assertIsNone(payload.get('owner_username'))