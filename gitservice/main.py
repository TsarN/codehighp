import sys
from http.server import HTTPServer

from gitservice.handler import GitService


def listen(port):
    server = HTTPServer(('127.0.0.1', port), GitService)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()


def main():
    if len(sys.argv) <= 1:
        print("Usage: {} <port>".format(sys.argv[0]))
        return
    port = int(sys.argv[1])
    listen(port)
