"""
Example: Asynchronous usage of Pyfinity

This example shows how to use the async InfinityClient to post bot statistics
to the Infinity Bot List API.
"""

import asyncio
from pyfinity import InfinityClient, InfinityAPIError


async def main():
    """Example of async usage."""

    # Initialize the client with your bot token and bot ID
    # Get these from your bot page on Infinity Bot List
    client = InfinityClient(bot_token="your_bot_token_here", bot_id="your_bot_id_here")

    try:
        # Use the client as an async context manager
        async with client:
            # Post bot statistics
            server_count = 150  # Number of servers your bot is in
            user_count = 5000  # Number of users your bot serves
            shard_count = 2  # Number of shards (optional)
            shard_list = [0, 1]  # List of shard IDs (optional)

            print("Posting bot statistics...")
            response = await client.post_bot_stats(
                server_count=server_count,
                user_count=user_count,
                shard_count=shard_count,
                shard_list=shard_list,
            )
            print(f"✅ Statistics posted successfully: {response}")

            # Get bot information
            print("\nFetching bot information...")
            bot_info = await client.get_bot_info()
            print(f"📊 Bot info: {bot_info}")

            # Get user information (optional)
            print("\nFetching user information...")
            user_info = await client.get_user_info("123456789012345678")
            print(f"👤 User info: {user_info}")

    except InfinityAPIError as e:
        print(f"❌ API Error: {e}")
        if e.status_code:
            print(f"Status code: {e.status_code}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
