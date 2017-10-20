from model import Coin, Portfolio, Asset, Notification

import pony.orm as pny

from flask import Flask, request, jsonify
app = Flask(__name__)

def get_portfolio(pushover_token):
    try:
        portfolio = Portfolio[pushover_token]
    except pny.ObjectNotFound:
        portfolio = Portfolio(pushover_token=pushover_token)

    return portfolio

@app.route('/')
def root():
    return """
        <iframe width="1120" height="630"
                src="https://www.youtube.com/embed/OU_5XaVULgw" frameborder="0"
                allowfullscreen>
        </iframe>
    """

def get_nullable_from_form(arg, arg_type=str):
    if arg in request.form:
        return arg_type(request.form[arg])
    else:
        return None

def json_error(msg):
    return jsonify({'error': msg})

@app.route('/<pushover_token>/assets', methods=['GET', 'POST'])
@pny.db_session
def assets(pushover_token):
    portfolio = get_portfolio(pushover_token)

    try:
        coin_id = get_nullable_from_form('coin_id')
        amount = get_nullable_from_form('amount', float)
        weight = get_nullable_from_form('weight', float)
    except ValueError as e:
        return json_error(str(e))

    if request.method == 'POST':
        if coin_id is None:
            return json_error('coin_id argument is required for method POST')

        asset = Asset.get(coin=coin_id, portfolio=pushover_token)
        if asset is None:
            if amount is None or weight is None:
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

    return jsonify([a.to_dict() for a in portfolio.assets])

@app.route('/<pushover_token>/notifications', methods=['GET', 'POST'])
@pny.db_session
def notifications(pushover_token):
    portfolio = get_portfolio(pushover_token)

    try:
        name = get_nullable_from_form('name')
        threshold = get_nullable_from_form('threshold', float)
    except ValueError as e:
        return json_error(str(e))

    if request.method == 'POST':
        if name is None:
            return json_error('name argument is required for method POST')

        if threshold is None:
            return json_error('threshold argument is required for method POST')

        notification = Notification.get(name=name, portfolio=pushover_token)
        if notification is None:
            Notification(name=name, portfolio=pushover_token,
                    threshold=threshold)
        else:
            notification.threshold = threshold

    return jsonify([n.to_dict() for n in portfolio.notifications])

@app.route('/<pushover_token>/report')
@pny.db_session
def report(pushover_token):
    portfolio = get_portfolio(pushover_token)
    return jsonify({'drift': portfolio.drift(),
            'total_value_usd': portfolio.value_usd()})
