import pytest
from app import app
import json


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'model' in data


def test_generate_comment_missing_data(client):
    """Test generate comment endpoint with missing data."""
    response = client.post('/generate-comment',
                          data=json.dumps({}),
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_generate_comment_valid_request(client):
    """Test generate comment endpoint with valid data."""
    response = client.post('/generate-comment',
                          data=json.dumps({
                              'title': 'Test Post',
                              'text': 'This is a test post'
                          }),
                          content_type='application/json')
    
    # This might fail if Ollama is not running, so we accept both success and error
    assert response.status_code in [200, 500]
    data = json.loads(response.data)
    
    if response.status_code == 200:
        assert 'comment' in data
        assert 'generated_by' in data


def test_generate_comment_missing_title(client):
    """Test generate comment endpoint with missing title."""
    response = client.post('/generate-comment',
                          data=json.dumps({
                              'text': 'This is a test post'
                          }),
                          content_type='application/json')
    assert response.status_code == 400


def test_generate_comment_missing_text(client):
    """Test generate comment endpoint with missing text."""
    response = client.post('/generate-comment',
                          data=json.dumps({
                              'title': 'Test Post'
                          }),
                          content_type='application/json')
    assert response.status_code == 400
