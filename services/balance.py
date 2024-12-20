import requests
from decimal import Decimal


def get_address_balance_btc(addr):
    b = 0.0
    try:
        r = requests.get("https://blockchain.info/q/addressbalance/" + addr)
        if not r.status_code == 200:
            print("Error", r.status_code)
            return b

        return round(int(r.text) / 100000000, 8)
    except Exception as e:
        print(f"Request error: {e}")
        return b


def get_address_balance_eth(addr):
    api_key = "freekey"
    url = f"https://api.ethplorer.io/getAddressInfo/{addr}?apiKey={api_key}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract ETH balance
        eth_data = data.get("ETH", {})
        eth_balance = eth_data.get("balance", 0)

        return Decimal(str(eth_balance))
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return Decimal("0.00")
    except (ValueError, KeyError) as e:
        print(f"Data processing error: {e}")
        return Decimal("0.00")
