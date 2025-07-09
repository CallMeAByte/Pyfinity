#!/usr/bin/env python3
"""
Test script to verify Pyfinity functionality
"""

from pyfinity import InfinityClient, SyncInfinityClient, InfinityAPIError, hello_world, __version__


def main():
    """Test the main functionality."""
    print("🚀 Testing Pyfinity...")
    print()
    
    # Test hello world
    print("Testing hello_world():")
    print(f"  {hello_world()}")
    print()
    
    # Test version
    print(f"Version: {__version__}")
    print()
    
    # Test client initialization
    print("Testing client initialization:")
    try:
        async_client = InfinityClient("test_token", "123456789")
        print(f"  ✅ InfinityClient: {async_client.bot_token[:4]}...{async_client.bot_token[-4:]}")
        
        sync_client = SyncInfinityClient("test_token", "123456789")
        print(f"  ✅ SyncInfinityClient: {sync_client.client.bot_token[:4]}...{sync_client.client.bot_token[-4:]}")
        
        # Test error class
        error = InfinityAPIError("Test error", 400)
        print(f"  ✅ InfinityAPIError: {error} (status: {error.status_code})")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    print()
    print("✅ All basic tests passed!")
    print()
    print("📚 Next steps:")
    print("  1. Get your API token from Infinity Bot List")
    print("  2. Use InfinityClient or SyncInfinityClient in your Discord bot")
    print("  3. Check out the examples/ directory for usage examples")
    print("  4. Visit spider.infinitybots.gg for API documentation")
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
