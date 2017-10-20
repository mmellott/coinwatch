#!/usr/bin/env python3

from pony.orm import Database, PrimaryKey, Required, Optional, Set

db = Database(provider='sqlite', filename='coinwatch.sqlite', create_db=True)

class Coin(db.Entity):
    id = PrimaryKey(str) # e.g., bitcoin
    name = Required(str) # e.g., Bitcoin
    symbol = Required(str) # e.g., BTC
    rank = Required(int) # e.g., 1
    price_usd = Required(float) # e.g., 573.137
    price_btc = Required(float) # e.g., 1.0

    assets = Set('Asset')

class Portfolio(db.Entity):
    pushover_token = PrimaryKey(str)

    assets = Set('Asset')
    notifications = Set('Notification')

    def value_usd(self):
        return sum(map(lambda x: x.value_usd(), self.assets))

    def drift(self):
        f = lambda x: abs(x.value_usd()/self.value_usd() - x.weight)
        return sum(map(f, self.assets))

class Asset(db.Entity):
    coin = Required('Coin')
    portfolio = Required('Portfolio')
    amount = Required(float)
    weight = Required(float)

    PrimaryKey(coin, portfolio)

    def value_usd(self):
        return self.coin.price_usd * self.amount

class Notification(db.Entity):
    name = Required(str)
    portfolio = Required('Portfolio')
    last_noted = Optional(float)
    threshold = Required(float)

    PrimaryKey(name, portfolio)

db.generate_mapping(create_tables=True)
