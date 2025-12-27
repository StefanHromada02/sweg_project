import pytest
from domains.posts.models import Post
import time


@pytest.mark.django_db
class TestPostModel:
    """Tests for Post model."""

    def test_post_creation(self):
        """Test creating a post."""
        post = Post.objects.create(
            author_id="test-user-123",
            author_name="Test User",
            title="Test Post",
            text="This is a test post.",
            image="posts/test.jpg"
        )
        
        assert post.id is not None
        assert post.title == "Test Post"
        assert post.author_id == "test-user-123"
        assert post.author_name == "Test User"
        assert str(post) == "Test Post by Test User"

    def test_manager_newest_first(self, transactional_db):
        """Test that PostManager returns posts sorted by newest first."""
        # Clear any existing posts to ensure clean test
        Post.objects.all().delete()
        
        post_older = Post.objects.create(
            author_id="test-user-123",
            author_name="Test User",
            title="Older Post",
            text="This is an older post.",
            image=""
        )
        time.sleep(0.01)
        post_newer = Post.objects.create(
            author_id="test-user-123",
            author_name="Test User",
            title="Newer Post",
            text="This is a newer post.",
            image=""
        )
        
        posts = Post.objects.newest_first()
        assert posts.count() == 2
        assert posts.first() == post_newer
        assert posts.last() == post_older