from fastapi.testclient import TestClient
import time
from main import app
from unittest.mock import patch

client = TestClient(app)

def test_403():
    response = client.get("/joke")
    assert response.status_code == 403

def test_200():
    response = client.get("/joke", headers={"Authorization": "1111-2222-3333"})
    assert response.status_code == 200
    assert "joke" in response.json()
    assert isinstance(response.json()["joke"], str)

@patch('time.time')
def test_rate_limit(mock_time):
    mock_time.return_value = 1719561600  # Set time to a known value
    # Test free plan rate limit (1 req/sec)
    headers = {"Authorization": "1111-2222-3333"}
    
    # First request should succeed
    response = client.get("/joke", headers=headers)
    assert response.status_code == 200
    
    # Second immediate request should fail
    response = client.get("/joke", headers=headers)
    assert response.status_code == 429

    # Wait 1 second and try again
    time.sleep(1)
    response = client.get("/joke", headers=headers)
    assert response.status_code == 200

def test_daily_limit():
    headers = {"Authorization": "1111-2222-3333"}
    
    # Make 51 requests with 1 second intervals
    for i in range(51):
        response = client.get("/joke", headers=headers)
        time.sleep(1)
        if i < 50:
            assert response.status_code == 200
        else:
            assert response.status_code == 429