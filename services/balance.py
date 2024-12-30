from decimal import Decimal
import requests
import time
import random
from typing import Dict, Tuple, Optional, Callable
from dataclasses import dataclass

# Cache configuration
CACHE_TTL = 60  # seconds

@dataclass
class CoinConfig:
    """Configuration for each supported coin's balance fetching"""

    symbol: str
    fetch_balance: Callable[[str], Decimal]
    description: str = ""


# Single unified cache for all coins
_balance_cache: Dict[Tuple[str, str], Tuple[Decimal, float]] = (
    {}
)  # {(coin_symbol, address): (balance, timestamp)}


def _fetch_btc_balance(address: str) -> Decimal:
    """Fetch BTC balance from blockchain.info"""
    try:
        response = requests.get(
            f"https://blockchain.info/q/addressbalance/{address}", timeout=10
        )
        response.raise_for_status()
        return Decimal(str(int(response.text) / 100000000))
    except Exception as e:
        print(f"Error fetching BTC balance: {e}")
        return Decimal("0")


def _fetch_eth_balance(address: str) -> Decimal:
    """Fetch ETH balance from ethplorer.io"""
    try:
        api_key = "freekey"
        url = f"https://api.ethplorer.io/getAddressInfo/{address}?apiKey={api_key}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return Decimal(str(data.get("ETH", {}).get("balance", 0)))
    except Exception as e:
        print(f"Error fetching ETH balance: {e}")
        return Decimal("0")


def _fetch_mock_balance(min_val: float, max_val: float) -> Callable[[str], Decimal]:
    """Create a mock balance fetcher with specified range"""

    def _fetch(address: str) -> Decimal:
        return Decimal(str(round(random.uniform(min_val, max_val), 8)))

    return _fetch


# Configuration for supported coins
SUPPORTED_COINS = {
    "BTC": CoinConfig(
        symbol="BTC",
        fetch_balance=_fetch_btc_balance,
        description="Bitcoin balance from blockchain.info",
    ),
    "ETH": CoinConfig(
        symbol="ETH",
        fetch_balance=_fetch_eth_balance,
        description="Ethereum balance from ethplorer.io",
    ),
    "SOL": CoinConfig(
        symbol="SOL",
        fetch_balance=_fetch_mock_balance(0, 50),
        description="Solana balance (mocked 0-100)",
    ),
    "BNB": CoinConfig(
        symbol="BNB",
        fetch_balance=_fetch_mock_balance(0, 20),
        description="BNB balance (mocked 0-50)",
    ),
}


def get_address_balance(coin_symbol: str, address: str) -> Decimal:
    """
    Generic function to get balance for any supported coin

    Args:
        coin_symbol: Upper case symbol of the coin (e.g., "BTC", "ETH")
        address: Wallet address to check

    Returns:
        Decimal: Balance of the address
    """
    # Validate coin is supported
    coin_config = SUPPORTED_COINS.get(coin_symbol.upper())
    if not coin_config:
        print(f"Unsupported coin: {coin_symbol}")
        return Decimal("0")

    current_time = time.time()
    cache_key = (coin_symbol.upper(), address)

    if cache_key in _balance_cache:
        balance, timestamp = _balance_cache[cache_key]
        if current_time - timestamp < CACHE_TTL:
            return balance

    try:
        balance = coin_config.fetch_balance(address)
        _balance_cache[cache_key] = (balance, current_time)
        return balance
    except Exception as e:
        print(f"Error fetching {coin_symbol} balance: {e}")
        return Decimal("0")