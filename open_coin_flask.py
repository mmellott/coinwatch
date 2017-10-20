#!/usr/bin/env python3

from gevent.wsgi import WSGIServer
from coin_flask import app

http_server = WSGIServer(('', 80), app)
http_server.serve_forever()
