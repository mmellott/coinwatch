from model import Coin, Portfolio, Asset, Notification
import model

import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

import pony.orm as pny

from flask import Flask, request, render_template
app = Flask(__name__)

def get_portfolio(pushover_token):
    try:
        portfolio = Portfolio[pushover_token]
    except pny.ObjectNotFound:
        portfolio = Portfolio(pushover_token=pushover_token)

    return portfolio

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/<pushover_token>', methods=['GET', 'POST'])
@pny.db_session
def report(pushover_token):
    portfolio = get_portfolio(pushover_token)
    value_usd = locale.currency(portfolio.value_usd())
    drift = '{:.2f}%'.format(portfolio.drift())

    return render_template('report.html', pushover_token=pushover_token,
            value_usd=value_usd, drift=drift)

def get_nullable_from_form(arg, arg_type=str):
    try:
        # Accessing missing form argument will NOT generate KeyError, so check
        if arg in request.form:
            return arg_type(request.form[arg])
    except ValueError:
        pass
    return None

@app.route('/<pushover_token>/portfolio', methods=['GET', 'POST'])
@pny.db_session
def portfolio(pushover_token):
    portfolio = get_portfolio(pushover_token)

    # Update portfolio if method is POST
    if request.method == 'POST':
        coin_id = get_nullable_from_form('coin_id')

        if coin_id is not None:
            asset = Asset.get(coin=coin_id, portfolio=pushover_token)

            if 'delete' in request.form:
                asset.delete()
            else:
                amount = get_nullable_from_form('amount', float)
                weight = get_nullable_from_form('weight', float)

                if asset is None:
                    if amount is None:
                        amount = 0

                    if weight is None:
                        weight = 0

                    Asset(coin=coin_id, portfolio=pushover_token, amount=amount,
                            weight=weight)
                else:
                    if amount is not None:
                        asset.amount = amount

                    if weight is not None:
                        asset.weight = weight

    # Display portfolio
    assets = []
    for asset in Asset.select(
            lambda x: x.portfolio.pushover_token == pushover_token).order_by(
            lambda x: x.coin.name):
        asset_dict = asset.to_dict()
        asset_dict['coin'] = asset.coin.to_dict()
        assets.append(asset_dict)

    coins = [c.to_dict() for c in Coin.select()]

    return render_template('portfolio.html', pushover_token=pushover_token,
            assets=assets, coins=coins)

@app.route('/<pushover_token>/notifications', methods=['GET', 'POST'])
@pny.db_session
def notifications(pushover_token):
    portfolio = get_portfolio(pushover_token)

    notification_classes = {
            "drift_threshold": model.NotificationThresholdDrift,
            "drift_change": model.NotificationChangeDrift,
            "value_usd_threshold": model.NotificationThresholdValueUsd,
            "value_usd_change": model.NotificationChangeValueUsd }

    # Update notifications if method is POST
    if request.method == 'POST':
        if 'delete' in request.form:
            nid = get_nullable_from_form('nid')
            if nid is not None:
                Notification.get(id=nid).delete()
        else:
            ntype = get_nullable_from_form('ntype')
            threshold = get_nullable_from_form('threshold', float)

            if ntype is not None and threshold is not None:
                notification_classes[ntype](portfolio=portfolio,
                        threshold=threshold)

    # Display notifications
    ntypes = zip(notification_classes.keys(),
            [nclass.long_name for nclass in notification_classes.values()])

    nbriefs = []
    for notification in Notification.select(
            lambda x: x.portfolio.pushover_token == pushover_token).order_by(
            lambda x: x.id):
        nbriefs.append((notification.id, notification.long_name,
                notification.threshold))

    return render_template('notifications.html', pushover_token=pushover_token,
            ntypes=ntypes, nbriefs=nbriefs)
