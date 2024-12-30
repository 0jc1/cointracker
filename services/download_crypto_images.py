import os
import requests
import time
from typing import Dict

def get_cryptocompare_images() -> Dict[str, str]:
    try:
        response = requests.get('https://min-api.cryptocompare.com/data/all/coinlist')
        response.raise_for_status()
        data = response.json()
        
        coin_images = {}
        if data['Response'] == 'Success':
            for _, coin_data in data['Data'].items():
                symbol = coin_data['Symbol'].lower()
                if symbol in [c.lower() for c in COINS_TO_DOWNLOAD]:
                    image_url = f"https://www.cryptocompare.com{coin_data['ImageUrl']}"
                    coin_images[symbol] = image_url
        return coin_images
    except Exception as e:
        print(f'Failed to get coin list from CryptoCompare: {str(e)}')
        return {}

def download_image(coin_symbol, cryptocompare_images: Dict[str, str]):
    # Check if image already exists
    output_path = f'static/images/{coin_symbol.lower()}.png'
    if os.path.exists(output_path):
        print(f'Skipping {coin_symbol}.png - already exists')
        return

    # Try both lowercase and uppercase versions
    variations = [coin_symbol.lower(), coin_symbol.upper()]
    
    for variant in variations:
        urls = []
        
        # Add CryptoCompare URL if available
        if variant.lower() in cryptocompare_images:
            urls.append(cryptocompare_images[variant.lower()])
        
        # Add fallback URLs
        urls.extend([
            f'https://public-assets.ramzinex.com/public/currencies/logo/{variant}.png',
            f'https://cryptoicons.org/api/icon/{variant.lower()}/200'
        ])
        
        for url in urls:
            try:
                response = requests.get(url)
                response.raise_for_status()
                
                # Create images directory if it doesn't exist
                os.makedirs('static/images', exist_ok=True)
                
                # Save the image
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f'Successfully downloaded {variant}.png from {url}')
                return  # Exit after successful download
            except Exception as e:
                print(f'Failed to download {variant}.png from {url}: {str(e)}')

# List of coins to download
COINS_TO_DOWNLOAD = [
        'aave',   # Aave
        'ada',    # Cardano
        'apt',    # Aptos
        'atom',   # Cosmos
        'avax',   # Avalanche
        'bch',    # Bitcoin Cash
        'bgb',    # Bitget Token
        'bnb',    # Binance Coin
        'btc',    # Bitcoin
        'cake',   # PancakeSwap
        'comp',   # Compound
        'crv',    # Curve DAO
        'dai',    # Dai
        'dot',    # Polkadot
        'doge',   # Dogecoin
        'eth',    # Ethereum
        'fil',    # Filecoin
        'ftm',    # Fantom
        'grt',    # The Graph
        'hbar',   # Hedera
        'hype',   # Hyperliquid
        'icp',    # Internet Computer
        'inj',    # Injective
        'leo',    # LEO Token
        'link',   # Chainlink
        'ltc',    # Litecoin
        'matic',  # Polygon
        'mnt',    # Mantle
        'near',   # NEAR Protocol
        'op',     # Optimism
        'pepe',   # Pepe
        'rune',   # THORChain
        'sand',   # The Sandbox
        'shib',   # Shiba Inu
        'snx',    # Synthetix
        'sol',    # Solana
        'steth',  # Lido Staked Ether
        'sui',    # Sui
        'trx',    # TRON
        'uni',    # Uniswap
        'usdc',   # USD Coin
        'usds',   # USDS
        'usdt',   # Tether
        'vet',    # VeChain
        'wbtc',   # Wrapped Bitcoin
        'weth',   # WETH
        'xlm',    # Stellar
        'xmr',    # Monero
        'xrp',    # Ripple
        'zec',    # Zcash
    ]
    
def main():
    print("Fetching coin data from CryptoCompare...")
    cryptocompare_images = get_cryptocompare_images()
    print(f"Found {len(cryptocompare_images)} coins on CryptoCompare")
    
    for coin in COINS_TO_DOWNLOAD:
        download_image(coin, cryptocompare_images)

if __name__ == '__main__':
    main()
