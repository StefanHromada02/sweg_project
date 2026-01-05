import pytest
from domains.posts.serializers import PostSerializer
from domains.posts.models import Post


@pytest.mark.django_db
class TestPostSerializer:
    """Tests for PostSerializer validation and serialization."""

    def test_serializer_with_valid_data(self):
        """Test deserialization (validation) of correct data."""
        valid_data = {
            "author_id": "1",
            "author_name": "Test User",
            "title": "A valid title",
            "text": "Valid text content."
        }
        
        serializer = PostSerializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors

    def test_serializer_with_invalid_data_missing_title(self):
        """Test serializer detects missing required fields (e.g. title)."""
        invalid_data = {
            "author_id": "1",
            "author_name": "Test User",
            "text": "Missing the title."
        }
        
        serializer = PostSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors

    def test_serializer_with_invalid_data_missing_text(self):
        """Test serializer detects missing text field."""
        data = {
            "author_id": "1",
            "author_name": "Test User",
            "title": "Only Title"
        }
        serializer = PostSerializer(data=data)
        assert not serializer.is_valid()
        assert 'text' in serializer.errors

    def test_serializer_output_format(self):
        """Test serializer output includes all expected fields."""
        post = Post.objects.create(
            author_id="1",
            author_name="Test User",
            title="Test Post",
            text="Test Content",
            image="posts/test.jpg"
        )
        
        serializer = PostSerializer(post)
        data = serializer.data
        
        assert 'id' in data
        assert 'author_id' in data
        assert 'author_name' in data
        assert 'title' in data
        assert 'text' in data
        assert 'image' in data
        assert 'created_at' in data
        assert data['title'] == "Test Post"
        assert data['image'].endswith("posts/test.jpg")
