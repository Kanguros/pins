# from unittest.mock import patch, Mock
#
# import pytest
# from requests.exceptions import RequestException
#
#
# def test_authentication_success():
#     # Create a session with failing auth
#     mock_session = Mock()
#     # Setup default auth response
#     mock_auth_response = Mock()
#     mock_auth_response.json.return_value = {"result": {"key": "test_token"}}
#     mock_auth_response.raise_for_status = Mock()
#     mock_session.post.return_value = mock_auth_response
#
#     with patch('requests.Session', return_value=mock_session):
#         with patch('policy_inspector.connector.panorama.urllib3'):
#             from policy_inspector.connector.panorama import PanoramaConnector
#             connector = PanoramaConnector(
#                 hostname="test_host",
#                 username="test_user",
#                 password="test_pass",
#             )
#
#             assert connector.token == "test_token"
#             assert connector.headers["X-PAN-KEY"] == "test_token"
#             mock_session.post.assert_called_once()
#
#
# def test_authentication_failure():
#     # Create a session with failing auth
#     mock_session = Mock()
#     mock_response = Mock()
#     mock_response.json.return_value = {}
#     mock_response.raise_for_status = Mock()
#     mock_session.post.return_value = mock_response
#
#     with patch('requests.Session', return_value=mock_session):
#         with patch('policy_inspector.connector.panorama.urllib3'):
#             from policy_inspector.connector.panorama import PanoramaConnector
#             with pytest.raises(ValueError, match="Authentication failed: No token in response"):
#                 panorama = PanoramaConnector(
#                     hostname="test_host",
#                     username="test_user",
#                     password="test_pass",
#                 )
#                 print(panorama.__dict__.items())
#
#
# def test_authentication_request_exception():
#     # Create a session with connection error
#     mock_session = Mock()
#     mock_session.post.side_effect = RequestException("Connection error")
#
#     with patch('requests.Session', return_value=mock_session):
#         with patch('policy_inspector.connector.panorama.urllib3'):
#             from policy_inspector.connector.panorama import PanoramaConnector
#             with pytest.raises(RequestException, match="Connection error"):
#                 PanoramaConnector(
#                     hostname="test_host",
#                     username="test_user",
#                     password="test_pass",
#                 )
#
#
# def test_token_expiration_handling():
#     # Create session with two different auth responses
#     mock_session = Mock()
#     mock_response1 = Mock()
#     mock_response1.json.return_value = {"result": {"key": "initial_token"}}
#     mock_response1.raise_for_status = Mock()
#     mock_response2 = Mock()
#     mock_response2.json.return_value = {"result": {"key": "renewed_token"}}
#     mock_response2.raise_for_status = Mock()
#     mock_session.post.side_effect = [mock_response1, mock_response2]
#
#     with patch('requests.Session', return_value=mock_session):
#         with patch('policy_inspector.connector.panorama.urllib3'):
#             from policy_inspector.connector.panorama import PanoramaConnector
#             connector = PanoramaConnector(
#                 hostname="test_host",
#                 username="test_user",
#                 password="test_pass",
#             )
#
#             assert connector.token == "initial_token"
#             connector._authenticate("test_user", "test_pass")
#             assert connector.token == "renewed_token"
#             assert connector.headers["X-PAN-KEY"] == "renewed_token"
#             assert mock_session.post.call_count == 2
