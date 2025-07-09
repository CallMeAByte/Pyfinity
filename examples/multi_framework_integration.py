"""
Example: Pycord (py-cord) Integration with Pyfinity

This example shows how to integrate Pyfinity with Pycord, another Discord.py fork.
Pyfinity is framework-agnostic and works with ANY Discord bot library!
"""

import discord  # This is py-cord, not discord.py
from discord.ext import commands, tasks
from pyfinity import InfinityClient, InfinityAPIError
import asyncio
import os


class PycordBot(commands.Bot):
    """Example bot using Pycord with Pyfinity integration."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        # Initialize Pyfinity client
        self.infinity_client = InfinityClient(
            bot_token=os.getenv('INFINITY_TOKEN', 'your_infinity_token_here'),
            bot_id=os.getenv('BOT_ID', 'your_bot_id_here')
        )
    
    async def on_ready(self):
        print(f'🚀 {self.user} has connected to Discord via Pycord!')
        print(f'📊 Bot is in {len(self.guilds)} servers')
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            print(f"🔄 Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")
        
        # Start automatic stats posting
        self.post_stats_loop.start()
    
    @tasks.loop(minutes=30)
    async def post_stats_loop(self):
        """Post stats every 30 minutes."""
        await self.post_stats()
    
    async def post_stats(self):
        """Post bot statistics to Infinity Bot List."""
        try:
            async with self.infinity_client:
                response = await self.infinity_client.post_bot_stats(
                    server_count=len(self.guilds),
                    user_count=len(self.users) if hasattr(self, 'users') else None
                )
                print(f"✅ Posted stats via Pycord: {len(self.guilds)} servers")
                return response
                
        except InfinityAPIError as e:
            print(f"❌ Failed to post stats: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    @discord.slash_command(description="Post bot statistics to Infinity Bot List")
    async def stats(self, ctx: discord.ApplicationContext):
        """Slash command to post stats."""
        await ctx.defer()
        
        response = await self.post_stats()
        if response:
            embed = discord.Embed(
                title="📊 Stats Posted!",
                description=f"Updated Infinity Bot List with current statistics.",
                color=0x00ff00
            )
            embed.add_field(name="Servers", value=len(self.guilds), inline=True)
            embed.add_field(name="Users", value=len(self.users) if hasattr(self, 'users') else "N/A", inline=True)
            
            await ctx.followup.send(embed=embed)
        else:
            await ctx.followup.send("❌ Failed to post stats. Check console for details.")
    
    @discord.slash_command(description="Get bot info from Infinity Bot List")
    async def botinfo(self, ctx: discord.ApplicationContext):
        """Get bot information from Infinity Bot List."""
        await ctx.defer()
        
        try:
            async with self.infinity_client:
                bot_info = await self.infinity_client.get_bot_info()
                
                embed = discord.Embed(
                    title="🤖 Infinity Bot List Info",
                    color=0x5865f2
                )
                
                # Add bot info fields
                for key, value in bot_info.items():
                    if isinstance(value, (str, int, float)) and len(str(value)) < 1000:
                        embed.add_field(
                            name=key.replace('_', ' ').title(), 
                            value=str(value), 
                            inline=True
                        )
                
                await ctx.followup.send(embed=embed)
                
        except InfinityAPIError as e:
            await ctx.followup.send(f"❌ API Error: {e}")
        except Exception as e:
            await ctx.followup.send(f"❌ Unexpected error: {e}")


# Example for Disnake integration
"""
import disnake
from disnake.ext import commands, tasks
from pyfinity import InfinityClient, InfinityAPIError

class DisnakeBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=disnake.Intents.default())
        
        self.infinity_client = InfinityClient(
            bot_token="your_infinity_token_here",
            bot_id="your_bot_id_here"
        )
    
    async def on_ready(self):
        print(f'{self.user} connected via Disnake!')
        self.post_stats_task.start()
    
    @tasks.loop(minutes=30)
    async def post_stats_task(self):
        try:
            async with self.infinity_client:
                await self.infinity_client.post_bot_stats(
                    server_count=len(self.guilds),
                    user_count=len(self.users)
                )
                print(f"Posted stats via Disnake: {len(self.guilds)} servers")
        except Exception as e:
            print(f"Failed to post stats: {e}")
    
    @disnake.slash_command(description="Post stats to Infinity Bot List")
    async def stats(self, inter: disnake.ApplicationCommandInteraction):
        # Same logic as other frameworks!
        pass
"""


# Example for Hikari integration (async Discord library)
"""
import hikari
import lightbulb
from pyfinity import InfinityClient, InfinityAPIError

class HikariBot:
    def __init__(self):
        self.bot = hikari.GatewayBot(token="your_discord_token_here")
        self.infinity_client = InfinityClient(
            bot_token="your_infinity_token_here",
            bot_id="your_bot_id_here"
        )
        
        # Set up event listeners
        self.bot.listen()(self.on_ready)
    
    async def on_ready(self, event: hikari.StartedEvent):
        print(f"Hikari bot started!")
        
        # Get guild count
        guilds = await self.bot.rest.fetch_my_guilds()
        
        # Post stats
        try:
            async with self.infinity_client:
                await self.infinity_client.post_bot_stats(
                    server_count=len(guilds)
                )
                print(f"Posted stats via Hikari: {len(guilds)} servers")
        except Exception as e:
            print(f"Failed to post stats: {e}")
    
    def run(self):
        self.bot.run()
"""


# Generic framework-agnostic approach
class FrameworkAgnosticStatsManager:
    """
    A completely framework-agnostic stats manager.
    
    This works with ANY Discord library or even custom implementations!
    """
    
    def __init__(self, infinity_token: str, bot_id: str):
        self.infinity_client = InfinityClient(infinity_token, bot_id)
        self.stats_history = []
    
    async def post_stats(self, server_count: int, user_count: int = None, **kwargs):
        """
        Post stats to Infinity Bot List.
        
        This method is completely framework-independent!
        """
        try:
            async with self.infinity_client:
                response = await self.infinity_client.post_bot_stats(
                    server_count=server_count,
                    user_count=user_count,
                    shard_count=kwargs.get('shard_count'),
                    shard_list=kwargs.get('shard_list')
                )
                
                # Log the stats
                self.stats_history.append({
                    'timestamp': asyncio.get_event_loop().time(),
                    'server_count': server_count,
                    'user_count': user_count,
                    'response': response
                })
                
                print(f"✅ Stats posted: {server_count} servers" + 
                      (f", {user_count} users" if user_count else ""))
                
                return response
                
        except InfinityAPIError as e:
            print(f"❌ API Error: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    async def get_bot_info(self):
        """Get bot info - works with any framework!"""
        try:
            async with self.infinity_client:
                return await self.infinity_client.get_bot_info()
        except Exception as e:
            print(f"❌ Failed to get bot info: {e}")
            return None
    
    def get_stats_history(self):
        """Get the history of stats posts."""
        return self.stats_history.copy()


async def demo_framework_agnostic():
    """Demonstrate framework-agnostic usage."""
    print("🌐 Framework-Agnostic Demo")
    print("This works with ANY Discord library!")
    print("-" * 40)
    
    # Create stats manager
    stats_manager = FrameworkAgnosticStatsManager(
        infinity_token="your_infinity_token_here",
        bot_id="your_bot_id_here"
    )
    
    # Simulate posting stats from different frameworks
    frameworks = [
        ("Discord.py", 150, 5000),
        ("Nextcord", 275, 8500),
        ("Pycord", 320, 12000),
        ("Disnake", 89, 3200),
        ("Hikari", 445, 18000),
        ("Custom Implementation", 67, 2100)
    ]
    
    for framework, servers, users in frameworks:
        print(f"\n📊 Posting stats from {framework}:")
        await stats_manager.post_stats(servers, users)
    
    # Show stats history
    print(f"\n📈 Posted stats for {len(frameworks)} different frameworks!")
    print("✅ Pyfinity works universally!")


async def main():
    """Main demo function."""
    print("🎯 Multi-Framework Discord Bot Integration")
    print("Pyfinity works with ALL Discord bot frameworks!")
    print("=" * 60)
    
    await demo_framework_agnostic()
    
    print("\n" + "=" * 60)
    print("📚 Frameworks that work with Pyfinity:")
    print("  ✅ Discord.py (original)")
    print("  ✅ Nextcord (discord.py fork)")
    print("  ✅ Pycord/py-cord (discord.py fork)")
    print("  ✅ Disnake (discord.py fork)")
    print("  ✅ Hikari (standalone async library)")
    print("  ✅ Discord4J (if using Python wrapper)")
    print("  ✅ Any custom Discord implementation")
    print("  ✅ Even non-Discord bots (just pass server/user counts)")
    print("\n🎉 Pyfinity is truly universal!")


if __name__ == "__main__":
    print("🔧 Pycord + Pyfinity Integration Example")
    print("This demonstrates Pyfinity's universal compatibility!")
    print("\nTo run with actual Pycord:")
    print("1. pip install py-cord pyfinity")
    print("2. Set your tokens in environment variables")
    print("3. Uncomment the bot.run() line below")
    print()
    
    # Uncomment to run the actual Pycord bot:
    # bot = PycordBot()
    # bot.run(os.getenv('DISCORD_TOKEN'))
    
    # Run the demo
    asyncio.run(main())
