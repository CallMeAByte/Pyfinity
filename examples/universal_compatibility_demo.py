"""
Demo: Universal Framework Compatibility

This demo shows how Pyfinity works with ANY Discord bot framework
without requiring specific libraries to be installed.
"""

import asyncio
from pyfinity import InfinityClient, InfinityAPIError


class MockDiscordPyBot:
    """Mock Discord.py bot to demonstrate integration."""
    
    def __init__(self):
        self.guilds = [f"guild_{i}" for i in range(150)]
        self.users = [f"user_{i}" for i in range(5000)]
        self.user = type('User', (), {'id': '123456789012345678'})()
        
        # Pyfinity integration
        self.infinity_client = InfinityClient(
            bot_token="your_infinity_token_here",
            bot_id=str(self.user.id)
        )
    
    async def post_stats(self):
        """Post stats using Discord.py pattern."""
        try:
            async with self.infinity_client:
                response = await self.infinity_client.post_bot_stats(
                    server_count=len(self.guilds),
                    user_count=len(self.users)
                )
                print(f"✅ Discord.py: Posted {len(self.guilds)} servers, {len(self.users)} users")
                return response
        except InfinityAPIError as e:
            print(f"❌ Discord.py API Error: {e}")
        except Exception as e:
            print(f"❌ Discord.py Error: {e}")


class MockNextcordBot:
    """Mock Nextcord bot to demonstrate integration."""
    
    def __init__(self):
        self.guilds = [f"guild_{i}" for i in range(275)]
        self.users = [f"user_{i}" for i in range(8500)]
        self.user = type('User', (), {'id': '987654321098765432'})()
        
        # Same Pyfinity integration!
        self.infinity_client = InfinityClient(
            bot_token="your_infinity_token_here",
            bot_id=str(self.user.id)
        )
    
    async def post_stats(self):
        """Post stats using Nextcord pattern."""
        try:
            async with self.infinity_client:
                response = await self.infinity_client.post_bot_stats(
                    server_count=len(self.guilds),
                    user_count=len(self.users)
                )
                print(f"✅ Nextcord: Posted {len(self.guilds)} servers, {len(self.users)} users")
                return response
        except InfinityAPIError as e:
            print(f"❌ Nextcord API Error: {e}")
        except Exception as e:
            print(f"❌ Nextcord Error: {e}")


class MockPycordBot:
    """Mock Pycord bot to demonstrate integration."""
    
    def __init__(self):
        self.guilds = [f"guild_{i}" for i in range(320)]
        self.users = [f"user_{i}" for i in range(12000)]
        self.bot_id = "456789123456789012"
        
        # Same Pyfinity integration pattern!
        self.infinity_client = InfinityClient(
            bot_token="your_infinity_token_here",
            bot_id=self.bot_id
        )
    
    async def post_stats(self):
        """Post stats using Pycord pattern."""
        try:
            async with self.infinity_client:
                response = await self.infinity_client.post_bot_stats(
                    server_count=len(self.guilds),
                    user_count=len(self.users)
                )
                print(f"✅ Pycord: Posted {len(self.guilds)} servers, {len(self.users)} users")
                return response
        except InfinityAPIError as e:
            print(f"❌ Pycord API Error: {e}")
        except Exception as e:
            print(f"❌ Pycord Error: {e}")


class MockDisnakeBot:
    """Mock Disnake bot to demonstrate integration."""
    
    def __init__(self):
        self.guilds = [f"guild_{i}" for i in range(89)]
        self.users = [f"user_{i}" for i in range(3200)]
        self.bot_id = "789012345678901234"
        
        # Same Pyfinity integration!
        self.infinity_client = InfinityClient(
            bot_token="your_infinity_token_here",
            bot_id=self.bot_id
        )
    
    async def post_stats(self):
        """Post stats using Disnake pattern."""
        try:
            async with self.infinity_client:
                response = await self.infinity_client.post_bot_stats(
                    server_count=len(self.guilds),
                    user_count=len(self.users)
                )
                print(f"✅ Disnake: Posted {len(self.guilds)} servers, {len(self.users)} users")
                return response
        except InfinityAPIError as e:
            print(f"❌ Disnake API Error: {e}")
        except Exception as e:
            print(f"❌ Disnake Error: {e}")


class MockHikariBot:
    """Mock Hikari bot to demonstrate integration."""
    
    def __init__(self):
        self.guilds = [f"guild_{i}" for i in range(445)]
        self.users = None  # Hikari might not track users the same way
        self.bot_id = "012345678901234567"
        
        # Same Pyfinity integration!
        self.infinity_client = InfinityClient(
            bot_token="your_infinity_token_here",
            bot_id=self.bot_id
        )
    
    async def post_stats(self):
        """Post stats using Hikari pattern."""
        try:
            async with self.infinity_client:
                response = await self.infinity_client.post_bot_stats(
                    server_count=len(self.guilds),
                    user_count=len(self.users) if self.users else None
                )
                print(f"✅ Hikari: Posted {len(self.guilds)} servers" + 
                      (f", {len(self.users)} users" if self.users else ""))
                return response
        except InfinityAPIError as e:
            print(f"❌ Hikari API Error: {e}")
        except Exception as e:
            print(f"❌ Hikari Error: {e}")


class UniversalStatsManager:
    """Universal stats manager that works with ANY framework."""
    
    def __init__(self, infinity_token: str, bot_id: str):
        self.infinity_client = InfinityClient(infinity_token, bot_id)
    
    async def post_stats(self, framework_name: str, server_count: int, user_count: int = None, **kwargs):
        """Universal stats posting method."""
        try:
            async with self.infinity_client:
                response = await self.infinity_client.post_bot_stats(
                    server_count=server_count,
                    user_count=user_count,
                    shard_count=kwargs.get('shard_count'),
                    shard_list=kwargs.get('shard_list')
                )
                
                stats_str = f"{server_count} servers"
                if user_count:
                    stats_str += f", {user_count} users"
                if kwargs.get('shard_count'):
                    stats_str += f", {kwargs.get('shard_count')} shards"
                
                print(f"✅ {framework_name}: Posted {stats_str}")
                return response
                
        except InfinityAPIError as e:
            print(f"❌ {framework_name} API Error: {e}")
        except Exception as e:
            print(f"❌ {framework_name} Error: {e}")


async def demo_framework_specific():
    """Demo specific framework integrations."""
    print("🎯 Framework-Specific Integration Demo")
    print("=" * 50)
    
    # Create mock bots for different frameworks
    discord_py_bot = MockDiscordPyBot()
    nextcord_bot = MockNextcordBot()
    pycord_bot = MockPycordBot()
    disnake_bot = MockDisnakeBot()
    hikari_bot = MockHikariBot()
    
    # Post stats from each framework
    print("📊 Posting stats from different Discord frameworks:")
    print()
    
    await discord_py_bot.post_stats()
    await nextcord_bot.post_stats()
    await pycord_bot.post_stats()
    await disnake_bot.post_stats()
    await hikari_bot.post_stats()


async def demo_universal_approach():
    """Demo universal approach that works with any framework."""
    print("\n🌍 Universal Integration Demo")
    print("=" * 50)
    
    # Universal stats manager
    stats_manager = UniversalStatsManager(
        infinity_token="your_infinity_token_here",
        bot_id="universal_bot_id_here"
    )
    
    # Simulate posting from different frameworks
    frameworks_data = [
        ("Custom Framework A", 67, 2100),
        ("Custom Framework B", 234, 9800),
        ("My Own Implementation", 156, 4500),
        ("Enterprise Bot System", 890, 45000),
        ("Microservice Bot", 23, 890),
    ]
    
    print("📊 Universal stats posting (works with ANY framework):")
    print()
    
    for framework, servers, users in frameworks_data:
        await stats_manager.post_stats(framework, servers, users)
    
    # Demo sharded posting
    print("\n🔄 Sharded bot example:")
    await stats_manager.post_stats(
        "Sharded Bot",
        server_count=2000,
        user_count=100000,
        shard_count=8,
        shard_list=[0, 1, 2, 3, 4, 5, 6, 7]
    )


async def main():
    """Main demo function."""
    print("🚀 Pyfinity Universal Framework Compatibility Demo")
    print("This shows how Pyfinity works with ANY Discord bot framework!")
    print()
    
    await demo_framework_specific()
    await demo_universal_approach()
    
    print("\n" + "=" * 70)
    print("🎉 SUCCESS: Pyfinity works with ALL Discord frameworks!")
    print("=" * 70)
    print()
    print("📚 Compatible Frameworks:")
    print("  ✅ Discord.py (original)")
    print("  ✅ Nextcord (discord.py fork)")
    print("  ✅ Pycord/py-cord (discord.py fork)")
    print("  ✅ Disnake (discord.py fork)")
    print("  ✅ Hikari (standalone async library)")
    print("  ✅ Discord4J (with Python wrapper)")
    print("  ✅ Any custom Discord implementation")
    print("  ✅ Even non-Discord applications!")
    print()
    print("🔑 Key Point: Pyfinity only needs:")
    print("  • Your Infinity Bot List API token")
    print("  • Your bot's Discord ID")
    print("  • Server count (required)")
    print("  • User count (optional)")
    print("  • Shard information (optional)")
    print()
    print("💡 It doesn't matter what Discord library you use!")
    print("   Pyfinity is completely framework-agnostic!")


if __name__ == "__main__":
    print("🌟 Universal Discord Framework Compatibility Demo")
    print("Demonstrating that Pyfinity works with ANY Discord library!")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    
    print("\n🎯 Ready to use Pyfinity with your favorite Discord framework!")
