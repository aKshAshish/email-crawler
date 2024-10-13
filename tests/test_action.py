import pytest
import os
import google.oauth2.credentials

from unittest.mock import patch, MagicMock
from app.action import Action


class TestAction:

    @patch('google.oauth2.credentials.Credentials.from_authorized_user_file')
    @patch('os.path.exists')
    @patch('requests.post')
    def test_mark_as_read_success(self, mock_post, mock_exists,  mock_creds):
        """Test successful mark as read action."""

        mock_exists = True
        # Mock credentials
        fake_creds = MagicMock()
        mock_creds.return_value = fake_creds
        fake_creds.valid = True
        fake_creds.token = "fake_token"

        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = ''
        mock_post.return_value = mock_response

        action = Action(action='mark_as_read')
        action(['msg1', 'msg2'])

        # Assertions
        mock_post.assert_called_once_with(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/batchModify",
            headers={
                "Authorization": f"Bearer {fake_creds.token}",
                "Content-Type": "application/json"
            },
            data='{"ids": ["msg1", "msg2"], "removeLabelIds": ["UNREAD"]}'
        )

    
    @patch('google.oauth2.credentials.Credentials.from_authorized_user_file')
    @patch('os.path.exists')
    @patch('requests.post')
    def test_mark_as_unread_success(self, mock_post, mock_exists,  mock_creds):
        """Test successful mark as unread action."""

        mock_exists = True
        # Mock credentials
        fake_creds = MagicMock()
        mock_creds.return_value = fake_creds
        fake_creds.valid = True
        fake_creds.token = "fake_token"

        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = ''
        mock_post.return_value = mock_response

        action = Action(action='mark_as_unread')
        action(['msg1', 'msg2'])

        # Assertions
        mock_post.assert_called_once_with(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/batchModify",
            headers={
                "Authorization": f"Bearer {fake_creds.token}",
                "Content-Type": "application/json"
            },
            data='{"ids": ["msg1", "msg2"], "addLabelIds": ["UNREAD"]}'
        )

    @patch('google.oauth2.credentials.Credentials.from_authorized_user_file')
    @patch('os.path.exists')
    @patch('requests.post')
    def test_move_action_success(self, mock_post, mock_exists,  mock_creds):
        """Test successful move action."""

        mock_exists = True
        # Mock credentials
        fake_creds = MagicMock()
        mock_creds.return_value = fake_creds
        fake_creds.valid = True
        fake_creds.token = "fake_token"

        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = ''
        mock_post.return_value = mock_response

        action = Action(action='move', param='INBOX')
        action(['msg1', 'msg2'])

        # Assertions
        mock_post.assert_called_once_with(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/batchModify",
            headers={
                "Authorization": f"Bearer {fake_creds.token}",
                "Content-Type": "application/json"
            },
            data='{"ids": ["msg1", "msg2"], "addLabelIds": ["INBOX"]}'
        )

    def test_invalid_action(self):
        """Test initialization with an invalid action."""
        with pytest.raises(ValueError, match=r"invalid_action .*"):
            Action(action='invalid_action')

    @patch('google.oauth2.credentials.Credentials.from_authorized_user_file')
    @patch('os.path.exists')
    def test_move_without_param(self, mock_exists,  mock_creds):
        """Test move action without a folder param."""
        mock_exists = True
        # Mock credentials
        fake_creds = MagicMock()
        mock_creds.return_value = fake_creds
        fake_creds.valid = True
        fake_creds.token = "fake_token"
        action = Action(action='move')
        with pytest.raises(ValueError, match=r"Pass a valid folder to move email to."):
            action(['msg1', 'msg2'])

if __name__ == "__main__":
    pytest.main()
