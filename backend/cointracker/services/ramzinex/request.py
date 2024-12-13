import requests
import json


def get_coin_id(coin_name):
    with open("currencies.json", "r") as fr:
        currencies_json = json.load(fr)
        for (id, name) in currencies_json:
            if name == coin_name:
                return id
        raise "Coin not found in currencies.json"


def make_request(coin_name):
    try
    response = requests.get(
        "https://publicapi.ramzinex.com/exchange/api/v1.0/exchange/currencies/" + get_coin_id())
    response.raise_for_status()
    data = response.json()
    except RequestException as e:
        raise f"{e}"
    except ValueError as e:
        raise f"{e}"
