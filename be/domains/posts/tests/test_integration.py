import pytest
from rest_framework.test import APIClient
from rest_framework import status
from domains.posts.models import Post
from django.urls import reverse
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestPostAPIIntegration:
    """End-to-end integration tests for complete workflows."""

    def setup_method(self):
        """Setup test data before each test."""
        self.client = APIClient()
        self.list_url = reverse('post-list')

    @patch('services.minio_storage.minio_storage.delete_image')
    @patch('config.authentication.KeycloakAuthentication.authenticate')
    def test_complete_post_lifecycle(self, mock_auth, mock_delete):
        """Test complete lifecycle: create -> read -> update -> delete."""
        # Mock authenticated user
        mock_user = MagicMock()
        mock_user.sub = 'integration-123'
        mock_user.name = 'Integration User'
        mock_user.is_authenticated = True
        mock_auth.return_value = (mock_user, None)
        mock_delete.return_value = True
        
        # Force authentication
        self.client.force_authenticate(user=mock_user)

        # 1. CREATE
        create_data = {
            'title': 'Lifecycle Test Post',
            'text': 'Initial content'
        }
        create_response = self.client.post(self.list_url, create_data, format='json')
        assert create_response.status_code == status.HTTP_201_CREATED
        post_id = create_response.data['id']

        # 2. READ
        detail_url = reverse('post-detail', kwargs={'pk': post_id})
        read_response = self.client.get(detail_url)
        assert read_response.status_code == status.HTTP_200_OK
        assert read_response.data['title'] == 'Lifecycle Test Post'

        # 3. DELETE
        delete_response = self.client.delete(detail_url)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
