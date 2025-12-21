import pytest
from domains.posts.serializers import PostSerializer
from domains.posts.models import Post


@pytest.mark.django_db
class TestPostSerializer:
    """Tests for PostSerializer validation and serialization."""

    def test_serializer_with_valid_data(self):
        """Test deserialization (validation) of correct data."""
        valid_data = {
            "author_id": "test-user-123",
            "author_name": "Test User",
            "title": "A valid title",
            "text": "Valid text content."
        }
        
        serializer = PostSerializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors

    def test_serializer_with_invalid_data_missing_title(self):
        """Test serializer detects missing required fields (e.g. title)."""
        invalid_data = {
            "author_id": "test-user-123",
            "author_name": "Test User",
            "text": "Missing the title."
        }
        
        serializer = PostSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors

    def test_serializer_with_invalid_data_missing_text(self):
        """Test serializer detects missing text field."""
        invalid_data = {
            "author_id": "test-user-123",
            "author_name": "Test User",
            "title": "Title without text."
        }
        
        serializer = PostSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'text' in serializer.errors

    def test_serialize_existing_post(self):
        """Test serialization of an existing Post instance."""
        post = Post.objects.create(
            author_id="test-user-123",
            author_name="Test User",
            title="Sample Post",
            text="Sample text.",
            image="posts/sample.jpg"
        )
        serializer = PostSerializer(instance=post)
        data = serializer.data
        
        assert data['id'] == post.id
        assert data['title'] == "Sample Post"
        assert data['text'] == "Sample text."
        assert data['author_id'] == "test-user-123"
        assert data['author_name'] == "Test User"
