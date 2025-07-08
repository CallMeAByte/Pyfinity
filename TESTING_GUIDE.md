# 🤖 How to Test Your Discord Bot with Pyfinity

This guide shows you different ways to test your Discord bot integration with the Infinity Bot List API using Pyfinity.

## 📋 Prerequisites

1. **Python 3.13.5** ✅ (Already installed)
2. **Pyfinity library** ✅ (Your library)
3. **Discord.py** (Optional - for real Discord bot)
4. **API Tokens** (From Infinity Bot List)

## 🧪 Testing Methods

### 1. **Basic Library Testing** (Already working)
```bash
# Test the core library
python test_pyfinity.py

# Run unit tests
python -m pytest tests/ -v
```

### 2. **Mock Bot Testing** (No Discord connection needed)
```bash
# Test with simulated bot data
python test_discord_bot.py
```

### 3. **Integration Testing**
```bash
# Test bot integration scenarios
python test_bot_integration.py
```

### 4. **Real Discord Bot Testing**

#### Step 1: Install Discord.py
```bash
pip install discord.py
```

#### Step 2: Get Required Tokens
1. **Discord Bot Token**: 
   - Go to https://discord.com/developers/applications
   - Create a new application
   - Go to "Bot" section
   - Copy the token

2. **Infinity Bot List Token**:
   - Go to https://infinitybots.gg
   - Add your bot to the list
   - Get your API token from your bot's page

#### Step 3: Set Environment Variables
```bash
# Windows PowerShell
$env:DISCORD_TOKEN="your_discord_token_here"
$env:INFINITY_TOKEN="your_infinity_token_here"
$env:BOT_ID="your_bot_discord_id_here"

# Or create a .env file (recommended)
```

#### Step 4: Test with Real Bot
```bash
python test_real_bot.py
```

## 🔧 Creating Your Own Test Bot

### Async Discord Bot Example

```python
import discord
from discord.ext import commands, tasks
from pyfinity import InfinityClient, InfinityAPIError
import os

class MyTestBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        # Initialize Pyfinity
        self.infinity_client = InfinityClient(
            bot_token=os.getenv('INFINITY_TOKEN'),
            bot_id=os.getenv('BOT_ID')
        )
    
    async def on_ready(self):
        print(f'{self.user} connected to Discord!')
        print(f'Bot is in {len(self.guilds)} servers')
        
        # Start stats posting
        self.post_stats_loop.start()
    
    @tasks.loop(minutes=30)  # Post every 30 minutes
    async def post_stats_loop(self):
        await self.post_stats()
    
    async def post_stats(self):
        try:
            async with self.infinity_client:
                response = await self.infinity_client.post_bot_stats(
                    server_count=len(self.guilds),
                    user_count=len(self.users)
                )
                print(f"📊 Posted stats: {len(self.guilds)} servers")
        except InfinityAPIError as e:
            print(f"❌ Failed to post stats: {e}")
    
    @commands.command(name='teststats')
    async def test_stats(self, ctx):
        """Test command to manually post stats."""
        await self.post_stats()
        await ctx.send("📊 Stats posted to Infinity Bot List!")
    
    @commands.command(name='botinfo')
    async def bot_info(self, ctx):
        """Get bot info from Infinity Bot List."""
        try:
            async with self.infinity_client:
                info = await self.infinity_client.get_bot_info()
                await ctx.send(f"📋 Bot info: {info}")
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")

# Run the bot
bot = MyTestBot()
bot.run(os.getenv('DISCORD_TOKEN'))
```

## 📊 Testing Checklist

### ✅ Basic Tests
- [ ] Library imports correctly
- [ ] Client initialization works
- [ ] Error handling functions
- [ ] Both async and sync clients work

### ✅ Integration Tests
- [ ] Stats posting works
- [ ] Bot info retrieval works
- [ ] Error handling with invalid tokens
- [ ] Context manager usage
- [ ] Periodic stats posting

### ✅ Real Bot Tests
- [ ] Discord bot connects successfully
- [ ] Stats are posted to Infinity Bot List
- [ ] Bot responds to commands
- [ ] Error handling in production environment
- [ ] Periodic stats updates work

## 🐛 Common Issues & Solutions

### Issue: "Event loop already running"
**Solution**: This happens with sync client in async context. Use async client instead:
```python
# Instead of:
client = SyncInfinityClient(token, bot_id)
response = client.post_bot_stats(10)

# Use:
client = InfinityClient(token, bot_id)
async with client:
    response = await client.post_bot_stats(10)
```

### Issue: "API request failed with status 404"
**Solution**: Check your tokens and bot ID:
1. Verify your Infinity Bot List token is correct
2. Ensure your bot is added to Infinity Bot List
3. Check that your bot ID matches your Discord bot's ID

### Issue: "Unauthorized" errors
**Solution**: 
1. Get a fresh API token from Infinity Bot List
2. Make sure you're using the correct bot token format
3. Verify your bot is approved on the list

## 🚀 Next Steps

1. **Start with mock testing** to verify your code logic
2. **Get real tokens** from Discord and Infinity Bot List  
3. **Test with a development bot** first
4. **Deploy to production** once everything works
5. **Monitor logs** for any API errors

## 📚 Additional Resources

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Infinity Bot List](https://infinitybots.gg)
- [API Documentation](https://spider.infinitybots.gg)
- Your `examples/` directory for more examples

Happy testing! 🎉
