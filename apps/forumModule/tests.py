import json
import os
import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from apps.forumModule.models import Post, Comment
from unittest.mock import patch, mock_open

User = get_user_model()


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.post = Post.objects.create(description='Test post', category='running', owner=self.user)
    
    def test_post_creation(self):
        self.assertEqual(self.post.description, 'Test post')
        self.assertTrue(isinstance(self.post.id, uuid.UUID))
    
    def test_is_post_hot(self):
        self.assertFalse(self.post.is_post_hot)
        self.post.post_views = 25
        self.assertTrue(self.post.is_post_hot)
    
    def test_increment_views(self):
        initial = self.post.post_views
        self.post.increment_views
        self.post.refresh_from_db()
        self.assertEqual(self.post.post_views, initial + 1)
    
    def test_like_count(self):
        self.assertEqual(self.post.like_count(), 0)
        self.post.likes.add(self.user)
        self.assertEqual(self.post.like_count(), 1)


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.post = Post.objects.create(description='Test', category='running', owner=self.user)
        self.comment = Comment.objects.create(post=self.post, author=self.user, content='Test comment')
    
    def test_comment_creation(self):
        self.assertEqual(self.comment.content, 'Test comment')
        self.assertEqual(self.comment.author, self.user)


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.post = Post.objects.create(description='Test post', category='running', owner=self.user)
    
    def test_show_main(self):
        response = self.client.get(reverse('forumModule:show_main'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forumMain.html')
    
    def test_show_main_filter(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('forumModule:show_main') + '?filter=my')
        self.assertEqual(response.status_code, 200)
    
    def test_show_post(self):
        response = self.client.get(reverse('forumModule:show_post', kwargs={'post_id': str(self.post.id)}))
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.post_views, 1)
    
    def test_show_post_404(self):
        response = self.client.get(reverse('forumModule:show_post', kwargs={'post_id': 'invalid'}))
        self.assertEqual(response.status_code, 404)
    
    def test_create_post(self):
        self.client.login(username='testuser', password='testpass123')
        data = {'description': 'New post', 'category': 'running'}
        response = self.client.post(reverse('forumModule:create_post'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(description='New post').exists())
    
    def test_create_post_ajax(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('forumModule:create_post'),
            {'description': 'AJAX post', 'category': 'workout'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('post_id', json.loads(response.content))
    
    def test_create_post_invalid(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('forumModule:create_post'),
            {'description': ''},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_edit_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('forumModule:edit_post', kwargs={'id': self.post.id}),
            {'description': 'Updated', 'category': 'workout'}
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.description, 'Updated')
    
    def test_edit_post_ajax(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('forumModule:edit_post', kwargs={'id': self.post.id}),
            {'description': 'Updated', 'category': 'workout'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_edit_post_not_owner(self):
        other_user = User.objects.create_user(username='other', password='testpass123')
        self.client.login(username='other', password='testpass123')
        response = self.client.post(
            reverse('forumModule:edit_post', kwargs={'id': self.post.id}),
            {'description': 'Hack'}
        )
        self.assertEqual(response.status_code, 404)
    
    def test_delete_post(self):
        self.client.login(username='testuser', password='testpass123')
        post_id = self.post.id
        response = self.client.post(reverse('forumModule:delete_post', kwargs={'id': post_id}))
        self.assertFalse(Post.objects.filter(id=post_id).exists())
    
    def test_delete_post_ajax(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('forumModule:delete_post', kwargs={'id': self.post.id}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_toggle_like(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('forumModule:toggle_like', kwargs={'post_id': self.post.id}))
        data = json.loads(response.content)
        self.assertTrue(data['liked'])
        self.assertEqual(data['like_count'], 1)
    
    def test_toggle_unlike(self):
        self.client.login(username='testuser', password='testpass123')
        self.post.likes.add(self.user)
        response = self.client.get(reverse('forumModule:toggle_like', kwargs={'post_id': self.post.id}))
        data = json.loads(response.content)
        self.assertFalse(data['liked'])
    
    def test_check_user_liked_exception(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('forumModule:check_user_liked', kwargs={'post_id': uuid.uuid4()}))
        data = json.loads(response.content)
        self.assertFalse(data['liked'])
    
    def test_add_comment(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('forumModule:add_comment', kwargs={'post_id': self.post.id}),
            {'content': 'Nice post!'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Comment.objects.filter(content='Nice post!').exists())
    
    def test_add_comment_empty(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('forumModule:add_comment', kwargs={'post_id': self.post.id}),
            {'content': '   '}
        )
        self.assertEqual(response.status_code, 400)
    
    def test_get_comments(self):
        Comment.objects.create(post=self.post, author=self.user, content='Test')
        response = self.client.get(reverse('forumModule:get_comments', kwargs={'post_id': str(self.post.id)}))
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
    
    def test_get_comments_non_uuid(self):
        with patch('builtins.open', mock_open(read_data='[{"id": "123", "comments": [{"user": "test"}]}]')):
            response = self.client.get(reverse('forumModule:get_comments', kwargs={'post_id': '123'}))
            self.assertEqual(response.status_code, 200)
    
    def test_get_comments_404(self):
        response = self.client.get(reverse('forumModule:get_comments', kwargs={'post_id': 'notfound'}))
        self.assertEqual(response.status_code, 404)
    
    def test_show_json(self):
        response = self.client.get(reverse('forumModule:show_json'))
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_show_json_by_id(self):
        response = self.client.get(reverse('forumModule:show_json_by_id', kwargs={'post_id': str(self.post.id)}))
        data = json.loads(response.content)
        self.assertEqual(data['description'], 'Test post')
    
    @patch('builtins.open', mock_open(read_data='[{"id": "999", "description": "JSON post"}]'))
    def test_show_json_by_id_from_file(self):
        response = self.client.get(reverse('forumModule:show_json_by_id', kwargs={'post_id': '999'}))
        data = json.loads(response.content)
        self.assertEqual(data['description'], 'JSON post')
    
    def test_show_json_by_id_404(self):
        response = self.client.get(reverse('forumModule:show_json_by_id', kwargs={'post_id': 'notfound'}))
        self.assertEqual(response.status_code, 404)

