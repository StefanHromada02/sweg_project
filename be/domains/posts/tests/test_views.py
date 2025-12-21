import pytest
from rest_framework.test import APIClient
from rest_framework import status
from domains.posts.models import Post
from django.urls import reverse
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestPostViewSet:
    """Tests for basic CRUD operations."""

    def setup_method(self):
        """Setup test data before each test."""
        self.client = APIClient()
        self.post = Post.objects.create(
            author_id="api-user-123",
            author_name="API User",
            title="API Test Post",
            text="Content for API test.",
            image="posts/test.jpg"
        )
        self.list_url = reverse('post-list')
        self.detail_url = reverse('post-detail', kwargs={'pk': self.post.pk})

    @patch('config.authentication.KeycloakAuthentication.authenticate')
    def test_get_post_list(self, mock_auth):
        """Test GET /api/posts/ returns list of posts."""
        # Mock authenticated user
        mock_user = MagicMock()
        mock_user.sub = 'test-user-123'
        mock_user.name = 'Test User'
        mock_user.is_authenticated = True
        mock_auth.return_value = (mock_user, None)
        
        # Force authentication
        self.client.force_authenticate(user=mock_user)
        
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    @patch('config.authentication.KeycloakAuthentication.authenticate')
    def test_get_post_detail(self, mock_auth):
        """Test GET /api/posts/<pk>/ returns single post."""
        # Mock authenticated user
        mock_user = MagicMock()
        mock_user.sub = 'test-user-123'
        mock_user.name = 'Test User'
        mock_user.is_authenticated = True
        mock_auth.return_value = (mock_user, None)
        
        # Force authentication
        self.client.force_authenticate(user=mock_user)
        
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == "API Test Post"

    @patch('config.authentication.KeycloakAuthentication.authenticate')
    def test_create_post_without_image(self, mock_auth):
        """Test POST /api/posts/ creates post without image."""
        # Mock authenticated user
        mock_user = MagicMock()
        mock_user.sub = 'test-123'
        mock_user.name = 'Test User'
        mock_user.is_authenticated = True
        mock_auth.return_value = (mock_user, None)
        
        # Force authentication
        self.client.force_authenticate(user=mock_user)
        
        data = {
            "title": "New Post",
            "text": "Test content"
        }
        response = self.client.post(self.list_url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == "New Post"
