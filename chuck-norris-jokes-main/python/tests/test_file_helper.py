import pytest
import os
import json
from unittest.mock import mock_open, patch
from helpers.file_helper import FileHelper, FileError

@pytest.fixture
def test_file_path():
    return "test_data.json"

@pytest.fixture
def cleanup_file():
    yield
    # Clean up both test files
    files_to_cleanup = ["test_data.json", "accounts.json", "no_permission.json"]
    for file in files_to_cleanup:
        if os.path.exists(file):
            os.remove(file)

def test_read_nonexistent_file():
    """Test reading a file that doesn't exist"""
    with pytest.raises(FileError) as exc:
        FileHelper.read_json_file("nonexistent.json")
    assert "File not found" in str(exc.value)

def test_read_invalid_json(test_file_path, cleanup_file):
    """Test reading invalid JSON content"""
    with open(test_file_path, 'w') as f:
        f.write("invalid json")
    
    with pytest.raises(FileError) as exc:
        FileHelper.read_json_file(test_file_path)
    assert "Invalid JSON format" in str(exc.value)

def test_read_permission_error(cleanup_file):
    """Test reading a file with no permissions"""
    test_file = "no_permission.json"
        # Create file with no read permissions
    with open(test_file, 'w') as f:
        f.write('{"test": "data"}')
    os.chmod(test_file, 0o000)

    with pytest.raises(FileError) as exc:
        FileHelper.read_json_file(test_file)
    assert "Error reading file" in str(exc.value)


def test_read_success_no_mock(cleanup_file):
    """Test successful reading of a real JSON file"""
    test_file = "accounts.json"
    test_data = {
        "1111-2222-3333": {
            "name": "Test User",
            "plan": "free",
            "daily_limit": 50,
            "rate_limit": 1
        },
        "4444-5555-6666": {
            "name": "Pro User",
            "plan": "pro",
            "daily_limit": 12000,
            "rate_limit": 10
        }
    }
    
    # Write test data to file
    with open(test_file, 'w') as f:
        json.dump(test_data, f, indent=4)
    
    # Read and verify without mocks
    result = FileHelper.read_json_file(test_file)
    
    # Verify structure and content
    assert isinstance(result, dict)
    assert len(result) == 2
    assert result["1111-2222-3333"]["plan"] == "free"
    assert result["1111-2222-3333"]["daily_limit"] == 50
    assert result["4444-5555-6666"]["plan"] == "pro"
    assert result["4444-5555-6666"]["daily_limit"] == 12000

def test_read_empty_file(test_file_path, cleanup_file):
    """Test reading an empty file"""
    with open(test_file_path, 'w') as f:
        f.write("")
    
    with pytest.raises(FileError) as exc:
        FileHelper.read_json_file(test_file_path)
    assert "Invalid JSON format" in str(exc.value)

def test_read_corrupted_json(test_file_path, cleanup_file):
    """Test reading corrupted JSON"""
    with open(test_file_path, 'w') as f:
        f.write('{"key": "value"')  # Missing closing brace
    
    with pytest.raises(FileError) as exc:
        FileHelper.read_json_file(test_file_path)
    assert "Invalid JSON format" in str(exc.value)

def test_read_success_with_mock():
    """Test successful reading of a JSON file using mock"""
    mock_json_data = '''{
        "1111-2222-3333": {
            "name": "Test User",
            "plan": "free",
            "daily_limit": 50,
            "rate_limit": 1
        },
        "4444-5555-6666": {
            "name": "Pro User",
            "plan": "pro",
            "daily_limit": 12000,
            "rate_limit": 10
        }
    }'''
    
    with patch('builtins.open', mock_open(read_data=mock_json_data)):
        result = FileHelper.read_json_file("fake_path.json")
        
        # Verify structure and content
        assert isinstance(result, dict)
        assert len(result) == 2
        assert result["1111-2222-3333"]["plan"] == "free"
        assert result["1111-2222-3333"]["daily_limit"] == 50
        assert result["4444-5555-6666"]["plan"] == "pro"
        assert result["4444-5555-6666"]["daily_limit"] == 12000 