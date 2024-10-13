import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
import pytest

from unittest.mock import patch, MagicMock
from app import util

# Constants for test paths
TEST_TOKEN_PATH = './app/tests/tokens.json'
TEST_CREDENTIALS_PATH = './app/tests/credentials.json'


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set up environment variables for testing."""
    monkeypatch.setenv('PATH_TOKENS', TEST_TOKEN_PATH)
    monkeypatch.setenv('PATH_GMAIL_CREDENTIALS', TEST_CREDENTIALS_PATH)


@patch('google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file')
@patch('os.path.exists')
@patch('builtins.open', new_callable=MagicMock)
def test_load_creds_new_auth(mock_open, mock_exists, mock_flow):
    """Test the case where credentials are not available and new authorization is required."""
    
    # Mock the existence of the token file
    mock_exists.return_value = False

    #Create a mock for the flow
    mock_flow_instance = MagicMock()
    mock_flow.return_value = mock_flow_instance

    # Mock the run_local_server method to return fake credentials
    fake_creds = MagicMock()
    fake_creds.to_json.return_value = '{"token": "fake_token"}'
    mock_flow_instance.run_local_server.return_value = fake_creds

    # Call the function
    creds = util.load_creds()

    # # Assertions
    mock_flow.assert_called_once_with(TEST_CREDENTIALS_PATH, util.SCOPES)
    mock_open.assert_called_once_with(TEST_TOKEN_PATH, "w")
    fake_creds.to_json.assert_called_once()
    assert creds == fake_creds


@patch('google.oauth2.credentials.Credentials.from_authorized_user_file')
@patch('os.path.exists')
def test_load_creds_valid_token(mock_exists, mock_creds):
    """Test the case where valid credentials exist."""
    
    # Mock the existence of the token file
    mock_exists.return_value = True

    # Mock credentials object
    fake_creds = MagicMock()
    mock_creds.return_value = fake_creds
    fake_creds.valid = True
    
    # Call the function
    creds = util.load_creds()

    # Assertions
    mock_exists.assert_called_once_with(TEST_TOKEN_PATH)
    mock_creds.assert_called_once_with(TEST_TOKEN_PATH, util.SCOPES)
    
    assert creds == fake_creds


@patch('google.oauth2.credentials.Credentials.from_authorized_user_file')
@patch('os.path.exists')
@patch('builtins.open', new_callable=MagicMock)
def test_load_creds_expired_token(mock_open, mock_exists, mock_creds):
    """Test the case where the credentials are expired and refresh is required."""
    
    # Mock the existence of the token file
    mock_exists.return_value = True

    # Mock expired credentials
    fake_creds = MagicMock()
    mock_creds.return_value = fake_creds
    fake_creds.valid = False
    fake_creds.expired = True
    fake_creds.refres_token = 'fake_refresh_token'
    
    # Mock the refresh method
    fake_creds.refresh.return_value = MagicMock()
    fake_creds.to_json.return_value = '{"token": "fake_token"}'
    # Call the function
    creds = util.load_creds()

    # Assertions
    mock_creds.return_value.refresh.assert_called_once()
    mock_open.assert_called_once_with(TEST_TOKEN_PATH, "w")
    fake_creds.to_json.assert_called_once()
    assert creds == fake_creds


if __name__ == "__main__":
    pytest.main()
