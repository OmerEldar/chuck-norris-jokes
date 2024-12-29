from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch
from redis_connection import get_redis

client = TestClient(app)

def init_test():
    redis_client = get_redis()
    redis_client.flushall()

def test_403():
    init_test()
    response = client.get("/joke")
    assert response.status_code == 403

def test_200():
    init_test()
    response = client.get("/joke", headers={"Authorization": "1111-2222-3333"})
    assert response.status_code == 200
    assert "joke" in response.json()
    assert isinstance(response.json()["joke"], str)

@patch('rate_limiter.RateLimiter._check_daily_limit')
@patch('rate_limiter.RateLimiter._check_rate_limit')
def test_daily_limit(mock_rate_check, mock_daily_check):
    init_test()
    headers = {"Authorization": "1111-2222-3333"}
    
    # First few requests pass both checks
    mock_rate_check.return_value = True
    mock_daily_check.side_effect = [True] * 5 + [False]
    
    # First 5 requests should succeed
    for i in range(5):
        response = client.get("/joke", headers=headers)
        assert response.status_code == 200, f"Request {i+1} failed"
    
    # Next request should fail (daily limit exceeded)
    response = client.get("/joke", headers=headers)
    assert response.status_code == 429

@patch('rate_limiter.RateLimiter._check_rate_limit')
def test_rate_limit(mock_rate_check):
    init_test()
    headers = {"Authorization": "1111-2222-3333"}
    
    # First request passes, second fails
    mock_rate_check.side_effect = [True, False]
    
    # First request should succeed
    response = client.get("/joke", headers=headers)
    assert response.status_code == 200
    
    # Second request should fail
    response = client.get("/joke", headers=headers)
    assert response.status_code == 429