#!/usr/bin/env python3

from model import Coin, Portfolio, Asset, Notification
import pushover

import pony.orm as pny
import requests
import sys

@pny.db_session
def update_coins():
    url = 'https://api.coinmarketcap.com/v1/ticker/'
    r = requests.get(url).json()
    for coin_dict in r:
        coin_dict_partial = { 'id': coin_dict['id'],
                'name': coin_dict['name'],
                'symbol': coin_dict['symbol'],
                'rank': coin_dict['rank'],
                'price_usd': coin_dict['price_usd'],
                'price_btc': coin_dict['price_btc'] }

        try:
            coin = Coin[coin_dict_partial['id']]
            coin.set(**coin_dict_partial)
        except:
            coin = Coin(**coin_dict_partial)

@pny.db_session
def send_notifications(pushover_token_app):
    for notification in Notification.select():
        if notification.check():
            msg = notification.generate()
            print(msg)

            if pushover_token_app is not None:
                pushover.Pushover(pushover_token_app,
                        notification.portfolio.pushover_token).notify(str(msg))

if __name__ == '__main__':
    update_coins()

    try:
        pushover_token_app = sys.argv[1]
    except IndexError:
        pushover_token_app = None

    send_notifications(pushover_token_app)
