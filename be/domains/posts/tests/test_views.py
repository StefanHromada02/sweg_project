import pytest
from rest_framework.test import APIClient
from rest_framework import status
from domains.posts.models import Post
from django.urls import reverse
from unittest.mock import patch


from config.authentication import DummyUser

@pytest.mark.django_db
class TestPostViewSet:
    """Tests for basic CRUD operations."""

    def setup_method(self):
        """Setup test data before each test."""
        self.client = APIClient()
        self.author_id = "1"
        self.author_name = "API User"

        # Authenticate the client
        user = DummyUser()
        token = {'sub': self.author_id, 'preferred_username': self.author_name}
        self.client.force_authenticate(user=user, token=token)

        self.post = Post.objects.create(
            author_id=self.author_id,
            author_name=self.author_name,
            title="API Test Post",
            text="Content for API test.",
            image="posts/test.jpg"
        )
        self.list_url = reverse('post-list')
        self.detail_url = reverse('post-detail', kwargs={'pk': self.post.pk})

    def test_get_post_list(self):
        """Test GET /api/posts/ returns list of posts."""
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_get_post_detail(self):
        """Test GET /api/posts/<pk>/ returns single post."""
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == "API Test Post"

    def test_create_post_without_image(self):
        """Test POST /api/posts/ creates post without image."""
        data = {
            "author_id": self.author_id,
            "author_name": self.author_name,
            "title": "New Post",
            "text": "Test content"
        }
        response = self.client.post(self.list_url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == "New Post"
        assert response.data['image'] is None

    def test_create_post_invalid_data(self):
        """Test POST /api/posts/ with missing required fields."""
        data = {
            "text": "Missing the title"
        }
        response = self.client.post(self.list_url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data

    def test_update_post(self):
        """Test PUT /api/posts/<pk>/ updates post."""
        data = {
            "author_id": self.author_id,
            "author_name": self.author_name,
            "title": "Updated Title",
            "text": "Updated content"
        }
        response = self.client.put(self.detail_url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == "Updated Title"
        
        # Verify in database
        self.post.refresh_from_db()
        assert self.post.title == "Updated Title"

    @patch('services.minio_storage.minio_storage.delete_image')
    def test_delete_post(self, mock_delete):
        """Test DELETE /api/posts/<pk>/ deletes post."""
        mock_delete.return_value = True
        
        response = self.client.delete(self.detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Post.objects.filter(pk=self.post.pk).exists()

    def test_get_nonexistent_post(self):
        """Test GET /api/posts/999/ returns 404."""
        url = reverse('post-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND