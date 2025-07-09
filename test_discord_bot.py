#!/usr/bin/env python3
"""
Test Discord bot to verify Pyfinity integration
"""

import asyncio
import os
from pyfinity import InfinityClient, InfinityAPIError

# Mock Discord.py for testing purposes
class MockBot:
    """Mock Discord bot for testing without actual Discord connection."""
    
    def __init__(self):
        self.guilds = [f"guild_{i}" for i in range(50)]  # Mock 50 servers
        self.users = [f"user_{i}" for i in range(1000)]  # Mock 1000 users
        self.user = MockUser()
    
    def get_server_count(self):
        return len(self.guilds)
    
    def get_user_count(self):
        return len(self.users)

class MockUser:
    """Mock bot user."""
    def __init__(self):
        self.id = "123456789012345678"  # Mock bot ID


async def test_bot_stats_posting():
    """Test posting bot statistics to Infinity Bot List."""
    print("🤖 Testing Bot Stats Posting...")
    
    # Mock bot data
    bot = MockBot()
    
    # Initialize Pyfinity client
    # Replace with your actual tokens when testing
    client = InfinityClient(
        bot_token="your_infinity_bot_token_here",
        bot_id=str(bot.user.id)
    )
    
    try:
        async with client:
            # Post bot statistics
            print(f"📊 Posting stats: {bot.get_server_count()} servers, {bot.get_user_count()} users")
            
            response = await client.post_bot_stats(
                server_count=bot.get_server_count(),
                user_count=bot.get_user_count()
            )
            
            print(f"✅ Successfully posted stats: {response}")
            
            # Get bot information
            print("\n📋 Fetching bot information...")
            bot_info = await client.get_bot_info()
            print(f"📋 Bot info: {bot_info}")
            
    except InfinityAPIError as e:
        print(f"❌ API Error: {e}")
        if e.status_code:
            print(f"   Status Code: {e.status_code}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


async def test_error_handling():
    """Test error handling with invalid credentials."""
    print("\n🧪 Testing Error Handling...")
    
    # Test with invalid token
    client = InfinityClient("invalid_token", "123456789")
    
    try:
        async with client:
            await client.post_bot_stats(server_count=10)
            print("❌ This should have failed!")
            
    except InfinityAPIError as e:
        print(f"✅ Correctly caught API error: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected error type: {e}")


def test_sync_client():
    """Test the synchronous client."""
    print("\n🔄 Testing Synchronous Client...")
    
    from pyfinity import SyncInfinityClient
    
    # Mock bot data
    bot = MockBot()
    
    # Initialize sync client
    client = SyncInfinityClient(
        bot_token="your_infinity_bot_token_here",
        bot_id=str(bot.user.id)
    )
    
    try:
        response = client.post_bot_stats(
            server_count=bot.get_server_count(),
            user_count=bot.get_user_count()
        )
        print(f"✅ Sync client posted stats: {response}")
        
    except InfinityAPIError as e:
        print(f"❌ Sync API Error: {e}")
    except Exception as e:
        print(f"❌ Sync Unexpected error: {e}")


async def main():
    """Run all tests."""
    print("🚀 Testing Pyfinity with Discord Bot Simulation")
    print("=" * 50)
    
    # Test async client
    await test_bot_stats_posting()
    
    # Test error handling
    await test_error_handling()
    
    # Test sync client
    test_sync_client()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\n📚 Next steps:")
    print("1. Replace mock tokens with real ones from Infinity Bot List")
    print("2. Install discord.py: pip install discord.py")
    print("3. Create a real Discord bot and test with actual data")
    print("4. Check the examples/ directory for Discord.py integration")


if __name__ == "__main__":
    asyncio.run(main())
