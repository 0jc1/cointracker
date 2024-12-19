import requests 
from decimal import Decimal


def get_address_balance(addr):
    r = requests.get('https://blockchain.info/q/addressbalance/'+addr)
    b = 0
    if not r.status_code==200:
        print('Error',r.status_code)

    return round(int(r.text)/100000000,8)
