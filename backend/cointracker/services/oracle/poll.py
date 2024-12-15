from web3 import Web3
import json

ENDPOINT = 'https://ethereum-mainnet.core.chainstack.com/b4992d373edbb4026efb4639cfe88a76'

PRICE_FEEDS = {
    'BTC': '0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c',  # BTC/USD
    'ETH': '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419',  # ETH/USD
    'LINK': '0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c',  # LINK/USD
    'AAVE': '0x547a514d5e3769680Ce22B2361c10Ea13619e8a9', # AAVE/USD
    'USDC': '0xA2F78ab2355fe2f984D808B5CeE7FD0A93D5270E', # USDC/USD
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



def get_crypto_price(crypto_symbol):
    try:
        w3 = Web3(Web3.HTTPProvider(ENDPOINT))
        
        if crypto_symbol.upper() not in PRICE_FEEDS:
            raise ValueError(f"Price feed not available for {crypto_symbol}")
            
        price_feed_address = PRICE_FEEDS[crypto_symbol.upper()]
        
        contract = w3.eth.contract(address=price_feed_address, abi=AGGREGATOR_ABI)
        
        latest_data = contract.functions.latestRoundData().call()
        price = latest_data[1] / 1e8
        
        return price
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
