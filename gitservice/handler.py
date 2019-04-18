import json
import os
import re
import subprocess

from http.server import BaseHTTPRequestHandler

from gitservice.config import REPO_DIR


def get_keys(username):
    r = re.compile(r'^{}(@\w+)?.pub$'.format(username))
    res = dict()
    for f in os.listdir(os.path.join(REPO_DIR, 'keydir')):
        if r.match(f):
            with open(os.path.join(REPO_DIR, 'keydir', f)) as fp:
                res[f] = fp.read()
    return res


def add_key(username, name, key):
    name = '{}@{}.pub'.format(username, name)
    with open(os.path.join(REPO_DIR, 'keydir', name), 'w') as f:
        f.write(key)
    subprocess.run(['git', 'add', './keydir/' + name], cwd=REPO_DIR)
    subprocess.run(['git', 'commit', '-m', 'AddKey ' + name], cwd=REPO_DIR)
    subprocess.run(['/home/git/bin/gitolite', 'push'], cwd=REPO_DIR)


def del_key(key):
    subprocess.run(['git', 'rm', '-f', './keydir/' + key], cwd=REPO_DIR)
    subprocess.run(['git', 'commit', '-m', 'DelKey ' + key], cwd=REPO_DIR)
    subprocess.run(['/home/git/bin/gitolite', 'push'], cwd=REPO_DIR)


class GitService(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/GetUserKeys':
            username = self.headers.get('username')
            if username:
                self.send_response(200)
                self.send_header('Content-Type', 'text/json')
                self.end_headers()
                self.wfile.write(json.dumps(get_keys(username)).encode())
                return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path == '/AddKey':
            username = self.headers.get('username')
            name = self.headers.get('name')
            key = self.headers.get('key')
            if username and name and key:
                add_key(username, name, key)
                self.send_response(204)
                self.end_headers()
                return

        if self.path == '/DelKey':
            key = self.headers.get('key')
            if key:
                del_key(key)
                self.send_response(204)
                self.end_headers()
                return

        self.send_response(404)
        self.end_headers()
