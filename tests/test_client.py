"""
Test cases for the Infinity API client
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pyfinity.client import InfinityClient, SyncInfinityClient, InfinityAPIError


class TestInfinityClient:
    """Test cases for the async InfinityClient."""

    def test_init(self):
        """Test client initialization."""
        client = InfinityClient("test_token", "123456789")
        assert client.bot_token == "test_token"
        assert client.bot_id == "123456789"
        assert client.base_url == "https://spider.infinitybots.gg"
        assert client.session is None

    @pytest.mark.asyncio
    async def test_start_session(self):
        """Test session initialization."""
        client = InfinityClient("test_token", "123456789")

        with patch("httpx.AsyncClient") as mock_client:
            await client.start_session()

            mock_client.assert_called_once()
            call_args = mock_client.call_args
            assert call_args[1]["base_url"] == "https://spider.infinitybots.gg"
            assert "Authorization" in call_args[1]["headers"]
            assert call_args[1]["headers"]["Authorization"] == "Bot test_token"

    @pytest.mark.asyncio
    async def test_close_session(self):
        """Test session cleanup."""
        client = InfinityClient("test_token", "123456789")

        # Mock session
        mock_session = AsyncMock()
        client.session = mock_session

        await client.close_session()

        mock_session.aclose.assert_called_once()
        assert client.session is None

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        client = InfinityClient("test_token", "123456789")

        with (
            patch.object(client, "start_session") as mock_start,
            patch.object(client, "close_session") as mock_close,
        ):

            async with client:
                pass

            mock_start.assert_called_once()
            mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_success(self):
        """Test successful API request."""
        client = InfinityClient("test_token", "123456789")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        mock_session = AsyncMock()
        mock_session.request.return_value = mock_response
        client.session = mock_session

        result = await client._make_request("GET", "/test")

        assert result == {"success": True}
        mock_session.request.assert_called_once_with(
            method="GET", url="/test", json=None
        )

    @pytest.mark.asyncio
    async def test_make_request_api_error(self):
        """Test API error handling."""
        client = InfinityClient("test_token", "123456789")

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Bad Request"}

        mock_session = AsyncMock()
        mock_session.request.return_value = mock_response
        client.session = mock_session

        with pytest.raises(InfinityAPIError) as exc_info:
            await client._make_request("GET", "/test")

        assert "Bad Request" in str(exc_info.value)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_post_bot_stats(self):
        """Test posting bot statistics."""
        client = InfinityClient("test_token", "123456789")

        with patch.object(client, "_make_request") as mock_request:
            mock_request.return_value = {"success": True}

            result = await client.post_bot_stats(
                server_count=100, user_count=5000, shard_count=2
            )

            mock_request.assert_called_once_with(
                "POST",
                "/bots/123456789/stats",
                data={"servers": 100, "users": 5000, "shards": 2},
            )
            assert result == {"success": True}

    @pytest.mark.asyncio
    async def test_post_bot_stats_minimal(self):
        """Test posting bot statistics with minimal data."""
        client = InfinityClient("test_token", "123456789")

        with patch.object(client, "_make_request") as mock_request:
            mock_request.return_value = {"success": True}

            result = await client.post_bot_stats(server_count=100)

            mock_request.assert_called_once_with(
                "POST", "/bots/123456789/stats", data={"servers": 100}
            )
            assert result == {"success": True}

    @pytest.mark.asyncio
    async def test_get_bot_info(self):
        """Test getting bot information."""
        client = InfinityClient("test_token", "123456789")

        with patch.object(client, "_make_request") as mock_request:
            mock_request.return_value = {"bot_id": "123456789"}

            result = await client.get_bot_info()

            mock_request.assert_called_once_with("GET", "/bots/123456789")
            assert result == {"bot_id": "123456789"}

    @pytest.mark.asyncio
    async def test_get_user_info(self):
        """Test getting user information."""
        client = InfinityClient("test_token", "123456789")

        with patch.object(client, "_make_request") as mock_request:
            mock_request.return_value = {"user_id": "987654321"}

            result = await client.get_user_info("987654321")

            mock_request.assert_called_once_with("GET", "/users/987654321")
            assert result == {"user_id": "987654321"}


class TestSyncInfinityClient:
    """Test cases for the sync SyncInfinityClient."""

    def test_init(self):
        """Test sync client initialization."""
        client = SyncInfinityClient("test_token", "123456789")
        assert isinstance(client.client, InfinityClient)
        assert client.client.bot_token == "test_token"
        assert client.client.bot_id == "123456789"

    def test_post_bot_stats(self):
        """Test synchronous bot stats posting."""
        client = SyncInfinityClient("test_token", "123456789")

        with patch.object(client, "_run_async") as mock_run:
            mock_run.return_value = {"success": True}

            result = client.post_bot_stats(100, 5000, 2)

            assert result == {"success": True}
            mock_run.assert_called_once()

    def test_get_bot_info(self):
        """Test synchronous bot info retrieval."""
        client = SyncInfinityClient("test_token", "123456789")

        with patch.object(client, "_run_async") as mock_run:
            mock_run.return_value = {"bot_id": "123456789"}

            result = client.get_bot_info()

            assert result == {"bot_id": "123456789"}
            mock_run.assert_called_once()

    def test_get_user_info(self):
        """Test synchronous user info retrieval."""
        client = SyncInfinityClient("test_token", "123456789")

        with patch.object(client, "_run_async") as mock_run:
            mock_run.return_value = {"user_id": "987654321"}

            result = client.get_user_info("987654321")

            assert result == {"user_id": "987654321"}
            mock_run.assert_called_once()


class TestInfinityAPIError:
    """Test cases for InfinityAPIError."""

    def test_init_with_status_code(self):
        """Test error initialization with status code."""
        error = InfinityAPIError("Test error", 400)
        assert str(error) == "Test error"
        assert error.status_code == 400

    def test_init_without_status_code(self):
        """Test error initialization without status code."""
        error = InfinityAPIError("Test error")
        assert str(error) == "Test error"
        assert error.status_code is None

    def test_is_exception(self):
        """Test that InfinityAPIError is an Exception."""
        error = InfinityAPIError("Test error")
        assert isinstance(error, Exception)
