import pytest
from rest_framework.test import APIClient
from rest_framework import status
from domains.posts.models import Post
from django.urls import reverse
from unittest.mock import patch


from config.authentication import DummyUser

@pytest.mark.django_db
class TestPostAPIIntegration:
    """End-to-end integration tests for complete workflows."""

    def setup_method(self):
        """Setup test data before each test."""
        self.client = APIClient()
        self.list_url = reverse('post-list')
        self.author_id = "1"
        self.author_name = "Integration User"

        # Authenticate the client
        user = DummyUser()
        token = {'sub': self.author_id, 'preferred_username': self.author_name}
        self.client.force_authenticate(user=user, token=token)

    @patch('services.minio_storage.minio_storage.delete_image')
    def test_complete_post_lifecycle(self, mock_delete):
        """Test complete lifecycle: create -> read -> update -> delete."""
        mock_delete.return_value = True

        # 1. CREATE
        create_data = {
            'author_id': self.author_id,
            'author_name': self.author_name,
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

        # 3. UPDATE
        update_data = {
            'author_id': self.author_id,
            'author_name': self.author_name,
            'title': 'Updated Lifecycle Post',
            'text': 'Updated content'
        }
        update_response = self.client.put(detail_url, update_data, format='json')
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.data['title'] == 'Updated Lifecycle Post'

        # 4. DELETE
        delete_response = self.client.delete(detail_url)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify post is gone
        assert not Post.objects.filter(pk=post_id).exists()