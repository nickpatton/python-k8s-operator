import requests

COIN_MARKET_API_URL = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids'


def get_value(coin, amount):
    coin_price = get_current_price(coin)
    value = coin_price * amount
    return value


def get_current_price(coin):
    """ return current price for given coin """
    current_price = requests.get(f"{COIN_MARKET_API_URL}={coin}").json()[
        0]['current_price']
    return current_price
