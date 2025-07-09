"""
Pyfinity - A Python wrapper around the Infinity Bot List API

This package provides a simple interface for Discord bot developers to interact
with the Infinity Bot List API (spider.infinitybots.gg) to post bot statistics
such as server count and user count.
"""

__version__ = "0.1.0"
__author__ = "CallMeAByte : Exa"
__email__ = ""
__description__ = (
    "A Python wrapper around the Infinity Bot List API for Discord bot developers"
)

from .client import InfinityClient, SyncInfinityClient, InfinityAPIError

__all__ = [
    "InfinityClient",
    "SyncInfinityClient",
    "InfinityAPIError",
    "__version__",
]


def hello_world() -> str:
    """
    A simple hello world function.

    Returns:
        str: A greeting message
    """
    return "Hello from Pyfinity! 🚀 A Python wrapper for Infinity Bot List API"


def main() -> None:
    """Main entry point for the application."""
    print(hello_world())
    print("Running on Python 3.13.5")
    print(f"Pyfinity version: {__version__}")
    print("Visit spider.infinitybots.gg for API documentation")


if __name__ == "__main__":
    main()
