#!/usr/bin/python3

import json

from flask import Flask, request
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    page = ''

    try:
        config = json.load(open('/etc/coinwatch/coins.json'))
    except:
        config = {}

    if request.method == 'POST':
        if request.form['name'] in config and request.form['amount'] == '':
            del config[request.form['name']]
        else:
            config[request.form['name']] = float(request.form['amount'])
        json.dump(config, open('/etc/coinwatch/coins.json', 'w'))

    page += str(config)
    page += '''
        <form method="post">
            <p>Name <input type=text name=name>
            <p>Amount <input type=text name=amount>
            <p><input type=submit value=Update>
        </form>
    '''

    return page
