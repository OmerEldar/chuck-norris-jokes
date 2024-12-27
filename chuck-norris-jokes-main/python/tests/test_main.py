from fastapi.testclient import TestClient
import time
from main import app
from unittest.mock import patch
from redis import Redis

client = TestClient(app)
redis_client = Redis(host='localhost', port=6379, db=0)

def init_test():
    # Clear Redis
    redis_client.flushall()

def test_403():
    init_test()  # Clear Redis
    response = client.get("/joke")
    assert response.status_code == 403

def test_200():
    init_test()  # Clear Redis
    response = client.get("/joke", headers={"Authorization": "1111-2222-3333"})
    assert response.status_code == 200
    assert "joke" in response.json()
    assert isinstance(response.json()["joke"], str)

@patch('time.time')
def test_rate_limit(mock_time):
    init_test()  # Clear Redis
    mock_time.return_value = 1719561600
    headers = {"Authorization": "1111-2222-3333"}
    
    response = client.get("/joke", headers=headers)
    assert response.status_code == 200
    
    response = client.get("/joke", headers=headers)
    assert response.status_code == 429

    mock_time.return_value += 1
    response = client.get("/joke", headers=headers)
    assert response.status_code == 200

@patch('time.time')
def test_daily_limit(mock_time):
    init_test()  # Clear Redis
    start_time = 1719561600
    headers = {"Authorization": "1111-2222-3333"}
    
    for i in range(50):
        mock_time.return_value = start_time + i
        response = client.get("/joke", headers=headers)
        assert response.status_code == 200, f"Request {i+1} failed"
    
    mock_time.return_value = start_time + 50
    response = client.get("/joke", headers=headers)
    assert response.status_code == 429