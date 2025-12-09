import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
import requests

# Import the app and function from your file
from ipc_api import app, obtener_ipc

# Fixture to create a test client for the FastAPI app
@pytest.fixture
def client():
    return TestClient(app)

# --- Tests for the obtener_ipc() function ---

@patch('ipc_api.requests.get')
def test_obtener_ipc_success(mock_get):
    """
    Tests the success case where the IPC value is found in the HTML.
    """
    # Mock the response from requests.get
    mock_response = Mock()
    mock_response.text = "El IPC sitúa su variación anual en el 3,4% en mayo."
    mock_response.encoding = 'utf-8'
    mock_get.return_value = mock_response

    # Call the function and assert the result
    ipc_value = obtener_ipc()
    assert ipc_value == 3.4
    mock_get.assert_called_once()

@patch('ipc_api.requests.get')
def test_obtener_ipc_not_found(mock_get):
    """
    Tests the case where the IPC pattern is not found in the HTML.
    """
    # Mock a response with different text
    mock_response = Mock()
    mock_response.text = "La información del IPC no está disponible actualmente."
    mock_response.encoding = 'utf-8'
    mock_get.return_value = mock_response

    # The function should return None
    ipc_value = obtener_ipc()
    assert ipc_value is None

@patch('ipc_api.requests.get')
def test_obtener_ipc_request_fails(mock_get):
    """
    Tests how the function behaves when the HTTP request fails.
    """
    # Simulate a request exception
    mock_get.side_effect = requests.exceptions.RequestException("Connection error")

    # The current implementation will raise the exception.
    # This test verifies that behavior.
    with pytest.raises(requests.exceptions.RequestException):
        obtener_ipc()

# --- Tests for the FastAPI endpoint ---

def test_leer_ipc_endpoint_success(client):
    """
    Tests the /ipc endpoint when obtener_ipc returns a value.
    """
    with patch('ipc_api.obtener_ipc', return_value=3.2):
        response = client.get("/ipc")
        assert response.status_code == 200
        assert response.json() == {"ipc": 3.2}

def test_leer_ipc_endpoint_none(client):
    """
    Tests the /ipc endpoint when obtener_ipc returns None.
    """
    with patch('ipc_api.obtener_ipc', return_value=None):
        response = client.get("/ipc")
        assert response.status_code == 200
        assert response.json() == {"ipc": None}