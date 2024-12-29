from fastapi.testclient import TestClient
import time
from main import app
from unittest.mock import patch
from redis import Redis
from redis_connection import get_redis

client = TestClient(app)

def init_test():
    redis_client = get_redis()
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

@patch('rate_limiter.RateLimiter._get_start_of_day_timestamp')
@patch('rate_limiter.RateLimiter._get_current_timestamp')
def test_daily_limit(mock_current_time, mock_day_start):
    init_test()  # Clear Redis
    start_time = 1719561600
    headers = {"Authorization": "test-user-light-1"}
    
    # Keep day start constant
    mock_day_start.return_value = start_time
    
    # Make current time advance for rate limit checks
    for i in range(5):  # Account has 50 daily limit
        mock_current_time.return_value = start_time + i
        response = client.get("/joke", headers=headers)
        assert response.status_code == 200, f"Request {i+1} failed"
    
    # Next request should fail (daily limit exceeded)
    mock_current_time.return_value = start_time + 5
    response = client.get("/joke", headers=headers)
    assert response.status_code == 429

@patch('rate_limiter.RateLimiter._get_current_timestamp')
def test_rate_limit(mock_current_time):
    init_test()  # Clear Redis
    start_time = 1719561600
    headers = {"Authorization": "1111-2222-3333"}
    
    # Keep time constant to test rate limit in same second
    mock_current_time.return_value = start_time
    
    # First request should succeed
    response = client.get("/joke", headers=headers)
    assert response.status_code == 200
    
    # Second request in same second should fail
    response = client.get("/joke", headers=headers)
    assert response.status_code == 429