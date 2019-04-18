import django
django.setup()

import os
import sys
import shutil
from http.server import HTTPServer

from iwatchdog.config import LOCK_DIR, PROBLEM_DIR
from iwatchdog.handler import InvokerWatchdog


def init():
    if os.path.exists(LOCK_DIR):
        shutil.rmtree(LOCK_DIR)
    os.makedirs(LOCK_DIR)

    for problem in os.listdir(PROBLEM_DIR):
        with open(os.path.join(LOCK_DIR, problem + '.lock'), 'w') as f:
            pass


def listen(port):
    server = HTTPServer(('127.0.0.1', port), InvokerWatchdog)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()


def main():
    if len(sys.argv) <= 1:
        print("Usage: {} <port>".format(sys.argv[0]))
        return
    port = int(sys.argv[1])
    init()
    listen(port)
