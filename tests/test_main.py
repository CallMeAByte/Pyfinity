"""
Test cases for the main Pyfinity module
"""

from pyfinity import (
    hello_world,
    __version__,
    InfinityClient,
    SyncInfinityClient,
    InfinityAPIError,
)


def test_hello_world():
    """Test the hello_world function."""
    result = hello_world()
    assert "Hello from Pyfinity!" in result
    assert "Infinity Bot List API" in result
    assert isinstance(result, str)


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"
    assert isinstance(__version__, str)


def test_hello_world_not_empty():
    """Test that hello_world returns a non-empty string."""
    result = hello_world()
    assert len(result) > 0
    assert result.strip() != ""


def test_client_classes_exist():
    """Test that the main client classes are properly imported."""
    assert InfinityClient is not None
    assert SyncInfinityClient is not None
    assert InfinityAPIError is not None


def test_infinity_client_initialization():
    """Test that InfinityClient can be initialized."""
    client = InfinityClient("test_token", "test_bot_id")
    assert client.bot_token == "test_token"
    assert client.bot_id == "test_bot_id"
    assert client.base_url == "https://spider.infinitybots.gg"


def test_sync_infinity_client_initialization():
    """Test that SyncInfinityClient can be initialized."""
    client = SyncInfinityClient("test_token", "test_bot_id")
    assert client.client.bot_token == "test_token"
    assert client.client.bot_id == "test_bot_id"


def test_infinity_api_error():
    """Test that InfinityAPIError works correctly."""
    error = InfinityAPIError("Test error", 400)
    assert str(error) == "Test error"
    assert error.status_code == 400

    error_no_status = InfinityAPIError("Test error")
    assert str(error_no_status) == "Test error"
    assert error_no_status.status_code is None
