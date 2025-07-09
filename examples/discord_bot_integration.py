"""
Example: Discord.py bot integration

This example shows how to integrate Pyfinity with a Discord.py bot
to automatically post statistics to Infinity Bot List.
"""

import asyncio
from pyfinity import InfinityClient, InfinityAPIError

# Note: This example assumes you have discord.py installed
# pip install discord.py

# Uncomment the following lines if you have discord.py installed:
# import discord
# from discord.ext import commands, tasks


class DiscordBotWithStats:
    """
    Example Discord bot that posts statistics to Infinity Bot List.

    This is a simplified example - you would integrate this with your
    actual Discord.py bot.
    """

    def __init__(self, infinity_token: str, bot_id: str):
        self.infinity_client = InfinityClient(infinity_token, bot_id)
        self.server_count = 0
        self.user_count = 0

    async def start_stats_posting(self):
        """Start the automatic stats posting task."""
        await self.infinity_client.start_session()

        # In a real bot, you would get these from your Discord bot
        # self.server_count = len(self.bot.guilds)
        # self.user_count = len(self.bot.users)

        # For demonstration, we'll use mock values
        self.server_count = 150
        self.user_count = 5000

        # Post stats every 30 minutes (1800 seconds)
        while True:
            try:
                await self.post_stats()
                await asyncio.sleep(1800)  # 30 minutes
            except Exception as e:
                print(f"Error posting stats: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying

    async def post_stats(self):
        """Post current bot statistics."""
        try:
            response = await self.infinity_client.post_bot_stats(
                server_count=self.server_count, user_count=self.user_count
            )
            print(
                f"📊 Stats posted: {self.server_count} servers, {self.user_count} users"
            )
            print(f"✅ Response: {response}")
        except InfinityAPIError as e:
            print(f"❌ Failed to post stats: {e}")
            raise

    async def close(self):
        """Clean up resources."""
        await self.infinity_client.close_session()


# Example usage with discord.py (commented out)
"""
class MyDiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.default())
        
        # Initialize Pyfinity client
        self.stats_bot = DiscordBotWithStats(
            infinity_token="your_infinity_token_here",
            bot_id="your_bot_id_here"
        )
    
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        
        # Update actual counts
        self.stats_bot.server_count = len(self.guilds)
        self.stats_bot.user_count = len(self.users)
        
        # Start posting stats
        asyncio.create_task(self.stats_bot.start_stats_posting())
    
    async def on_guild_join(self, guild):
        # Update server count when joining a new guild
        self.stats_bot.server_count = len(self.guilds)
        
        # Post updated stats immediately
        try:
            await self.stats_bot.post_stats()
        except Exception as e:
            print(f"Failed to post stats after joining guild: {e}")
    
    async def on_guild_remove(self, guild):
        # Update server count when leaving a guild
        self.stats_bot.server_count = len(self.guilds)
        
        # Post updated stats immediately
        try:
            await self.stats_bot.post_stats()
        except Exception as e:
            print(f"Failed to post stats after leaving guild: {e}")

# Run the bot
# bot = MyDiscordBot()
# bot.run('your_discord_token_here')
"""


async def main():
    """Example of manual stats posting."""
    stats_bot = DiscordBotWithStats(
        infinity_token="your_infinity_token_here", bot_id="your_bot_id_here"
    )

    try:
        # Post stats once
        await stats_bot.start_stats_posting()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    finally:
        await stats_bot.close()


if __name__ == "__main__":
    print("🤖 Discord.py Bot Integration Example")
    print("This example shows how to integrate Pyfinity with Discord.py")
    print("Uncomment the discord.py code to use with a real bot")
    print("\nRunning manual stats posting example...")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
