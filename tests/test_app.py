import pytest

from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_index(client):
    r = client.get('/')
    assert r.status_code == 200
    assert b'Weather Dashboard' in r.data


def test_api_no_key(client, monkeypatch):
    # Ensure OPENWEATHER_API_KEY is not set for this test
    monkeypatch.setenv('OPENWEATHER_API_KEY', '')
    r = client.get('/api/weather?q=London')
    assert r.status_code == 500
    assert b'OPENWEATHER_API_KEY' in r.data
