#!/usr/bin/env python3

import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

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
    id = PrimaryKey(int, auto=True)
    portfolio = Required('Portfolio')

class NotificationThreshold(Notification):
    threshold = Required(float)

class NotificationChange(NotificationThreshold):
    last_noted = Optional(float)

    def changed(self, parameter):
        if self.last_noted is not None:
            return abs(parameter - self.last_noted) > self.threshold
        else:
            return True

class NotificationThresholdDrift(NotificationThreshold):
    long_name = "Drift Threshold"

    def check(self):
        return self.portfolio.drift() > self.threshold

    def generate(self):
        return "Drift is {:.2f}%".format(self.portfolio.drift())

class NotificationChangeDrift(NotificationChange):
    long_name = "Drift Change"

    def check(self):
        return self.changed(self.portfolio.drift())

    def generate(self):
        drift = self.portfolio.drift()
        msg = "Drift is {:.2f}%".format(drift)
        self.last_noted = drift
        return msg

class NotificationThresholdValueUsd(NotificationThreshold):
    long_name = "Value USD Threshold"

    def check(self):
        return self.portfolio.value_usd() > self.threshold

    def generate(self):
        return "Value USD is {}".format(locale.currency(
                self.portfolio.value_usd()))

class NotificationChangeValueUsd(NotificationChange):
    long_name = "Value USD Change"

    def check(self):
        return self.changed(self.portfolio.value_usd())

    def generate(self):
        value_usd = self.portfolio.value_usd()
        msg = "Value USD is {}".format(locale.currency(value_usd))
        self.last_noted = value_usd
        return msg

db.generate_mapping(create_tables=True)
