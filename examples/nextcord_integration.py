"""
Example: Nextcord Integration with Pyfinity

This example shows how to integrate Pyfinity with Nextcord, a Discord.py fork.
Pyfinity works seamlessly with any Discord bot framework!
"""

import nextcord
from nextcord.ext import commands, tasks
from pyfinity import InfinityClient, InfinityAPIError
import asyncio
import os


class NextcordBot(commands.Bot):
    """Example bot using Nextcord with Pyfinity integration."""
    
    def __init__(self):
        intents = nextcord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        # Initialize Pyfinity client
        self.infinity_client = InfinityClient(
            bot_token=os.getenv('INFINITY_TOKEN', 'your_infinity_token_here'),
            bot_id=os.getenv('BOT_ID', 'your_bot_id_here')
        )
    
    async def on_ready(self):
        print(f'🚀 {self.user} has connected to Discord via Nextcord!')
        print(f'📊 Bot is in {len(self.guilds)} servers')
        
        # Start automatic stats posting
        self.post_stats_task.start()
    
    @tasks.loop(minutes=30)  # Post stats every 30 minutes
    async def post_stats_task(self):
        """Automatically post bot statistics."""
        await self.post_stats()
    
    async def post_stats(self):
        """Post current bot statistics to Infinity Bot List."""
        try:
            async with self.infinity_client:
                response = await self.infinity_client.post_bot_stats(
                    server_count=len(self.guilds),
                    user_count=len(self.users) if hasattr(self, 'users') else None
                )
                print(f"✅ Posted stats via Nextcord: {len(self.guilds)} servers")
                return response
                
        except InfinityAPIError as e:
            print(f"❌ Failed to post stats: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    @nextcord.slash_command(description="Post bot statistics manually")
    async def poststats(self, interaction: nextcord.Interaction):
        """Slash command to manually post stats."""
        await interaction.response.defer()
        
        response = await self.post_stats()
        if response:
            await interaction.followup.send(f"✅ Stats posted! Bot is in {len(self.guilds)} servers.")
        else:
            await interaction.followup.send("❌ Failed to post stats. Check console for details.")
    
    @nextcord.slash_command(description="Get bot info from Infinity Bot List")
    async def botinfo(self, interaction: nextcord.Interaction):
        """Get bot information from Infinity Bot List."""
        await interaction.response.defer()
        
        try:
            async with self.infinity_client:
                bot_info = await self.infinity_client.get_bot_info()
                
                embed = nextcord.Embed(
                    title="🤖 Infinity Bot List Info",
                    color=0x00ff00
                )
                
                # Add bot info fields (adjust based on actual API response)
                for key, value in bot_info.items():
                    if isinstance(value, (str, int, float)):
                        embed.add_field(name=key.title(), value=str(value), inline=True)
                
                await interaction.followup.send(embed=embed)
                
        except InfinityAPIError as e:
            await interaction.followup.send(f"❌ API Error: {e}")
        except Exception as e:
            await interaction.followup.send(f"❌ Unexpected error: {e}")
    
    async def on_guild_join(self, guild):
        """Post updated stats when joining a guild."""
        print(f"📈 Joined guild: {guild.name}")
        await asyncio.sleep(5)  # Brief delay to let things settle
        await self.post_stats()
    
    async def on_guild_remove(self, guild):
        """Post updated stats when leaving a guild."""
        print(f"📉 Left guild: {guild.name}")
        await asyncio.sleep(5)  # Brief delay to let things settle
        await self.post_stats()


# Example without framework-specific features (works with ANY Discord library)
class UniversalBotIntegration:
    """
    Universal bot integration that works with any Discord library.
    
    This approach can be used with ANY Discord bot framework:
    - Discord.py
    - Nextcord
    - Pycord (py-cord)
    - Disnake
    - Hikari
    - Or any custom Discord implementation
    """
    
    def __init__(self, infinity_token: str, bot_id: str):
        self.infinity_client = InfinityClient(infinity_token, bot_id)
        self.last_stats_post = None
    
    async def update_stats(self, server_count: int, user_count: int = None, shard_count: int = None):
        """
        Update bot statistics on Infinity Bot List.
        
        Call this method from your bot's framework whenever you want to update stats.
        Works with ANY Discord library!
        """
        try:
            async with self.infinity_client:
                response = await self.infinity_client.post_bot_stats(
                    server_count=server_count,
                    user_count=user_count,
                    shard_count=shard_count
                )
                
                print(f"✅ Stats updated: {server_count} servers" + 
                      (f", {user_count} users" if user_count else "") +
                      (f", {shard_count} shards" if shard_count else ""))
                
                self.last_stats_post = response
                return response
                
        except InfinityAPIError as e:
            print(f"❌ Failed to update stats: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    async def get_bot_info(self):
        """Get bot information from Infinity Bot List."""
        try:
            async with self.infinity_client:
                return await self.infinity_client.get_bot_info()
        except Exception as e:
            print(f"❌ Failed to get bot info: {e}")
            return None
    
    def setup_periodic_updates(self, get_stats_callback, interval_minutes: int = 30):
        """
        Set up periodic stats updates.
        
        Args:
            get_stats_callback: Function that returns (server_count, user_count, shard_count)
            interval_minutes: How often to post stats (default: 30 minutes)
        """
        async def update_loop():
            while True:
                try:
                    stats = get_stats_callback()
                    if stats:
                        server_count, user_count, shard_count = stats
                        await self.update_stats(server_count, user_count, shard_count)
                except Exception as e:
                    print(f"❌ Error in periodic update: {e}")
                
                await asyncio.sleep(interval_minutes * 60)
        
        # Start the update loop
        asyncio.create_task(update_loop())


async def main():
    """Example usage with any Discord library."""
    print("🌍 Universal Discord Bot Integration Example")
    print("This works with ANY Discord bot framework!")
    print("=" * 50)
    
    # Example 1: Direct usage (works with any framework)
    stats_manager = UniversalBotIntegration(
        infinity_token="your_infinity_token_here",
        bot_id="your_bot_id_here"
    )
    
    # Simulate posting stats (you'd get these from your actual bot)
    await stats_manager.update_stats(
        server_count=150,
        user_count=5000,
        shard_count=2
    )
    
    # Get bot info
    bot_info = await stats_manager.get_bot_info()
    if bot_info:
        print(f"📊 Bot info: {bot_info}")
    
    print("\n✅ Universal integration example completed!")
    print("\n📚 This same approach works with:")
    print("  • Discord.py")
    print("  • Nextcord") 
    print("  • Pycord (py-cord)")
    print("  • Disnake")
    print("  • Hikari")
    print("  • Any custom Discord implementation")


if __name__ == "__main__":
    print("🎯 Nextcord + Pyfinity Integration Example")
    print("Replace tokens with your actual values to test!")
    print("\nTo run the actual bot:")
    print("1. pip install nextcord pyfinity")
    print("2. Set your DISCORD_TOKEN, INFINITY_TOKEN, and BOT_ID")
    print("3. Uncomment the bot.run() line below")
    print()
    
    # Uncomment to run the actual Nextcord bot:
    # bot = NextcordBot()
    # bot.run(os.getenv('DISCORD_TOKEN'))
    
    # Run the universal example
    asyncio.run(main())
