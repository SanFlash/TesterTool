from flask import Flask, jsonify
import pytest

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Enter Website URL' in response.data

def test_analyze_page(client):
    response = client.post('/analyze', data={'url': 'http://example.com'})
    assert response.status_code == 200
    assert b'Test Cases' in response.data

def test_invalid_url(client):
    response = client.post('/analyze', data={'url': 'invalid-url'})
    assert response.status_code == 400
    assert b'Invalid URL' in response.data

def test_results_page(client):
    response = client.get('/results')
    assert response.status_code == 200
    assert b'Results of Analysis' in response.data

@pytest.fixture
def client():
    # Use the application instance from the project so routes are available
    from src.app import app as flask_app
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client