import pytest
from unittest.mock import patch
from domains.posts.models import Post


class TestPostSimple:
    """Simple unit tests for Post model."""

    @patch("domains.posts.models.Post.objects.create")
    def test_create_post_mocked(self, mock_create_post):
        """Test creating a post with mocked database."""
        # Arrange – Fake Post
        fake_post = Post(
            id=1,
            author_id="alice-123",
            author_name="Alice",
            title="Hello World",
            text="This is my first post!",
            image="https://example.com/image.jpg",
        )
        mock_create_post.return_value = fake_post

        # Act
        post = Post.objects.create(
            author_id="alice-123",
            author_name="Alice",
            title="Hello World",
            text="This is my first post!",
            image="https://example.com/image.jpg",
        )

        # Assert
        assert post.id == 1
        assert post.author_name == "Alice"
        assert str(post) == "Hello World by Alice"
        assert mock_create_post.call_count == 1