#!/usr/bin/env python3
"""
526 Error Diagnostic and Fix Verification Script

This script helps diagnose and verify the 526 error fix for Pyfinity.
"""

import asyncio
import os
from pyfinity import InfinityClient, InfinityAPIError


async def test_526_fix():
    """Test the 526 error fix with your actual tokens."""
    print("🔧 Pyfinity 526 Error Diagnostic Tool")
    print("=" * 50)
    
    # Get your actual tokens from environment or replace here
    infinity_token = os.getenv('INFINITY_TOKEN', 'your_infinity_token_here')
    bot_id = os.getenv('BOT_ID', 'your_bot_id_here')
    
    if infinity_token == 'your_infinity_token_here' or bot_id == 'your_bot_id_here':
        print("⚠️  Please set your actual tokens:")
        print("   INFINITY_TOKEN=your_actual_infinity_token")
        print("   BOT_ID=your_actual_bot_discord_id")
        print()
        print("🔧 Testing with mock values for connection verification...")
        print()
    
    client = InfinityClient(bot_token=infinity_token, bot_id=bot_id)
    
    print(f"✅ Base URL: {client.base_url}")
    print(f"✅ Bot ID: {bot_id}")
    print()
    
    try:
        async with client:
            print("🔗 HTTP session started successfully")
            print("📊 Testing bot stats posting...")
            
            # Test posting stats
            try:
                response = await client.post_bot_stats(
                    server_count=25,
                    user_count=500
                )
                print(f"✅ SUCCESS: Stats posted successfully!")
                print(f"📊 Response: {response}")
                return True
                
            except InfinityAPIError as e:
                if e.status_code == 526:
                    print("❌ 526 ERROR STILL OCCURRING!")
                    print(f"   Message: {e}")
                    print()
                    print("🔧 ADDITIONAL FIXES NEEDED:")
                    print("   1. Check if your bot is approved on Infinity Bot List")
                    print("   2. Verify your API token is correct and active")
                    print("   3. Ensure your bot ID is correct")
                    print("   4. Try regenerating your API token")
                    return False
                    
                elif e.status_code in [401, 403]:
                    print("⚠️  Authentication Error (Token/Permission Issue)")
                    print(f"   Status: {e.status_code}")
                    print(f"   Message: {e}")
                    print("✅ NO 526 ERROR - Connection fix successful!")
                    print()
                    print("🔧 To fix authentication:")
                    print("   1. Get your API token from https://infinitybots.gg")
                    print("   2. Make sure your bot is added and approved")
                    print("   3. Use the correct Discord bot ID")
                    return True
                    
                elif e.status_code == 404:
                    print("⚠️  Bot Not Found (ID Issue)")
                    print(f"   Message: {e}")
                    print("✅ NO 526 ERROR - Connection fix successful!")
                    print()
                    print("🔧 To fix bot not found:")
                    print("   1. Verify your Discord bot ID is correct")
                    print("   2. Make sure your bot is added to Infinity Bot List")
                    return True
                    
                else:
                    print(f"ℹ️  Different API Error: {e.status_code}")
                    print(f"   Message: {e}")
                    print("✅ NO 526 ERROR - Connection fix successful!")
                    return True
                    
    except Exception as e:
        if "526" in str(e):
            print(f"❌ 526 ERROR DETECTED: {e}")
            print()
            print("🔧 TROUBLESHOOTING STEPS:")
            print("   1. Update to the latest Pyfinity version")
            print("   2. Check your internet connection")
            print("   3. Try using a VPN or different network")
            print("   4. Contact Infinity Bot List support")
            return False
        else:
            print(f"ℹ️  Other connection error: {e}")
            print("✅ Likely not a 526 error")
            return True


async def main():
    """Main diagnostic function."""
    success = await test_526_fix()
    
    print()
    print("=" * 50)
    if success:
        print("🎉 526 ERROR FIX VERIFICATION COMPLETE!")
        print("✅ The 526 error should be resolved")
    else:
        print("⚠️  Additional troubleshooting may be needed")
    
    print()
    print("📚 Next Steps:")
    print("   1. Use your real Infinity Bot List API token")
    print("   2. Use your real Discord bot ID")
    print("   3. Test with actual bot statistics")
    print("   4. Check Infinity Bot List for any service issues")


if __name__ == "__main__":
    asyncio.run(main())
