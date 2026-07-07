# tests/test_app.py
import json

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'

def test_get_models(client):
    """Test the get models endpoint."""
    # This assumes OPENROUTER_API_KEY is set in the test environment
    response = client.get('/api/models')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'primary' in data['models']
    assert 'fallbacks' in data['models']
    assert 'available' in data['models']

def test_index(client):
    """Test the web interface."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Care AI" in response.data