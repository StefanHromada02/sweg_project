"""
Unit tests for Image Resize Service
"""
import pytest
import json
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
from resize_worker import ImageResizeService


class TestImageResizeService:
    """Test cases for ImageResizeService class."""

    @pytest.fixture
    def service(self):
        """Create a service instance for testing."""
        with patch('resize_worker.boto3.client'):
            service = ImageResizeService()
            return service

    @pytest.fixture
    def sample_image(self):
        """Create a sample test image."""
        img = Image.new('RGB', (800, 600), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes

    def test_initialization(self, service):
        """Test service initialization with default values."""
        assert service.rabbitmq_host == 'rabbitmq'
        assert service.rabbitmq_port == 5672
        assert service.queue_name == 'image_resize_queue'
        assert service.minio_endpoint == 'minio:9000'
        assert service.bucket_name == 'social-media-bucket'
        assert service.thumbnail_size == (300, 300)

    def test_resize_image(self, service, sample_image):
        """Test image resizing functionality."""
        resized = service.resize_image(sample_image)

        assert resized is not None
        assert isinstance(resized, BytesIO)

        # Verify the resized image
        resized.seek(0)
        img = Image.open(resized)
        assert img.width <= 300
        assert img.height <= 300
        assert img.format == 'JPEG'

    def test_resize_image_preserves_aspect_ratio(self, service):
        """Test that resizing preserves aspect ratio."""
        # Create wide image (16:9)
        img = Image.new('RGB', (1600, 900), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        resized = service.resize_image(img_bytes)
        resized.seek(0)

        result_img = Image.open(resized)
        # Should maintain aspect ratio
        assert result_img.width == 300
        # 300 * (9/16) = 168.75 ≈ 169
        assert 165 <= result_img.height <= 172

    def test_resize_image_rgba_to_rgb(self, service):
        """Test conversion of RGBA to RGB during resize."""
        # Create RGBA image (with transparency)
        img = Image.new('RGBA', (800, 600), color=(255, 0, 0, 128))
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        resized = service.resize_image(img_bytes)
        resized.seek(0)

        result_img = Image.open(resized)
        # Should be converted to RGB (no alpha channel)
        assert result_img.mode == 'RGB'

    def test_generate_thumbnail_path(self, service):
        """Test thumbnail path generation."""
        original_path = "posts/image123.jpg"
        thumbnail_data = BytesIO(b"fake thumbnail data")

        with patch.object(service.s3_client, 'upload_fileobj') as mock_upload:
            thumbnail_path = service.upload_thumbnail(thumbnail_data, original_path)

            assert thumbnail_path == "posts/thumbnails/image123.jpg"
            mock_upload.assert_called_once()

    def test_generate_thumbnail_path_no_folder(self, service):
        """Test thumbnail path generation without folder."""
        original_path = "image123.jpg"
        thumbnail_data = BytesIO(b"fake thumbnail data")

        with patch.object(service.s3_client, 'upload_fileobj') as mock_upload:
            thumbnail_path = service.upload_thumbnail(thumbnail_data, original_path)

            assert thumbnail_path == "thumbnails/image123.jpg"
            mock_upload.assert_called_once()

    @patch('psycopg2.connect')
    def test_update_post_thumbnail(self, mock_connect, service):
        """Test updating post thumbnail in database."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        post_id = 123
        thumbnail_path = "posts/thumbnails/image.jpg"

        service.update_post_thumbnail(post_id, thumbnail_path)

        mock_cursor.execute.assert_called_once_with(
            "UPDATE posts_post SET thumbnail = %s WHERE id = %s",
            (thumbnail_path, post_id)
        )
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_download_image_success(self, service):
        """Test successful image download from MinIO."""
        mock_response = {
            'Body': MagicMock()
        }
        mock_response['Body'].read.return_value = b"fake image data"

        with patch.object(service.s3_client, 'get_object', return_value=mock_response):
            result = service.download_image("posts/image.jpg")

            assert isinstance(result, BytesIO)
            assert result.read() == b"fake image data"

    def test_upload_thumbnail_success(self, service):
        """Test successful thumbnail upload to MinIO."""
        thumbnail_data = BytesIO(b"thumbnail data")
        original_path = "posts/image.jpg"

        with patch.object(service.s3_client, 'upload_fileobj') as mock_upload:
            result_path = service.upload_thumbnail(thumbnail_data, original_path)

            assert result_path == "posts/thumbnails/image.jpg"
            mock_upload.assert_called_once()
            call_args = mock_upload.call_args
            # Check positional args: (fileobj, bucket, key)
            assert call_args.args[1] == service.bucket_name
            assert call_args.args[2] == "posts/thumbnails/image.jpg"
            assert call_args.kwargs['ExtraArgs']['ContentType'] == 'image/jpeg'

    @patch('psycopg2.connect')
    def test_process_message_success(self, mock_connect, service):
        """Test successful message processing."""
        # Setup mocks
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = 'test-tag'
        mock_properties = MagicMock()

        message = {
            'image_path': 'posts/test.jpg',
            'post_id': 42
        }
        body = json.dumps(message).encode()

        # Mock database
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock S3 operations
        mock_image_data = BytesIO()
        img = Image.new('RGB', (800, 600), color='green')
        img.save(mock_image_data, format='JPEG')
        mock_image_data.seek(0)

        with patch.object(service, 'download_image', return_value=mock_image_data):
            with patch.object(service.s3_client, 'upload_fileobj'):
                service.process_message(mock_channel, mock_method, mock_properties, body)

                # Verify message was acknowledged
                mock_channel.basic_ack.assert_called_once_with(delivery_tag='test-tag')
                mock_channel.basic_nack.assert_not_called()

    @patch('psycopg2.connect')
    def test_process_message_failure(self, mock_connect, service):
        """Test message processing with failure."""
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = 'test-tag'
        mock_properties = MagicMock()

        message = {
            'image_path': 'posts/test.jpg',
            'post_id': 42
        }
        body = json.dumps(message).encode()

        # Simulate download failure
        with patch.object(service, 'download_image', side_effect=Exception("Download failed")):
            service.process_message(mock_channel, mock_method, mock_properties, body)

            # Verify message was negatively acknowledged and requeued
            mock_channel.basic_nack.assert_called_once_with(
                delivery_tag='test-tag',
                requeue=True
            )
            mock_channel.basic_ack.assert_not_called()

    def test_resize_small_image(self, service):
        """Test that small images are not upscaled."""
        # Create small image (100x100)
        img = Image.new('RGB', (100, 100), color='yellow')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        resized = service.resize_image(img_bytes)
        resized.seek(0)

        result_img = Image.open(resized)
        # Should not be upscaled
        assert result_img.width == 100
        assert result_img.height == 100

    def test_environment_variables(self):
        """Test that environment variables are properly used."""
        env_vars = {
            'RABBITMQ_HOST': 'custom-rabbitmq',
            'RABBITMQ_PORT': '5673',
            'MINIO_ENDPOINT': 'custom-minio:9001',
            'MINIO_BUCKET': 'custom-bucket'
        }

        with patch.dict('os.environ', env_vars):
            with patch('resize_worker.boto3.client'):
                service = ImageResizeService()

                assert service.rabbitmq_host == 'custom-rabbitmq'
                assert service.rabbitmq_port == 5673
                assert service.minio_endpoint == 'custom-minio:9001'
                assert service.bucket_name == 'custom-bucket'
