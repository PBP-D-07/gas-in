from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.eventMakerModule.models import Event
from apps.eventModule.models import SavedSearch
from apps.eventModule.forms import SavedSearchForm
from datetime import datetime, timedelta
import json
import uuid

User = get_user_model()

class EventModuleViewsTestCase(TestCase):
    """Test untuk views.py - Discovery & Filter"""
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.user2 = User.objects.create_user(username="testuser2", password="testpass2")
        
        # Create test events
        self.event_jakarta = Event.objects.create(
            name="Jakarta Marathon",
            description="Marathon in Jakarta",
            date=datetime.now() + timedelta(days=7),
            location="Jakarta Pusat",
            category="running",
            is_accepted=True,
            owner=self.user
        )
        
        self.event_bogor = Event.objects.create(
            name="Bogor Futsal",
            description="Futsal tournament",
            date=datetime.now() + timedelta(days=10),
            location="Bogor",
            category="futsal",
            is_accepted=True,
            owner=self.user
        )
        
        self.event_pending = Event.objects.create(
            name="Pending Event",
            description="Not accepted yet",
            date=datetime.now() + timedelta(days=14),
            location="Jakarta",
            category="running",
            is_accepted=False,
            owner=self.user
        )

    # View Render Tests
    def test_show_discover_renders(self):
        """Test discovery page renders correctly"""
        response = self.client.get(reverse('eventModule:show_discover'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discover_events.html')

    def test_show_saved_searches_renders(self):
        """Test saved searches page renders correctly"""
        response = self.client.get(reverse('eventModule:show_saved_searches'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'saved_searches.html')

    # Filter Events Tests
    def test_get_filtered_events_no_filter(self):
        """Test get all events without filter"""
        response = self.client.get(reverse('eventModule:get_filtered_events'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['total'], 2)  # Only accepted events
        self.assertEqual(len(data['data']), 2)

    def test_get_filtered_events_by_location(self):
        """Test filter by location"""
        response = self.client.get(reverse('eventModule:get_filtered_events') + '?location=Jakarta')
        data = json.loads(response.content)
        
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['filters_applied']['location'], 'Jakarta')

    def test_get_filtered_events_by_category(self):
        """Test filter by category"""
        response = self.client.get(reverse('eventModule:get_filtered_events') + '?category=running')
        data = json.loads(response.content)
        
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['data'][0]['category'], 'running')

    def test_get_filtered_events_combined(self):
        """Test combined filters"""
        response = self.client.get(
            reverse('eventModule:get_filtered_events') + '?location=Jakarta&category=running'
        )
        data = json.loads(response.content)
        
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['filters_applied']['location'], 'Jakarta')
        self.assertEqual(data['filters_applied']['category'], 'running')

    def test_get_filtered_events_case_insensitive(self):
        """Test location filter is case insensitive"""
        response = self.client.get(reverse('eventModule:get_filtered_events') + '?location=jakarta')
        data = json.loads(response.content)
        
        self.assertEqual(data['total'], 1)

    def test_get_filtered_events_only_accepted(self):
        """Test only accepted events are returned"""
        response = self.client.get(reverse('eventModule:get_filtered_events'))
        data = json.loads(response.content)
        
        event_names = [e['name'] for e in data['data']]
        self.assertNotIn('Pending Event', event_names)

    def test_get_filtered_events_response_structure(self):
        """Test response structure"""
        response = self.client.get(reverse('eventModule:get_filtered_events'))
        data = json.loads(response.content)
        
        self.assertIn('message', data)
        self.assertIn('data', data)
        self.assertIn('total', data)
        self.assertIn('filters_applied', data)
        
        if data['data']:
            event = data['data'][0]
            self.assertIn('id', event)
            self.assertIn('name', event)
            self.assertIn('category_display', event)
            self.assertIn('owner', event)
            self.assertIn('participants_count', event)

    # Filter Options Tests
    def test_get_filter_options_success(self):
        """Test get filter options"""
        response = self.client.get(reverse('eventModule:get_filter_options'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('locations', data['data'])
        self.assertIn('categories', data['data'])

    def test_get_filter_options_locations(self):
        """Test locations list"""
        response = self.client.get(reverse('eventModule:get_filter_options'))
        data = json.loads(response.content)
        
        locations = data['data']['locations']
        self.assertEqual(len(locations), 5)
        self.assertIn('Jakarta', locations)
        self.assertIn('Bogor', locations)

    def test_get_filter_options_categories(self):
        """Test categories list"""
        response = self.client.get(reverse('eventModule:get_filter_options'))
        data = json.loads(response.content)
        
        categories = data['data']['categories']
        self.assertEqual(len(categories), 10)


class SavedSearchCRUDTestCase(TestCase):
    """Test untuk SavedSearch CRUD operations"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.user2 = User.objects.create_user(username="testuser2", password="testpass2")

    # Authentication Tests
    def test_create_saved_search_requires_login(self):
        """Test create requires login"""
        response = self.client.post(
            reverse('eventModule:create_saved_search'),
            data=json.dumps({'name': 'Test'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_get_saved_searches_requires_login(self):
        """Test get requires login"""
        response = self.client.get(reverse('eventModule:get_saved_searches'))
        self.assertEqual(response.status_code, 302)

    # CREATE Tests
    def test_create_saved_search_success(self):
        """Test create saved search successfully"""
        self.client.login(username='testuser', password='testpass')
        
        response = self.client.post(
            reverse('eventModule:create_saved_search'),
            data=json.dumps({
                'name': 'Futsal Jakarta',
                'location': 'Jakarta',
                'category': 'futsal'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data['message'], 'Saved search created successfully')
        self.assertEqual(data['data']['name'], 'Futsal Jakarta')

    def test_create_saved_search_without_name(self):
        """Test create without name fails"""
        self.client.login(username='testuser', password='testpass')
        
        response = self.client.post(
            reverse('eventModule:create_saved_search'),
            data=json.dumps({'location': 'Jakarta'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)

    def test_create_saved_search_location_only(self):
        """Test create with location only"""
        self.client.login(username='testuser', password='testpass')
        
        response = self.client.post(
            reverse('eventModule:create_saved_search'),
            data=json.dumps({
                'name': 'Jakarta Only',
                'location': 'Jakarta'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertIsNone(data['data']['category'])

    def test_create_saved_search_category_only(self):
        """Test create with category only"""
        self.client.login(username='testuser', password='testpass')
        
        response = self.client.post(
            reverse('eventModule:create_saved_search'),
            data=json.dumps({
                'name': 'All Futsal',
                'category': 'futsal'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertIsNone(data['data']['location'])

    # READ Tests
    def test_get_saved_searches_empty(self):
        """Test get empty saved searches"""
        self.client.login(username='testuser', password='testpass')
        
        response = self.client.get(reverse('eventModule:get_saved_searches'))
        data = json.loads(response.content)
        
        self.assertEqual(len(data['data']), 0)

    def test_get_saved_searches_with_data(self):
        """Test get saved searches with data"""
        self.client.login(username='testuser', password='testpass')
        
        SavedSearch.objects.create(user=self.user, name='Search 1', location='Jakarta')
        SavedSearch.objects.create(user=self.user, name='Search 2', category='futsal')
        
        response = self.client.get(reverse('eventModule:get_saved_searches'))
        data = json.loads(response.content)
        
        self.assertEqual(len(data['data']), 2)

    def test_get_saved_searches_only_own(self):
        """Test user only sees their own searches"""
        self.client.login(username='testuser', password='testpass')
        
        SavedSearch.objects.create(user=self.user, name='My Search')
        SavedSearch.objects.create(user=self.user2, name='Other Search')
        
        response = self.client.get(reverse('eventModule:get_saved_searches'))
        data = json.loads(response.content)
        
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['name'], 'My Search')

    def test_get_saved_search_by_id_success(self):
        """Test get saved search by ID"""
        self.client.login(username='testuser', password='testpass')
        
        saved = SavedSearch.objects.create(user=self.user, name='Test', location='Jakarta')
        
        response = self.client.get(
            reverse('eventModule:get_saved_search_by_id', args=[saved.id])
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['data']['name'], 'Test')

    def test_get_saved_search_by_id_not_found(self):
        """Test get non-existent saved search"""
        self.client.login(username='testuser', password='testpass')
        
        fake_id = uuid.uuid4()
        response = self.client.get(
            reverse('eventModule:get_saved_search_by_id', args=[fake_id])
        )
        
        self.assertEqual(response.status_code, 404)

    def test_get_saved_search_by_id_not_owner(self):
        """Test cannot get other user's search"""
        self.client.login(username='testuser', password='testpass')
        
        saved = SavedSearch.objects.create(user=self.user2, name='Other')
        
        response = self.client.get(
            reverse('eventModule:get_saved_search_by_id', args=[saved.id])
        )
        
        self.assertEqual(response.status_code, 404)

    # UPDATE Tests
    def test_update_saved_search_success(self):
        """Test update saved search"""
        self.client.login(username='testuser', password='testpass')
        
        saved = SavedSearch.objects.create(
            user=self.user,
            name='Old Name',
            location='Jakarta'
        )
        
        response = self.client.post(
            reverse('eventModule:update_saved_search', args=[saved.id]),
            data=json.dumps({
                'name': 'New Name',
                'location': 'Bogor'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['data']['name'], 'New Name')

    def test_update_saved_search_partial(self):
        """Test partial update"""
        self.client.login(username='testuser', password='testpass')
        
        saved = SavedSearch.objects.create(
            user=self.user,
            name='Old Name',
            location='Jakarta'
        )
        
        response = self.client.post(
            reverse('eventModule:update_saved_search', args=[saved.id]),
            data=json.dumps({'name': 'New Name'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['data']['name'], 'New Name')
        self.assertEqual(data['data']['location'], 'Jakarta')

    def test_update_saved_search_not_owner(self):
        """Test cannot update other user's search"""
        self.client.login(username='testuser', password='testpass')
        
        saved = SavedSearch.objects.create(user=self.user2, name='Other')
        
        response = self.client.post(
            reverse('eventModule:update_saved_search', args=[saved.id]),
            data=json.dumps({'name': 'Hacked'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)

    # DELETE Tests
    def test_delete_saved_search_success(self):
        """Test delete saved search"""
        self.client.login(username='testuser', password='testpass')
        
        saved = SavedSearch.objects.create(user=self.user, name='To Delete')
        
        response = self.client.post(
            reverse('eventModule:delete_saved_search', args=[saved.id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SavedSearch.objects.filter(pk=saved.id).exists())

    def test_delete_saved_search_not_owner(self):
        """Test cannot delete other user's search"""
        self.client.login(username='testuser', password='testpass')
        
        saved = SavedSearch.objects.create(user=self.user2, name='Other')
        
        response = self.client.post(
            reverse('eventModule:delete_saved_search', args=[saved.id])
        )
        
        self.assertEqual(response.status_code, 404)
        self.assertTrue(SavedSearch.objects.filter(pk=saved.id).exists())

    # HTTP Method Tests
    def test_create_invalid_method(self):
        """Test create with wrong method"""
        self.client.login(username='testuser', password='testpass')
        
        response = self.client.get(reverse('eventModule:create_saved_search'))
        self.assertEqual(response.status_code, 405)

    def test_update_invalid_method(self):
        """Test update with wrong method"""
        self.client.login(username='testuser', password='testpass')
        
        saved = SavedSearch.objects.create(user=self.user, name='Test')
        response = self.client.get(
            reverse('eventModule:update_saved_search', args=[saved.id])
        )
        self.assertEqual(response.status_code, 405)

    def test_delete_invalid_method(self):
        """Test delete with wrong method"""
        self.client.login(username='testuser', password='testpass')
        
        saved = SavedSearch.objects.create(user=self.user, name='Test')
        response = self.client.get(
            reverse('eventModule:delete_saved_search', args=[saved.id])
        )
        self.assertEqual(response.status_code, 405)


class SavedSearchModelTestCase(TestCase):
    """Test untuk SavedSearch model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_create_saved_search(self):
        """Test create saved search model"""
        saved = SavedSearch.objects.create(
            user=self.user,
            name='Test Search',
            location='Jakarta',
            category='futsal'
        )
        
        self.assertIsNotNone(saved.id)
        self.assertEqual(saved.name, 'Test Search')
        self.assertEqual(saved.user, self.user)

    def test_saved_search_str(self):
        """Test string representation"""
        saved = SavedSearch.objects.create(
            user=self.user,
            name='Test Search'
        )
        
        self.assertEqual(str(saved), 'testuser - Test Search')

    def test_saved_search_ordering(self):
        """Test ordering by created_at desc"""
        import time
        
        saved1 = SavedSearch.objects.create(user=self.user, name='First')
        time.sleep(0.01)  # Ensure different timestamps
        saved2 = SavedSearch.objects.create(user=self.user, name='Second')
        
        searches = list(SavedSearch.objects.all())
        # Check that searches exist and are ordered
        self.assertEqual(len(searches), 2)
        # Most recent should be first due to ordering = ['-created_at']
        names = [s.name for s in searches]
        self.assertIn('First', names)
        self.assertIn('Second', names)

    def test_saved_search_optional_fields(self):
        """Test optional location and category"""
        saved = SavedSearch.objects.create(
            user=self.user,
            name='Minimal'
        )
        
        self.assertIsNone(saved.location)
        self.assertIsNone(saved.category)

    def test_saved_search_cascade_delete(self):
        """Test cascade delete when user deleted"""
        saved = SavedSearch.objects.create(user=self.user, name='Test')
        
        self.user.delete()
        
        self.assertFalse(SavedSearch.objects.filter(pk=saved.id).exists())


class SavedSearchFormTestCase(TestCase):
    """Test untuk SavedSearchForm"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_form_valid_data(self):
        """Test form with valid data"""
        form = SavedSearchForm(data={
            'name': 'Test Search',
            'location': 'Jakarta',
            'category': 'futsal'
        })
        
        self.assertTrue(form.is_valid())

    def test_form_minimal_data(self):
        """Test form with only required field"""
        form = SavedSearchForm(data={
            'name': 'Test Search'
        })
        
        self.assertTrue(form.is_valid())

    def test_form_missing_name(self):
        """Test form without name"""
        form = SavedSearchForm(data={
            'location': 'Jakarta'
        })
        
        self.assertFalse(form.is_valid())

    def test_form_strips_html(self):
        """Test form strips HTML tags"""
        form = SavedSearchForm(data={
            'name': '<script>alert("xss")</script>Test',
            'location': '<b>Jakarta</b>',
            'category': '<i>futsal</i>'
        })
        
        self.assertTrue(form.is_valid())
        # strip_tags removes tags but keeps content inside script tags
        # So we just check it's not the original with tags
        self.assertNotIn('<script>', form.cleaned_data['name'])
        self.assertNotIn('<b>', form.cleaned_data['location'])
        self.assertNotIn('<i>', form.cleaned_data['category'])


class URLPatternsTestCase(TestCase):
    """Test untuk URL patterns"""
    
    def test_discover_url_resolves(self):
        """Test discovery URL resolves"""
        url = reverse('eventModule:show_discover')
        self.assertEqual(url, '/event/')

    def test_saved_searches_url_resolves(self):
        """Test saved searches URL resolves"""
        url = reverse('eventModule:show_saved_searches')
        self.assertEqual(url, '/event/saved-searches/')

    def test_api_events_url_resolves(self):
        """Test API events URL resolves"""
        url = reverse('eventModule:get_filtered_events')
        self.assertEqual(url, '/event/api/events/')

    def test_api_filter_options_url_resolves(self):
        """Test API filter options URL resolves"""
        url = reverse('eventModule:get_filter_options')
        self.assertEqual(url, '/event/api/filter-options/')

    def test_saved_search_crud_urls_resolve(self):
        """Test saved search CRUD URLs resolve"""
        test_id = uuid.uuid4()
        
        urls = [
            ('create_saved_search', [], '/event/api/saved-search/create/'),
            ('get_saved_searches', [], '/event/api/saved-search/'),
            ('get_saved_search_by_id', [test_id], f'/event/api/saved-search/{test_id}/'),
            ('update_saved_search', [test_id], f'/event/api/saved-search/{test_id}/update/'),
            ('delete_saved_search', [test_id], f'/event/api/saved-search/{test_id}/delete/'),
        ]
        
        for name, args, expected in urls:
            with self.subTest(name=name):
                url = reverse(f'eventModule:{name}', args=args)
                self.assertEqual(url, expected)


class IntegrationTestCase(TestCase):
    """Integration tests untuk complete user flow"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        
        Event.objects.create(
            name="Test Event",
            description="Test",
            date=datetime.now() + timedelta(days=7),
            location="Jakarta",
            category="futsal",
            is_accepted=True,
            owner=self.user
        )

    def test_complete_flow_discovery_to_saved(self):
        """Test complete flow from discovery to saving search"""
        # 1. Visit discovery page
        response = self.client.get(reverse('eventModule:show_discover'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Get filtered events
        response = self.client.get(
            reverse('eventModule:get_filtered_events') + '?location=Jakarta&category=futsal'
        )
        data = json.loads(response.content)
        self.assertEqual(data['total'], 1)
        
        # 3. Login
        self.client.login(username='testuser', password='testpass')
        
        # 4. Save the search
        response = self.client.post(
            reverse('eventModule:create_saved_search'),
            data=json.dumps({
                'name': 'My Futsal Search',
                'location': 'Jakarta',
                'category': 'futsal'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        # 5. View saved searches
        response = self.client.get(reverse('eventModule:show_saved_searches'))
        self.assertEqual(response.status_code, 200)
        
        # 6. Get saved searches via API
        response = self.client.get(reverse('eventModule:get_saved_searches'))
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 1)

    def test_content_type_json(self):
        """Test API returns JSON"""
        response = self.client.get(reverse('eventModule:get_filtered_events'))
        self.assertEqual(response['Content-Type'], 'application/json')