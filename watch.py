#!/usr/bin/python3

import pushover

import sys
import http.client, urllib.parse
import json
import locale
import time
from datetime import datetime
import random

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

def pushover_notify(msg):
    config = json.load(open('pushover.json'))
    paul_ryan = pushover.Pushover(config['token'], config['user'])
    paul_ryan.notify(msg)

def get_conversion(pair):
    conn = http.client.HTTPSConnection('api.cryptonator.com:443')
    conn.request('POST', '/api/ticker/{}-{}'.format(pair[0], pair[1]))
    ticker = json.loads(conn.getresponse().read().decode('utf-8'))
    return float(ticker['ticker']['price'])

if __name__ == '__main__':
    last_noted_price = None
    last_noted_total = 0
    last_noted_drift = 100

    while True:
        print(datetime.today())
        config = json.load(open('coins.json'))

        price = {}
        usd_val = {}
        for coin in config:
            price[coin] = get_conversion((coin, 'USD'))
            usd_val[coin] = config[coin] * price[coin]

        if last_noted_price is None:
            last_noted_price = {}
            for coin in config:
                last_noted_price[coin] = price[coin]

        total = sum(usd_val.values())
        mean_val = total / max(len(config), 1)

        drift = 0
        for coin in config:
            drift += abs(usd_val[coin] - mean_val) / sum(usd_val.values())

        msg = 'Drift %{:.2f}\n'.format(drift * 100.0)
        msg += '{}\n'.format(locale.currency(total))
        price_strs = []
        for coin in price:
            last = last_noted_price[coin]
            percent_delta = 100 * (price[coin] - last) / last
            price_strs.append('{}\t${:.0f} ({:.0f}%)'.format(coin, price[coin],
                    percent_delta))
        msg += '\n'.join(sorted(price_strs))

        print(msg)
        if abs(last_noted_total - total) >= 5000 or \
                abs(last_noted_drift - drift) >= .05:
            pushover_notify(msg)
            print('Notified!')

            for coin in price:
                last_noted_price[coin] = price[coin]
            last_noted_total = total
            last_noted_drift = drift
        print()

        time.sleep(60*10 + random.randint(-10, 10))
