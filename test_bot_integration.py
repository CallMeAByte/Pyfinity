#!/usr/bin/env python3
"""
Unit tests for Discord bot integration with Pyfinity
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from pyfinity import InfinityClient, SyncInfinityClient, InfinityAPIError


class TestBotIntegration:
    """Test cases for bot integration scenarios."""
    
    def test_bot_initialization(self):
        """Test bot initialization with Pyfinity client."""
        # Mock bot data
        bot_token = "test_token"
        bot_id = "123456789012345678"
        
        # Initialize client
        client = InfinityClient(bot_token, bot_id)
        
        assert client.bot_token == bot_token
        assert client.bot_id == bot_id
        assert client.base_url == "https://spider.infinitybots.gg"
    
    @pytest.mark.asyncio
    async def test_stats_posting_workflow(self):
        """Test the complete stats posting workflow."""
        client = InfinityClient("test_token", "123456789")
        
        # Mock bot data
        server_count = 50
        user_count = 1000
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                "success": True,
                "message": "Stats updated successfully"
            }
            
            # Test posting stats
            response = await client.post_bot_stats(
                server_count=server_count,
                user_count=user_count
            )
            
            # Verify the request was made correctly
            mock_request.assert_called_once_with(
                "POST",
                "/bots/123456789/stats",
                data={"servers": server_count, "users": user_count}
            )
            
            assert response["success"] is True
    
    @pytest.mark.asyncio
    async def test_bot_info_retrieval(self):
        """Test retrieving bot information."""
        client = InfinityClient("test_token", "123456789")
        
        expected_info = {
            "id": "123456789",
            "name": "Test Bot",
            "servers": 50,
            "votes": 10
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = expected_info
            
            bot_info = await client.get_bot_info()
            
            mock_request.assert_called_once_with("GET", "/bots/123456789")
            assert bot_info == expected_info
    
    @pytest.mark.asyncio
    async def test_error_handling_in_bot(self):
        """Test error handling in bot context."""
        client = InfinityClient("invalid_token", "123456789")
        
        with patch.object(client, '_make_request') as mock_request:
            # Simulate API error
            mock_request.side_effect = InfinityAPIError("Unauthorized", 401)
            
            with pytest.raises(InfinityAPIError) as exc_info:
                await client.post_bot_stats(server_count=10)
            
            assert "Unauthorized" in str(exc_info.value)
            assert exc_info.value.status_code == 401
    
    def test_sync_client_in_bot(self):
        """Test synchronous client usage in bot."""
        client = SyncInfinityClient("test_token", "123456789")
        
        with patch.object(client, '_run_async') as mock_run:
            mock_run.return_value = {"success": True}
            
            response = client.post_bot_stats(server_count=25, user_count=500)
            
            assert response["success"] is True
            mock_run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_periodic_stats_posting(self):
        """Test periodic stats posting like in a real bot."""
        client = InfinityClient("test_token", "123456789")
        
        # Mock multiple stats postings
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {"success": True}
            
            # Simulate posting stats multiple times
            for i in range(3):
                await client.post_bot_stats(
                    server_count=50 + i,
                    user_count=1000 + i * 10
                )
            
            # Verify all requests were made
            assert mock_request.call_count == 3
    
    @pytest.mark.asyncio
    async def test_context_manager_usage(self):
        """Test using client as context manager in bot."""
        client = InfinityClient("test_token", "123456789")
        
        with (
            patch.object(client, 'start_session') as mock_start,
            patch.object(client, 'close_session') as mock_close,
            patch.object(client, '_make_request') as mock_request
        ):
            mock_request.return_value = {"success": True}
            
            # Test context manager usage
            async with client:
                await client.post_bot_stats(server_count=10)
            
            # Verify session management
            mock_start.assert_called_once()
            mock_close.assert_called_once()
            mock_request.assert_called_once()


class MockDiscordBot:
    """Mock Discord bot for testing."""
    
    def __init__(self):
        self.guilds = [f"guild_{i}" for i in range(25)]
        self.users = [f"user_{i}" for i in range(500)]
        self.user = MagicMock()
        self.user.id = 123456789012345678
        self.infinity_client = None
    
    async def setup_infinity_client(self, token):
        """Setup Infinity client for the bot."""
        self.infinity_client = InfinityClient(token, str(self.user.id))
    
    async def post_bot_stats(self):
        """Post bot statistics."""
        if not self.infinity_client:
            raise ValueError("Infinity client not initialized")
        
        async with self.infinity_client:
            return await self.infinity_client.post_bot_stats(
                server_count=len(self.guilds),
                user_count=len(self.users)
            )


class TestMockBot:
    """Test the mock bot functionality."""
    
    @pytest.mark.asyncio
    async def test_mock_bot_stats_posting(self):
        """Test mock bot posting stats."""
        bot = MockDiscordBot()
        await bot.setup_infinity_client("test_token")
        
        with patch.object(bot.infinity_client, '_make_request') as mock_request:
            mock_request.return_value = {"success": True}
            
            response = await bot.post_bot_stats()
            
            assert response["success"] is True
            mock_request.assert_called_once()
    
    def test_mock_bot_data(self):
        """Test mock bot data."""
        bot = MockDiscordBot()
        
        assert len(bot.guilds) == 25
        assert len(bot.users) == 500
        assert bot.user.id == 123456789012345678


# Run tests
if __name__ == "__main__":
    print("🧪 Running Bot Integration Tests...")
    print("=" * 40)
    
    # Run with pytest
    pytest.main([__file__, "-v"])
