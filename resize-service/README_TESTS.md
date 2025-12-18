# Resize Service Tests

This directory contains unit tests for the image resize microservice.

## Test Coverage

The test suite covers:

### Core Functionality
- ✅ **Image Resizing**: Test image resize to 300x300 thumbnail
- ✅ **Aspect Ratio**: Verify aspect ratio is preserved during resize
- ✅ **RGBA to RGB**: Test conversion of transparent images to JPEG
- ✅ **Small Images**: Ensure small images aren't upscaled

### MinIO Operations
- ✅ **Download Image**: Test downloading images from MinIO
- ✅ **Upload Thumbnail**: Test uploading resized thumbnails
- ✅ **Path Generation**: Test thumbnail path generation (with/without folders)

### Database Operations
- ✅ **Update Post**: Test updating post record with thumbnail path

### Message Processing
- ✅ **Process Success**: Test successful message processing
- ✅ **Process Failure**: Test error handling and message requeuing

### Configuration
- ✅ **Initialization**: Test service initialization with defaults
- ✅ **Environment Variables**: Test custom configuration via env vars

## Running Tests

### Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest test_resize_worker.py -v

# Run with coverage
pytest test_resize_worker.py --cov=resize_worker --cov-report=html
```

### In CI/CD

Tests run automatically in GitHub Actions on:
- Push to `main` or `develop`
- Pull requests to `main` or `develop`

See [.github/workflows/ci.yml](../.github/workflows/ci.yml)

## Test Structure

```python
TestImageResizeService
├── test_initialization              # Service setup
├── test_resize_image                # Core resize logic
├── test_resize_image_preserves_aspect_ratio
├── test_resize_image_rgba_to_rgb
├── test_resize_small_image
├── test_generate_thumbnail_path     # Path generation
├── test_generate_thumbnail_path_no_folder
├── test_download_image_success      # MinIO operations
├── test_upload_thumbnail_success
├── test_update_post_thumbnail       # Database operations
├── test_process_message_success     # Message handling
├── test_process_message_failure
└── test_environment_variables       # Configuration
```

## Mocking Strategy

Tests use mocks for external dependencies:
- **boto3 S3 client**: MinIO operations
- **psycopg2**: PostgreSQL database
- **pika**: RabbitMQ (not tested in unit tests)

## Adding New Tests

When adding new functionality:

1. Create a new test method in `TestImageResizeService`
2. Use fixtures for common setup (`service`, `sample_image`)
3. Mock external dependencies
4. Assert expected behavior
5. Run locally before committing

Example:
```python
def test_new_feature(self, service):
    """Test description."""
    # Arrange
    # Act
    # Assert
```
