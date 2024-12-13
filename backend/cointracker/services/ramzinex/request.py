import requests
import json

def get_coin_id(coin_name):
    with open("currencies.json", "r") as fr:
        currencies_json = json.load(fr)
        for currency in currencies_json:
            if currency['name'] == coin_name:  # Use == for value comparison
                return str(currency['id'])
        raise ValueError(f"Coin '{coin_name}' not found in currencies.json")  # Raise a proper exception

def make_request(coin_name):
    try:
        response = requests.get(
            "https://publicapi.ramzinex.com/exchange/api/v1.0/exchange/currencies/" + get_coin_id(coin_name))
        response.raise_for_status()
        data = response.json()
        print(data)
    except requests.exceptions.RequestException as e:
        raise f"{e}"
    except ValueError as e:
        raise f"{e}"

make_request("bitcoin")
