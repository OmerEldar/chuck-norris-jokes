from fastapi.testclient import TestClient
from main import app, Auth
from unittest.mock import patch
from redis_connection import get_redis
from helpers.cached_accounts_file_helper import CachedAccountsFileHelper
import json
import os
import pytest

# Test accounts data
TEST_ACCOUNTS = {
    "1111-2222-3333": {
        "rate_limit": 10,
        "daily_limit": 100
    },
    "test-token": {
        "rate_limit": 5,
        "daily_limit": 50
    }
}

# Get the test directory path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_ACCOUNTS_PATH = os.path.join(TEST_DIR, "test_accounts.json")

@pytest.fixture(autouse=True)
def setup_and_cleanup():
    """Create test accounts file before tests and clean up after"""
    # Setup: Create test accounts file
    with open(TEST_ACCOUNTS_PATH, 'w') as f:
        json.dump(TEST_ACCOUNTS, f)
    
    # Initialize app with test accounts file
    file_helper = CachedAccountsFileHelper()
    app.middleware_stack = None  # Clear existing middleware
    app.add_middleware(
        Auth,
        accounts_path=TEST_ACCOUNTS_PATH,
        file_helper=file_helper
    )
    
    yield  # Run tests
    
    # Cleanup: Remove test accounts file
    try:
        os.remove(TEST_ACCOUNTS_PATH)
    except FileNotFoundError:
        pass
    
    # Clear Redis cache
    redis_client = get_redis()
    redis_client.flushall()

client = TestClient(app)

def test_403_without_token():
    """Test that requests without token return 403"""
    response = client.get("/joke")
    assert response.status_code == 403

def test_403_with_invalid_token():
    """Test that requests with invalid token return 403"""
    response = client.get("/joke", headers={"Authorization": "invalid-token"})
    assert response.status_code == 403

def test_200_with_valid_token():
    """Test that requests with valid token return 200"""
    response = client.get("/joke", headers={"Authorization": "1111-2222-3333"})
    assert response.status_code == 200
    assert "joke" in response.json()
    assert isinstance(response.json()["joke"], str)

@patch('rate_limiter.RateLimiter._is_within_daily_limit')
@patch('rate_limiter.RateLimiter._is_within_rate_limit')
def test_rate_limiting(mock_rate_check, mock_daily_check):
    """Test rate limiting functionality"""
    headers = {"Authorization": "1111-2222-3333"}
    
    # Configure mocks
    mock_rate_check.side_effect = [True, False]  # First request passes, second fails
    mock_daily_check.return_value = True  # Daily limit always passes
    
    # First request should succeed
    response = client.get("/joke", headers=headers)
    assert response.status_code == 200
    
    # Second request should fail due to rate limit
    response = client.get("/joke", headers=headers)
    assert response.status_code == 429

@patch('rate_limiter.RateLimiter._is_within_daily_limit')
@patch('rate_limiter.RateLimiter._is_within_rate_limit')
def test_daily_limit(mock_rate_check, mock_daily_check):
    """Test daily limit functionality"""
    headers = {"Authorization": "test-token"}
    
    # Configure mocks
    mock_rate_check.return_value = True  # Rate limit always passes
    mock_daily_check.side_effect = [True] * 5 + [False]  # Pass 5 times, then fail
    
    # First 5 requests should succeed
    for _ in range(5):
        response = client.get("/joke", headers=headers)
        assert response.status_code == 200
    
    # Sixth request should fail due to daily limit
    response = client.get("/joke", headers=headers)
    assert response.status_code == 429