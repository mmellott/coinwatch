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
    for portfolio in Portfolio.select():
        notify = False
        drift = portfolio.drift()
        value_usd = portfolio.value_usd()

        report = {}
        for notification in portfolio.notifications:
            if notification.name == 'drift':
                current = drift
            elif notification.name == 'value_usd':
                current = value_usd
            else:
                print('Unsupported notification: {}'.format(notification.name))
                continue

            if notification.last_noted is None:
                difference = 0
                notify = True
            else:
                difference = current - notification.last_noted
                if abs(difference) >= notification.threshold:
                    notify = True
            report[notification.name] = (current, difference)

        if notify:
            for notification in portfolio.notifications:
                notification.last_noted = report[notification.name][0]

            pushover.Pushover(pushover_token_app,
                    portfolio.pushover_token).notify(str(report))

if __name__ == '__main__':
    update_coins()

    try:
        pushover_token_app = sys.argv[1]
        send_notifications(pushover_token_app)
    except KeyError:
        pass
