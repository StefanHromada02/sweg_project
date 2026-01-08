"""
MinIO Storage Service for handling image uploads and deletions.
"""
import os
import uuid
from typing import Optional
import boto3
from botocore.exceptions import ClientError


class MinIOStorage:
    """Service class for interacting with MinIO object storage."""

    def __init__(self):
        """Prepare configuration; defer network I/O until first use."""
        # Configuration via env with sensible defaults
        # Default endpoint works in Docker Compose; override to localhost:9000 in CI/local as needed
        self.endpoint = os.getenv('MINIO_ENDPOINT', 'minio:9000')
        self.access_key = os.getenv('MINIO_ACCESS_KEY', os.getenv('MINIO_ROOT_USER', 'minio'))
        self.secret_key = os.getenv('MINIO_SECRET_KEY', os.getenv('MINIO_ROOT_PASSWORD', 'minio_admin'))
        self.bucket_name = os.getenv('MINIO_BUCKET', 'social-media-bucket')

        self.client = None  # created lazily
        self._initialized = False

    def _ensure_initialized(self):
        """Create S3 client and ensure bucket exists, once."""
        if self._initialized:
            return
        # Create S3 client (MinIO is S3-compatible)
        self.client = boto3.client(
            's3',
            endpoint_url=f"http://{self.endpoint}",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name='us-east-1'
        )
        # Ensure bucket exists
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            # Bucket doesn't exist, create it
            try:
                self.client.create_bucket(Bucket=self.bucket_name)
                print(f"Created bucket: {self.bucket_name}")
            except ClientError as e:
                print(f"Error creating bucket: {e}")
        self._initialized = True

    def upload_image(self, file, folder: str = 'posts') -> Optional[str]:
        """
        Upload an image file to MinIO.

        Args:
            file: Django UploadedFile object
            folder: Folder path in bucket (default: 'posts')

        Returns:
            str: URL path to the uploaded image, or None if upload failed
        """
        self._ensure_initialized()
        try:
            # Generate unique filename
            ext = file.name.split('.')[-1] if '.' in file.name else 'jpg'
            filename = f"{folder}/{uuid.uuid4()}.{ext}"

            # Upload file
            self.client.upload_fileobj(
                file,
                self.bucket_name,
                filename,
                ExtraArgs={'ContentType': getattr(file, 'content_type', 'application/octet-stream')}
            )

            # Return the path (URL will be constructed when serving)
            return filename

        except ClientError as e:
            print(f"Error uploading image: {e}")
            return None

    def upload_thumbnail(self, file_data, original_path: str) -> Optional[str]:
        """
        Upload a thumbnail image to MinIO.

        Args:
            file_data: BytesIO object containing the image data
            original_path: Path to the original image (used to derive thumbnail path)

        Returns:
            str: URL path to the uploaded thumbnail, or None if upload failed
        """
        self._ensure_initialized()
        try:
            # Generate thumbnail filename based on original path
            # e.g., posts/abc123.jpg -> posts/thumbnails/abc123.jpg
            parts = original_path.split('/')
            if len(parts) >= 2:
                folder = parts[0]
                filename = '/'.join(parts[1:])
                thumbnail_path = f"{folder}/thumbnails/{filename}"
            else:
                thumbnail_path = f"thumbnails/{original_path}"

            # Upload thumbnail
            file_data.seek(0)  # Reset file pointer
            self.client.upload_fileobj(
                file_data,
                self.bucket_name,
                thumbnail_path,
                ExtraArgs={'ContentType': 'image/jpeg'}
            )

            return thumbnail_path

        except ClientError as e:
            print(f"Error uploading thumbnail: {e}")
            return None

    def get_thumbnail_path(self, image_path: str) -> str:
        """
        Get the thumbnail path for a given image path.

        Args:
            image_path: Path to the original image

        Returns:
            str: Path to the thumbnail
        """
        if not image_path:
            return ""
        
        parts = image_path.split('/')
        if len(parts) >= 2:
            folder = parts[0]
            filename = '/'.join(parts[1:])
            return f"{folder}/thumbnails/{filename}"
        return f"thumbnails/{image_path}"

    def delete_image(self, image_path: str) -> bool:
        """
        Delete an image from MinIO.

        Args:
            image_path: Path to the image in the bucket

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        self._ensure_initialized()
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=image_path
            )
            return True
        except ClientError as e:
            print(f"Error deleting image: {e}")
            return False

    def get_image_url(self, image_path: str) -> str:
        """
        Get the full URL for an image.

        Args:
            image_path: Path to the image in the bucket

        Returns:
            str: Full URL to access the image
        """
        scheme = os.getenv('MINIO_SCHEME', 'http')
        return f"{scheme}://{self.endpoint}/{self.bucket_name}/{image_path}"


class MinIOStorageProxy:
    """Proxy that defers MinIO client initialization until a method is used.

    Keeps a stable object for import-time patching in tests.
    """

    def __init__(self):
        self._instance: Optional[MinIOStorage] = None

    def _get(self) -> MinIOStorage:
        if self._instance is None:
            self._instance = MinIOStorage()
        return self._instance

    # Expose methods so tests can patch attributes on this proxy
    def upload_image(self, *args, **kwargs):
        return self._get().upload_image(*args, **kwargs)

    def upload_thumbnail(self, *args, **kwargs):
        return self._get().upload_thumbnail(*args, **kwargs)

    def get_thumbnail_path(self, *args, **kwargs):
        return self._get().get_thumbnail_path(*args, **kwargs)

    def delete_image(self, *args, **kwargs):
        return self._get().delete_image(*args, **kwargs)

    def get_image_url(self, *args, **kwargs):
        return self._get().get_image_url(*args, **kwargs)


# Global proxy instance (safe to import without network calls)
minio_storage = MinIOStorageProxy()
