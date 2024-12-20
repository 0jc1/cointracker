from web3 import Web3
import json
from os import getenv
from dotenv import load_dotenv
from django.utils.timezone import now
from django.utils import timezone
import threading
import time
from portfolios.models import CryptoPrice 
from decimal import Decimal

load_dotenv()

ENDPOINT = getenv('CHAINLINK_ENDPOINT')

PRICE_FEEDS = {
    'BTC': '0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c',  # BTC/USD
    'ETH': '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419',  # ETH/USD
    'LINK': '0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c',  # LINK/USD
    'BNB': '0x14e613AC84a31f709eadbdF89C6CC390fDc9540A'
   # 'LTC':  '0x6AF09DF7563C363B5763b9102712EbeD3b9e859B'
    #'AAVE': '0x547a514d5e3769680Ce22B2361c10Ea13619e8a9', # AAVE/USD
    #'USDC': '0xA2F78ab2355fe2f984D808B5CeE7FD0A93D5270E', # USDC/USD
}

# Chainlink Price Feed ABI (Application Binary Interface)
AGGREGATOR_ABI = json.loads('''[
    {
        "inputs": [],
        "name": "latestRoundData",
        "outputs": [
            {"internalType": "uint80", "name": "roundId", "type": "uint80"},
            {"internalType": "int256", "name": "answer", "type": "int256"},
            {"internalType": "uint256", "name": "startedAt", "type": "uint256"},
            {"internalType": "uint256", "name": "updatedAt", "type": "uint256"},
            {"internalType": "uint80", "name": "answeredInRound", "type": "uint80"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]''')

# Global in-memory cache and timestamp
_cached_prices = None
_last_update_time = None
_CACHE_EXPIRY = 60  # in seconds, how often to refresh the data

def get_crypto_price(crypto_symbol):
    try:
        w3 = Web3(Web3.HTTPProvider(ENDPOINT))
        
        if crypto_symbol.upper() not in PRICE_FEEDS:
            raise ValueError(f"Price feed not available for {crypto_symbol}")
            
        price_feed_address = PRICE_FEEDS[crypto_symbol.upper()]
        
        contract = w3.eth.contract(address=price_feed_address, abi=AGGREGATOR_ABI)
        
        latest_data = contract.functions.latestRoundData().call()
        price = latest_data[1] / 1e8
        
        CryptoPrice.objects.create(
            ticker=crypto_symbol.upper(),
            currency='USD',
            price=Decimal(str(price))
        )        
        return price
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    
def get_latest_price(ticker):
    latest_price = CryptoPrice.objects.filter(ticker=ticker).order_by('-timestamp').first()
    if latest_price:
        return latest_price.price
    return Decimal('0.00')


def get_price_24h_ago(ticker):
    time_24h_ago = timezone.now() - timezone.timedelta(hours=24)
    price_24h_ago = CryptoPrice.objects.filter(
        ticker__iexact=ticker, 
        timestamp__lte=time_24h_ago
    ).order_by('-timestamp').first()
    
    if price_24h_ago:
        return price_24h_ago.price
    else:
        oldest_price = CryptoPrice.objects.filter(
            ticker__iexact=ticker
        ).order_by('timestamp').first()
        if oldest_price:
            return oldest_price.price
        else:
            return Decimal('0.00')
    
def get_crypto_prices():
    prices = {}
    w3 = Web3(Web3.HTTPProvider(ENDPOINT))
    
    for symbol, address in PRICE_FEEDS.items():
        try:
            price = get_crypto_price(symbol)

            prices[symbol] = price
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            prices[symbol] = None

    return prices

def _update_prices_in_background():
    global _cached_prices, _last_update_time
    try:
        prices = get_crypto_prices()  # Returns dict like {'BTC': 30000, 'ETH': 2000, ...}
        _cached_prices = prices
        _last_update_time = time.time()
    except Exception as e:
        print(f"Error updating prices: {e}")

def get_cached_or_refresh_prices():
    global _cached_prices, _last_update_time

    # If no cached data or data is stale
    if _cached_prices is None or (_last_update_time is not None and (time.time() - _last_update_time) > _CACHE_EXPIRY):
        print("getting updated prices")
        thread = threading.Thread(target=_update_prices_in_background)
        thread.start()
        if _cached_prices is None:
            return {}
        return _cached_prices
    else:
        return _cached_prices
