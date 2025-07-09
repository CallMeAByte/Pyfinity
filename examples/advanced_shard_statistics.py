"""
Example: Advanced Shard Statistics with Pyfinity

This example demonstrates all the shard-related features in Pyfinity,
including basic shard stats, per-shard stats, batch updates, and analytics.
"""

import asyncio
from typing import Dict, Any
from pyfinity import InfinityClient, SyncInfinityClient, InfinityAPIError


class ShardStatsDemo:
    """Demonstration of advanced shard statistics features."""
    
    def __init__(self, infinity_token: str, bot_id: str):
        self.async_client = InfinityClient(infinity_token, bot_id)
        self.sync_client = SyncInfinityClient(infinity_token, bot_id)
        
        # Mock shard data for demonstration
        self.mock_shard_data = {
            0: {"servers": 150, "users": 3000},
            1: {"servers": 120, "users": 2400},
            2: {"servers": 180, "users": 3600},
            3: {"servers": 90, "users": 1800},
            4: {"servers": 160, "users": 3200}
        }
    
    async def demo_basic_shard_stats(self):
        """Demo basic shard statistics posting."""
        print("📊 Demo: Basic Shard Statistics")
        print("-" * 40)
        
        try:
            async with self.async_client as client:
                # Post basic shard info with total counts
                total_servers = sum(stats["servers"] for stats in self.mock_shard_data.values())
                total_users = sum(stats["users"] for stats in self.mock_shard_data.values())
                shard_list = list(self.mock_shard_data.keys())
                
                response = await client.post_bot_stats(
                    server_count=total_servers,
                    user_count=total_users,
                    shard_count=len(shard_list),
                    shard_list=shard_list
                )
                
                print(f"✅ Posted basic shard stats: {response}")
                print(f"📈 Total: {total_servers} servers, {total_users} users across {len(shard_list)} shards")
                
        except InfinityAPIError as e:
            print(f"❌ API Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    async def demo_per_shard_stats(self):
        """Demo per-shard statistics posting."""
        print("\n📋 Demo: Per-Shard Statistics")
        print("-" * 40)
        
        try:
            async with self.async_client as client:
                # Post stats for each shard individually
                for shard_id, stats in self.mock_shard_data.items():
                    response = await client.post_shard_stats(
                        shard_id=shard_id,
                        server_count=stats["servers"],
                        user_count=stats["users"]
                    )
                    print(f"✅ Shard {shard_id}: {stats['servers']} servers, {stats['users']} users")
                
                # Get info for a specific shard
                shard_info = await client.get_shard_info(0)
                print(f"📊 Shard 0 info: {shard_info}")
                
        except InfinityAPIError as e:
            print(f"❌ API Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    async def demo_batch_shard_stats(self):
        """Demo batch shard statistics posting."""
        print("\n🚀 Demo: Batch Shard Statistics")
        print("-" * 40)
        
        try:
            async with self.async_client as client:
                # Post all shard stats at once
                response = await client.post_batch_shard_stats(self.mock_shard_data)
                print(f"✅ Posted batch shard stats: {response}")
                
                # Get all shard info
                all_shards = await client.get_all_shard_info()
                print(f"📊 All shards info: {all_shards}")
                
        except InfinityAPIError as e:
            print(f"❌ API Error (Note: Batch endpoints might not be available): {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    def demo_shard_analytics(self):
        """Demo shard analytics and reporting."""
        print("\n📈 Demo: Shard Analytics")
        print("-" * 40)
        
        try:
            # Analyze shard distribution
            analysis = self.async_client.analyze_shard_distribution(self.mock_shard_data)
            print("📊 SHARD ANALYSIS:")
            print(f"   Total Shards: {analysis['summary']['total_shards']}")
            print(f"   Total Servers: {analysis['summary']['total_servers']:,}")
            print(f"   Total Users: {analysis['summary']['total_users']:,}")
            print(f"   Balance Status: {analysis['insights']['balance_recommendation']}")
            
            # Generate full report
            print("\n" + "=" * 50)
            report = self.async_client.generate_shard_report(self.mock_shard_data)
            print(report)
            
        except Exception as e:
            print(f"❌ Error in analytics: {e}")
    
    def demo_shard_calculation(self):
        """Demo shard calculation utilities."""
        print("\n🧮 Demo: Shard Calculation Utilities")
        print("-" * 40)
        
        try:
            # Calculate shard distribution for a new bot
            total_servers = 1000
            total_users = 50000
            shard_list = [0, 1, 2, 3, 4, 5, 6, 7]
            
            calculated_stats = self.async_client.calculate_shard_stats(
                total_servers, total_users, shard_list
            )
            
            print(f"📊 Calculated distribution for {total_servers} servers, {total_users} users:")
            for shard_id, stats in calculated_stats.items():
                print(f"   Shard {shard_id}: {stats['servers']} servers, {stats['users']} users")
                
        except Exception as e:
            print(f"❌ Error in calculation: {e}")
    
    def demo_sync_shard_features(self):
        """Demo synchronous shard features."""
        print("\n🔄 Demo: Synchronous Shard Features")
        print("-" * 40)
        
        try:
            # Post shard stats synchronously
            response = self.sync_client.post_shard_stats(
                shard_id=0,
                server_count=150,
                user_count=3000
            )
            print(f"✅ Sync shard stats posted: {response}")
            
            # Get shard info synchronously
            shard_info = self.sync_client.get_shard_info(0)
            print(f"📊 Sync shard info: {shard_info}")
            
            # Use sync analytics
            analysis = self.sync_client.analyze_shard_distribution(self.mock_shard_data)
            print(f"📈 Sync analysis: {analysis['insights']['balance_recommendation']}")
            
        except InfinityAPIError as e:
            print(f"❌ Sync API Error: {e}")
        except Exception as e:
            print(f"❌ Sync Error: {e}")
    
    async def run_all_demos(self):
        """Run all shard demonstration examples."""
        print("🎯 PYFINITY SHARD STATISTICS DEMO")
        print("=" * 60)
        
        # Run async demos
        await self.demo_basic_shard_stats()
        await self.demo_per_shard_stats()
        await self.demo_batch_shard_stats()
        
        # Run utility demos
        self.demo_shard_analytics()
        self.demo_shard_calculation()
        self.demo_sync_shard_features()
        
        print("\n" + "=" * 60)
        print("✅ All shard demos completed!")


async def main():
    """Run the shard statistics demo."""
    # Replace with your actual tokens
    demo = ShardStatsDemo(
        infinity_token="your_infinity_token_here",
        bot_id="your_bot_id_here"
    )
    
    await demo.run_all_demos()


if __name__ == "__main__":
    print("🚀 Advanced Shard Statistics Demo")
    print("This demo shows all shard features in Pyfinity")
    print("Replace the tokens with your actual values to test with the API")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
