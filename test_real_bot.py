#!/usr/bin/env python3
"""
Real Discord bot example using Pyfinity
This requires discord.py to be installed: pip install discord.py
"""

import asyncio
import os
from pyfinity import InfinityClient, InfinityAPIError

# Uncomment these lines when you have discord.py installed
# import discord
# from discord.ext import commands, tasks

class TestDiscordBot:
    """Test Discord bot with Pyfinity integration."""
    
    def __init__(self):
        # Configuration
        self.discord_token = os.getenv('DISCORD_TOKEN', 'your_discord_token_here')
        self.infinity_token = os.getenv('INFINITY_TOKEN', 'your_infinity_token_here')
        self.bot_id = os.getenv('BOT_ID', 'your_bot_id_here')
        
        # Initialize Pyfinity client
        self.infinity_client = InfinityClient(
            bot_token=self.infinity_token,
            bot_id=self.bot_id
        )
        
        # Mock bot data for testing
        self.mock_server_count = 25
        self.mock_user_count = 500
    
    async def post_stats(self):
        """Post bot statistics to Infinity Bot List."""
        try:
            async with self.infinity_client:
                response = await self.infinity_client.post_bot_stats(
                    server_count=self.mock_server_count,
                    user_count=self.mock_user_count
                )
                print(f"✅ Posted stats: {self.mock_server_count} servers, {self.mock_user_count} users")
                print(f"📊 Response: {response}")
                return True
                
        except InfinityAPIError as e:
            print(f"❌ Failed to post stats: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    async def get_bot_info(self):
        """Get bot information from Infinity Bot List."""
        try:
            async with self.infinity_client:
                bot_info = await self.infinity_client.get_bot_info()
                print(f"📋 Bot info: {bot_info}")
                return bot_info
                
        except InfinityAPIError as e:
            print(f"❌ Failed to get bot info: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    async def test_all_features(self):
        """Test all Pyfinity features."""
        print("🤖 Testing Discord Bot with Pyfinity")
        print("=" * 40)
        
        # Test posting stats
        print("\n1. Testing stats posting...")
        await self.post_stats()
        
        # Test getting bot info
        print("\n2. Testing bot info retrieval...")
        await self.get_bot_info()
        
        # Test error handling
        print("\n3. Testing error handling...")
        await self.test_error_handling()
        
        print("\n✅ All tests completed!")
    
    async def test_error_handling(self):
        """Test error handling with invalid data."""
        invalid_client = InfinityClient("invalid_token", "123")
        
        try:
            async with invalid_client:
                await invalid_client.post_bot_stats(server_count=1)
                print("❌ This should have failed!")
                
        except InfinityAPIError as e:
            print(f"✅ Correctly caught API error: {e}")
        except Exception as e:
            print(f"⚠️ Caught unexpected error: {e}")


# Example Discord.py bot (commented out - uncomment when you have discord.py)
"""
class PyfinityDiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        # Initialize Pyfinity
        self.infinity_client = InfinityClient(
            bot_token=os.getenv('INFINITY_TOKEN'),
            bot_id=str(self.user.id) if self.user else os.getenv('BOT_ID')
        )
        
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        print(f'Bot is in {len(self.guilds)} servers')
        
        # Post initial stats
        await self.post_stats()
        
        # Start periodic stats posting
        self.stats_loop.start()
    
    @tasks.loop(minutes=30)
    async def stats_loop(self):
        await self.post_stats()
    
    async def post_stats(self):
        try:
            async with self.infinity_client:
                response = await self.infinity_client.post_bot_stats(
                    server_count=len(self.guilds),
                    user_count=len(self.users)
                )
                print(f"📊 Posted stats: {len(self.guilds)} servers, {len(self.users)} users")
        except Exception as e:
            print(f"Failed to post stats: {e}")
    
    @commands.command(name='stats')
    async def stats_command(self, ctx):
        try:
            async with self.infinity_client:
                bot_info = await self.infinity_client.get_bot_info()
                await ctx.send(f"📊 Bot stats: {bot_info}")
        except Exception as e:
            await ctx.send(f"❌ Error fetching stats: {e}")

# To run the actual Discord bot:
# bot = PyfinityDiscordBot()
# bot.run(os.getenv('DISCORD_TOKEN'))
"""


async def main():
    """Run the test bot."""
    test_bot = TestDiscordBot()
    await test_bot.test_all_features()
    
    print("\n" + "=" * 50)
    print("🔧 Setup Instructions:")
    print("1. Get your Discord bot token from https://discord.com/developers/applications")
    print("2. Get your Infinity Bot List token from https://infinitybots.gg")
    print("3. Set environment variables or replace the tokens in the code:")
    print("   - DISCORD_TOKEN=your_discord_token")
    print("   - INFINITY_TOKEN=your_infinity_token")
    print("   - BOT_ID=your_bot_id")
    print("4. Install discord.py: pip install discord.py")
    print("5. Uncomment the Discord.py bot code and run it")


if __name__ == "__main__":
    asyncio.run(main())
