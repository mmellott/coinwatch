#!/usr/bin/python3

import http.client
import urllib.parse

class Pushover(object):

    def __init__(self, token, user):
        self.token = token
        self.user = user

    def notify(self, msg):
        data = {
            'token': self.token,
            'user': self.user,
            'message': msg
        }

        conn = http.client.HTTPSConnection('api.pushover.net:443')
        conn.request('POST', '/1/messages.json', urllib.parse.urlencode(data),
                { 'Content-type': 'application/x-www-form-urlencoded' })
        return conn.getresponse().status

if __name__ == '__main__':
    import json

    config = json.load(open('pushover.json'))
    paul_ryan = Pushover(config['token'], config['user'])

    # notice, no trailing newline
    paul_ryan.notify('Obamacare is the law of the land...')
