"""
Pyfinity API Client - Main client for interacting with Infinity Bot List API
"""

import asyncio
import time
from typing import Optional, Dict, Any, List
from functools import wraps
import httpx


class InfinityAPIError(Exception):
    """Custom exception for Infinity API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator for automatic retry with exponential backoff for rate limits.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except InfinityAPIError as e:
                    if e.status_code == 429 and attempt < max_retries - 1:  # Rate limited
                        delay = base_delay * (2 ** attempt)
                        print(f"⏳ Rate limited (429). Retrying in {delay:.1f}s... (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(delay)
                        continue
                    raise
            return None
        return wrapper
    return decorator


class InfinityClient:
    """
    Main client for interacting with the Infinity Bot List API.

    This client allows Discord bot developers to post their bot statistics
    to the Infinity Bot List website with built-in rate limiting and hourly refresh.
    """

    def __init__(self, bot_token: str, bot_id: str, auto_refresh: bool = True):
        """
        Initialize the Infinity API client.

        Args:
            bot_token: The API token for your bot from Infinity Bot List
            bot_id: Your Discord bot's ID
            auto_refresh: Enable automatic hourly stats refresh (default: True)
        """
        self.bot_token = bot_token
        self.bot_id = bot_id
        self.base_url = "https://spider.infinitybots.gg/api"
        self.session: Optional[httpx.AsyncClient] = None
        self.auto_refresh = auto_refresh
        self._refresh_task: Optional[asyncio.Task] = None
        self._last_stats: Optional[Dict[str, Any]] = None
        self._last_refresh: float = 0
        self._rate_limit_remaining: int = 100
        self._rate_limit_reset: float = 0

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_session()

    async def start_session(self):
        """Start the HTTP session and auto-refresh task."""
        if self.session is None:
            self.session = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": self.bot_token,
                    "Content-Type": "application/json",
                    "User-Agent": "Pyfinity/0.1.0 (Python Bot API Wrapper; https://github.com/InfinityBotList/pyfinity)",
                    "Accept": "application/json",
                },
                timeout=30.0,
                verify=True,  # Ensure SSL verification
                follow_redirects=True,  # Follow redirects if needed
            )
        
        # Start hourly refresh task if auto_refresh is enabled
        if self.auto_refresh and self._refresh_task is None:
            self._refresh_task = asyncio.create_task(self._hourly_refresh_loop())

    async def close_session(self):
        """Close the HTTP session and stop auto-refresh task."""
        if self._refresh_task:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass
            self._refresh_task = None
            
        if self.session:
            await self.session.aclose()
            self.session = None

    async def _hourly_refresh_loop(self):
        """Background task to refresh stats every hour."""
        while True:
            try:
                await asyncio.sleep(3600)  # Wait 1 hour (3600 seconds)
                
                if self._last_stats:
                    print("🔄 Auto-refreshing bot statistics (hourly)")
                    await self.post_bot_stats(**self._last_stats)
                    print("✅ Stats auto-refreshed successfully")
                    
            except asyncio.CancelledError:
                print("⏹️ Auto-refresh task stopped")
                break
            except Exception as e:
                print(f"⚠️ Auto-refresh failed: {e}")
                # Continue the loop even if one refresh fails

    async def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API with rate limit detection.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data

        Returns:
            Response data as dictionary

        Raises:
            InfinityAPIError: If the request fails
        """
        if not self.session:
            await self.start_session()

        try:
            response = await self.session.request(
                method=method, url=endpoint, json=data
            )

            # Update rate limit info from headers
            self._rate_limit_remaining = int(response.headers.get("X-RateLimit-Remaining", 100))
            reset_timestamp = response.headers.get("X-RateLimit-Reset")
            if reset_timestamp:
                self._rate_limit_reset = float(reset_timestamp)

            # Log rate limit status
            if self._rate_limit_remaining < 10:
                print(f"⚠️ Rate limit warning: {self._rate_limit_remaining} requests remaining")

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Enhanced 429 handling
                retry_after = response.headers.get("Retry-After", "60")
                error_msg = f"Rate limited (429). Retry after {retry_after} seconds"
                print(f"🚫 {error_msg}")
                raise InfinityAPIError(error_msg, 429)
            else:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"]
                except (ValueError, KeyError):
                    error_msg = f"{error_msg}: {response.text}"

                raise InfinityAPIError(error_msg, response.status_code)

        except httpx.RequestError as e:
            raise InfinityAPIError(f"Request failed: {str(e)}")

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    async def post_bot_stats(
        self,
        server_count: int,
        user_count: Optional[int] = None,
        shard_count: Optional[int] = None,
        shard_list: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Post bot statistics to Infinity Bot List with automatic retry on 429.

        Args:
            server_count: Number of servers the bot is in
            user_count: Number of users the bot serves (optional)
            shard_count: Number of shards the bot is using (optional)
            shard_list: List of shard IDs the bot is using (optional)

        Returns:
            API response data

        Raises:
            InfinityAPIError: If the request fails
        """
        data = {
            "servers": server_count,
        }

        if user_count is not None:
            data["users"] = user_count

        if shard_count is not None:
            data["shards"] = shard_count

        if shard_list is not None:
            data["shard_list"] = shard_list

        # Store stats for auto-refresh
        self._last_stats = {
            "server_count": server_count,
            "user_count": user_count,
            "shard_count": shard_count,
            "shard_list": shard_list
        }
        self._last_refresh = time.time()

        return await self._make_request("POST", f"/bots/{self.bot_id}/stats", data=data)

    def get_rate_limit_info(self) -> Dict[str, Any]:
        """
        Get current rate limit information.

        Returns:
            Dictionary with rate limit info including remaining requests and reset time
        """
        return {
            "remaining": self._rate_limit_remaining,
            "reset_timestamp": self._rate_limit_reset,
            "reset_in_seconds": max(0, self._rate_limit_reset - time.time()) if self._rate_limit_reset else 0
        }

    def get_auto_refresh_info(self) -> Dict[str, Any]:
        """
        Get auto-refresh status information.

        Returns:
            Dictionary with auto-refresh info including last refresh time and next refresh
        """
        next_refresh = self._last_refresh + 3600 if self._last_refresh else 0
        return {
            "enabled": self.auto_refresh,
            "last_refresh": self._last_refresh,
            "next_refresh": next_refresh,
            "seconds_until_next": max(0, next_refresh - time.time()) if next_refresh else 0,
            "has_stats_cached": self._last_stats is not None
        }

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    async def post_shard_stats(
        self,
        shard_id: int,
        server_count: int,
        user_count: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Post statistics for a specific shard to Infinity Bot List with automatic retry.

        This is useful for bots that want to report per-shard statistics.

        Args:
            shard_id: The ID of the specific shard
            server_count: Number of servers this shard handles
            user_count: Number of users this shard serves (optional)

        Returns:
            API response data

        Raises:
            InfinityAPIError: If the request fails
        """
        data = {
            "shard_id": shard_id,
            "servers": server_count,
        }

        if user_count is not None:
            data["users"] = user_count

        return await self._make_request("POST", f"/bots/{self.bot_id}/shard/{shard_id}/stats", data=data)

    async def post_batch_shard_stats(
        self,
        shard_stats: Dict[int, Dict[str, int]]
    ) -> Dict[str, Any]:
        """
        Post statistics for multiple shards at once.

        This is useful for bots that want to efficiently update multiple shards
        with a single API call.

        Args:
            shard_stats: Dictionary mapping shard_id to stats dict
                        Example: {0: {"servers": 50, "users": 1000}, 1: {"servers": 45, "users": 900}}

        Returns:
            API response data

        Raises:
            InfinityAPIError: If the request fails
        """
        data = {
            "shard_stats": shard_stats
        }

        return await self._make_request("POST", f"/bots/{self.bot_id}/stats/batch", data=data)

    async def get_bot_info(self) -> Dict[str, Any]:
        """
        Get information about the bot from Infinity Bot List.

        Returns:
            Bot information from the API

        Raises:
            InfinityAPIError: If the request fails
        """
        return await self._make_request("GET", f"/bots/{self.bot_id}")

    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get information about a user from Infinity Bot List.

        Args:
            user_id: Discord user ID

        Returns:
            User information from the API

        Raises:
            InfinityAPIError: If the request fails
        """
        return await self._make_request("GET", f"/users/{user_id}")

    async def get_shard_info(self, shard_id: int) -> Dict[str, Any]:
        """
        Get information about a specific shard from Infinity Bot List.

        Args:
            shard_id: The ID of the shard to get information for

        Returns:
            Shard information from the API

        Raises:
            InfinityAPIError: If the request fails
        """
        return await self._make_request("GET", f"/bots/{self.bot_id}/shard/{shard_id}")

    async def get_all_shard_info(self) -> Dict[str, Any]:
        """
        Get information about all shards for this bot.

        Returns:
            All shard information from the API

        Raises:
            InfinityAPIError: If the request fails
        """
        return await self._make_request("GET", f"/bots/{self.bot_id}/shards")

    def calculate_shard_stats(self, total_servers: int, total_users: int, shards: List[int]) -> Dict[int, Dict[str, int]]:
        """
        Calculate estimated statistics per shard.

        This is a utility method that helps estimate how servers and users
        are distributed across shards. Useful for bots that want to report
        per-shard statistics but don't track them separately.

        Args:
            total_servers: Total number of servers across all shards
            total_users: Total number of users across all shards
            shards: List of shard IDs

        Returns:
            Dictionary mapping shard_id to estimated stats

        Example:
            stats = client.calculate_shard_stats(1000, 50000, [0, 1, 2, 3])
            # Returns: {0: {"servers": 250, "users": 12500}, 1: {"servers": 250, "users": 12500}, ...}
        """
        if not shards:
            return {}

        shard_count = len(shards)
        servers_per_shard = total_servers // shard_count
        users_per_shard = total_users // shard_count

        # Handle remainder distribution
        server_remainder = total_servers % shard_count
        user_remainder = total_users % shard_count

        shard_stats = {}
        for i, shard_id in enumerate(shards):
            # Distribute remainder across first few shards
            extra_servers = 1 if i < server_remainder else 0
            extra_users = 1 if i < user_remainder else 0

            shard_stats[shard_id] = {
                "servers": servers_per_shard + extra_servers,
                "users": users_per_shard + extra_users
            }

        return shard_stats

    def analyze_shard_distribution(self, shard_stats: Dict[int, Dict[str, int]]) -> Dict[str, Any]:
        """
        Analyze shard distribution and provide insights.

        Args:
            shard_stats: Dictionary mapping shard_id to stats dict

        Returns:
            Dictionary containing analysis results

        Example:
            analysis = client.analyze_shard_distribution({
                0: {"servers": 100, "users": 2000},
                1: {"servers": 80, "users": 1500},
                2: {"servers": 120, "users": 2500}
            })
        """
        if not shard_stats:
            return {"error": "No shard statistics provided"}

        shards = list(shard_stats.keys())
        server_counts = [stats.get("servers", 0) for stats in shard_stats.values()]
        user_counts = [stats.get("users", 0) for stats in shard_stats.values()]

        total_servers = sum(server_counts)
        total_users = sum(user_counts)
        shard_count = len(shards)

        # Calculate averages
        avg_servers = total_servers / shard_count if shard_count > 0 else 0
        avg_users = total_users / shard_count if shard_count > 0 else 0

        # Find min/max
        min_servers = min(server_counts) if server_counts else 0
        max_servers = max(server_counts) if server_counts else 0
        min_users = min(user_counts) if user_counts else 0
        max_users = max(user_counts) if user_counts else 0

        # Calculate load balance ratio (lower is better balanced)
        server_balance = (max_servers - min_servers) / avg_servers if avg_servers > 0 else 0
        user_balance = (max_users - min_users) / avg_users if avg_users > 0 else 0

        # Find most/least loaded shards
        most_loaded_shard = shards[server_counts.index(max_servers)] if server_counts else None
        least_loaded_shard = shards[server_counts.index(min_servers)] if server_counts else None

        return {
            "summary": {
                "total_shards": shard_count,
                "total_servers": total_servers,
                "total_users": total_users,
                "avg_servers_per_shard": round(avg_servers, 2),
                "avg_users_per_shard": round(avg_users, 2)
            },
            "distribution": {
                "min_servers": min_servers,
                "max_servers": max_servers,
                "min_users": min_users,
                "max_users": max_users,
                "server_balance_ratio": round(server_balance, 3),
                "user_balance_ratio": round(user_balance, 3)
            },
            "insights": {
                "most_loaded_shard": most_loaded_shard,
                "least_loaded_shard": least_loaded_shard,
                "is_well_balanced": server_balance < 0.2 and user_balance < 0.2,
                "balance_recommendation": "Well balanced" if server_balance < 0.2 else "Consider rebalancing shards"
            }
        }

    def generate_shard_report(self, shard_stats: Dict[int, Dict[str, int]]) -> str:
        """
        Generate a human-readable shard statistics report.

        Args:
            shard_stats: Dictionary mapping shard_id to stats dict

        Returns:
            Formatted report string
        """
        if not shard_stats:
            return "No shard statistics available"

        analysis = self.analyze_shard_distribution(shard_stats)
        
        report = []
        report.append("📊 SHARD STATISTICS REPORT")
        report.append("=" * 40)
        
        # Summary
        summary = analysis["summary"]
        report.append(f"🎯 Total Shards: {summary['total_shards']}")
        report.append(f"🏢 Total Servers: {summary['total_servers']:,}")
        report.append(f"👥 Total Users: {summary['total_users']:,}")
        report.append(f"📈 Avg Servers/Shard: {summary['avg_servers_per_shard']}")
        report.append(f"📈 Avg Users/Shard: {summary['avg_users_per_shard']:,}")
        report.append("")
        
        # Distribution
        dist = analysis["distribution"]
        report.append("📊 DISTRIBUTION")
        report.append("-" * 20)
        report.append(f"🔻 Min Servers: {dist['min_servers']}")
        report.append(f"🔺 Max Servers: {dist['max_servers']}")
        report.append(f"🔻 Min Users: {dist['min_users']:,}")
        report.append(f"🔺 Max Users: {dist['max_users']:,}")
        report.append("")
        
        # Insights
        insights = analysis["insights"]
        report.append("💡 INSIGHTS")
        report.append("-" * 20)
        report.append(f"🏆 Most Loaded Shard: {insights['most_loaded_shard']}")
        report.append(f"💤 Least Loaded Shard: {insights['least_loaded_shard']}")
        report.append(f"⚖️ Balance Status: {insights['balance_recommendation']}")
        report.append("")
        
        # Per-shard breakdown
        report.append("📋 PER-SHARD BREAKDOWN")
        report.append("-" * 20)
        for shard_id, stats in sorted(shard_stats.items()):
            servers = stats.get("servers", 0)
            users = stats.get("users", 0)
            report.append(f"Shard {shard_id}: {servers:,} servers, {users:,} users")
        
        return "\n".join(report)

class SyncInfinityClient:
    """
    Synchronous wrapper for the Infinity API client.

    This provides a synchronous interface for developers who prefer
    not to use async/await.
    """

    def __init__(self, bot_token: str, bot_id: str):
        """
        Initialize the synchronous Infinity API client.

        Args:
            bot_token: The API token for your bot from Infinity Bot List
            bot_id: Your Discord bot's ID
        """
        self.client = InfinityClient(bot_token, bot_id)

    def _run_async(self, coro):
        """Run an async coroutine synchronously."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(coro)

    def post_bot_stats(
        self,
        server_count: int,
        user_count: Optional[int] = None,
        shard_count: Optional[int] = None,
        shard_list: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Post bot statistics to Infinity Bot List (synchronous).

        Args:
            server_count: Number of servers the bot is in
            user_count: Number of users the bot serves (optional)
            shard_count: Number of shards the bot is using (optional)
            shard_list: List of shard IDs the bot is using (optional)

        Returns:
            API response data
        """

        async def _post():
            async with self.client as client:
                return await client.post_bot_stats(
                    server_count, user_count, shard_count, shard_list
                )

        return self._run_async(_post())

    def post_shard_stats(
        self,
        shard_id: int,
        server_count: int,
        user_count: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Post statistics for a specific shard to Infinity Bot List (synchronous).

        Args:
            shard_id: The ID of the specific shard
            server_count: Number of servers this shard handles
            user_count: Number of users this shard serves (optional)

        Returns:
            API response data
        """

        async def _post():
            async with self.client as client:
                return await client.post_shard_stats(
                    shard_id, server_count, user_count
                )

        return self._run_async(_post())

    def post_batch_shard_stats(
        self,
        shard_stats: Dict[int, Dict[str, int]]
    ) -> Dict[str, Any]:
        """
        Post statistics for multiple shards at once (synchronous).

        This is useful for bots that want to efficiently update multiple shards
        with a single API call.

        Args:
            shard_stats: Dictionary mapping shard_id to stats dict
                        Example: {0: {"servers": 50, "users": 1000}, 1: {"servers": 45, "users": 900}}

        Returns:
            API response data
        """

        async def _post():
            async with self.client as client:
                return await client.post_batch_shard_stats(shard_stats)

        return self._run_async(_post())

    def get_bot_info(self) -> Dict[str, Any]:
        """
        Get information about the bot from Infinity Bot List (synchronous).

        Returns:
            Bot information from the API
        """

        async def _get():
            async with self.client as client:
                return await client.get_bot_info()

        return self._run_async(_get())

    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get information about a user from Infinity Bot List (synchronous).

        Args:
            user_id: Discord user ID

        Returns:
            User information from the API
        """

        async def _get():
            async with self.client as client:
                return await client.get_user_info(user_id)

        return self._run_async(_get())

    def get_shard_info(self, shard_id: int) -> Dict[str, Any]:
        """
        Get information about a specific shard from Infinity Bot List (synchronous).

        Args:
            shard_id: The ID of the shard to get information for

        Returns:
            Shard information from the API
        """

        async def _get():
            async with self.client as client:
                return await client.get_shard_info(shard_id)

        return self._run_async(_get())

    def get_all_shard_info(self) -> Dict[str, Any]:
        """
        Get information about all shards for this bot (synchronous).

        Returns:
            All shard information from the API
        """

        async def _get():
            async with self.client as client:
                return await client.get_all_shard_info()

        return self._run_async(_get())

    def analyze_shard_distribution(self, shard_stats: Dict[int, Dict[str, int]]) -> Dict[str, Any]:
        """
        Analyze shard distribution and provide insights (synchronous).

        Args:
            shard_stats: Dictionary mapping shard_id to stats dict

        Returns:
            Dictionary containing analysis results
        """

        return self.client.analyze_shard_distribution(shard_stats)

    def generate_shard_report(self, shard_stats: Dict[int, Dict[str, int]]) -> str:
        """
        Generate a human-readable shard statistics report (synchronous).

        Args:
            shard_stats: Dictionary mapping shard_id to stats dict

        Returns:
            Formatted report string
        """

        return self.client.generate_shard_report(shard_stats)

    def calculate_shard_stats(self, total_servers: int, total_users: int, shards: List[int]) -> Dict[int, Dict[str, int]]:
        """
        Calculate estimated statistics per shard (synchronous).

        Args:
            total_servers: Total number of servers across all shards
            total_users: Total number of users across all shards
            shards: List of shard IDs

        Returns:
            Dictionary mapping shard_id to estimated stats
        """

        return self.client.calculate_shard_stats(total_servers, total_users, shards)
