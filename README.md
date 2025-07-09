# Pyfinity 🚀

<div align="center">
  <div style="background-color: #000000; padding: 30px; border-radius: 15px; display: inline-block;">
    <img src="assets/pyfinitylogo.png" alt="Pyfinity - Python Infinity Snake Logo" width="200" height="200">
  </div>
  <br><br>
  <strong>A Python wrapper for the Infinity Bot List API, designed for Discord bot developers.</strong>
</div>

## What is Pyfinity?

Pyfinity is a lightweight Python library that makes it easy to post your Discord bot's statistics to the [Infinity Bot List](https://infinitybots.gg). It handles all the API communication for you, so you can focus on building your bot.

## What does it do?

- **Posts bot statistics** (server count, user count) to Infinity Bot List
- **Supports both async and sync** Python code
- **Handles sharding** for large bots with advanced shard statistics
- **Provides error handling** with custom exceptions
- **Works with ANY Discord framework** - Discord.py, Nextcord, Pycord, Disnake, Hikari, and more!
- **Automatic hourly refresh** - Keep your stats updated without manual intervention
- **Smart rate limiting** - Automatic 429 detection and retry with exponential backoff
- **Built-in monitoring** - Track rate limits and refresh status

## Installation

### Requirements
- Python 3.13 or higher
- Only dependency: `httpx` (automatically installed)

### Install from PyPI
```bash
pip install pyfinity
```

### For Any Discord Framework
Pyfinity works with **ANY** Discord bot library! Here are some examples:

```bash
# Discord.py (original)
pip install pyfinity discord.py

# Nextcord (discord.py fork)
pip install pyfinity nextcord

# Pycord (py-cord)
pip install pyfinity py-cord

# Disnake (discord.py fork)
pip install pyfinity disnake

# Hikari (standalone async library)
pip install pyfinity hikari
```

### Development Installation
If you want to contribute or run tests:
```bash
git clone https://github.com/your-username/pyfinity.git
cd pyfinity
pip install -e ".[dev]"
```

## How to track statistics in your bot

### Basic Usage (Async)

```python
import asyncio
from pyfinity import InfinityClient

async def main():
    client = InfinityClient(
        bot_token="your_infinity_token_here",
        bot_id="your_bot_id_here"
    )
    
    async with client:
        # Post your bot's statistics
        await client.post_bot_stats(
            server_count=150,
            user_count=5000
        )
        print("✅ Stats posted successfully!")

asyncio.run(main())
```

### Discord.py Integration

```python
import discord
from discord.ext import commands, tasks
from pyfinity import InfinityClient

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.default())
        self.infinity_client = InfinityClient(
            bot_token="your_infinity_token",
            bot_id=str(self.user.id)
        )
    
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        self.post_stats.start()  # Start posting stats every 30 minutes
    
    @tasks.loop(minutes=30)
    async def post_stats(self):
        try:
            await self.infinity_client.post_bot_stats(
                server_count=len(self.guilds),
                user_count=len(self.users)
            )
            print("📊 Posted stats to Infinity Bot List")
        except Exception as e:
            print(f"Failed to post stats: {e}")

bot = MyBot()
bot.run('your_discord_token')
```

### Universal Integration (Works with ANY framework)

```python
from pyfinity import InfinityClient

# This approach works with Discord.py, Nextcord, Pycord, Disnake, Hikari, etc.
class UniversalStatsManager:
    def __init__(self, infinity_token: str, bot_id: str):
        self.infinity_client = InfinityClient(infinity_token, bot_id)
    
    async def update_stats(self, server_count: int, user_count: int = None):
        async with self.infinity_client:
            return await self.infinity_client.post_bot_stats(
                server_count=server_count,
                user_count=user_count
            )

# Use with any Discord framework:
stats_manager = UniversalStatsManager("your_token", "your_bot_id")
await stats_manager.update_stats(len(guilds), len(users))
```

## Statistics you can track

### Basic Statistics
- **Server Count**: Number of servers your bot is in
- **User Count**: Total number of users your bot serves

### Shard Statistics (for large bots)
```python
# Post shard information
await client.post_bot_stats(
    server_count=1000,
    user_count=50000,
    shard_count=4,
    shard_list=[0, 1, 2, 3]
)

# Post per-shard statistics
await client.post_shard_stats(
    shard_id=0,
    server_count=250,
    user_count=12500
)
```

### Getting Your API Token

1. Visit [Infinity Bot List](https://infinitybots.gg)
2. Add your bot to the list
3. Get your API token from your bot's page
4. Use it with Pyfinity

## Troubleshooting

### 526 Error Fix ✅

If you encountered a **526 error** when posting stats, this has been **fixed** in the latest version:

- ✅ **Updated API base URL** to use the correct endpoint
- ✅ **Fixed authorization headers** for proper authentication  
- ✅ **Enhanced SSL handling** for better connection reliability
- ✅ **Improved error handling** with detailed error messages

**The fix automatically handles:**
- Correct API endpoint (`https://spider.infinitybots.gg/api`)
- Proper header formatting
- SSL certificate validation
- Connection redirects

Simply update to the latest version and the 526 error should be resolved!

### Common Issues

1. **Authentication Error**: Make sure your API token is correct
2. **Bot Not Found**: Ensure your bot is added to Infinity Bot List
3. **Network Issues**: Check your internet connection and firewall settings

## Rate Limiting & Auto-Refresh

Pyfinity includes built-in rate limiting and automatic refresh features:

### Automatic Hourly Refresh
```python
# Auto-refresh is enabled by default
client = InfinityClient(
    bot_token="your_token",
    bot_id="your_bot_id",
    auto_refresh=True  # Stats refresh every hour automatically
)

# Check refresh status
refresh_info = client.get_auto_refresh_info()
print(f"Next refresh in: {refresh_info['seconds_until_next']} seconds")
```

### Rate Limit Handling
```python
# Automatic retry on 429 rate limits with exponential backoff
# No additional code needed - handled automatically!

# Check current rate limits
rate_info = client.get_rate_limit_info()
print(f"Requests remaining: {rate_info['remaining']}")
print(f"Reset in: {rate_info['reset_in_seconds']} seconds")
```

### Benefits
- **🔄 Hourly refresh**: Your stats stay current automatically
- **⚡ Smart retries**: 429 errors are handled with exponential backoff
- **📊 Rate monitoring**: Track your API usage in real-time
- **🛡️ Protection**: Prevents hitting rate limits with intelligent spacing

## Framework Compatibility

Pyfinity is designed to work with **any Discord bot framework**:

- ✅ **Discord.py** (original)
- ✅ **Nextcord** (discord.py fork)
- ✅ **Pycord** (py-cord, discord.py fork)
- ✅ **Disnake** (discord.py fork)
- ✅ **Hikari** (standalone async library)
- ✅ **Any custom Discord implementation**

Since Pyfinity only needs your bot's server/user counts, it works with any framework that can provide these numbers. Check the `examples/` directory for specific integration examples!

---

**That's it!** Pyfinity handles the rest, automatically posting your bot's statistics to help users discover your bot on Infinity Bot List.
