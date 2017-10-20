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

# currently broken
#if __name__ == '__main__':
#    import argparse, json
#
#    parser = argparse.ArgumentParser(description='Send Pushover notification.')
#    parser.add_argument('message', metavar='MSG', nargs=argparse.REMAINDER,
#            help='message to send')
#    args = parser.parse_args()
#
#    config = json.load(open('/root/coinwatch/pushover.json'))
#    paul_ryan = Pushover(config['token'], config['user'])
#
#    # notice, no trailing newline
#    #print(paul_ryan.notify(' '.join(args.message)))
