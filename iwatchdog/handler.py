import os
import shutil
import subprocess
from fcntl import flock, LOCK_EX, LOCK_UN
from http.server import BaseHTTPRequestHandler

from compete.invoke import build_problem
from iwatchdog.config import LOCK_DIR, PROBLEM_DIR, REPO_URL


class Flock:
    def __init__(self, fd, kind = LOCK_EX):
        self.fd = fd
        self.kind = kind

    def __enter__(self):
        flock(self.fd, self.kind)

    def __exit__(self, exc_type, exc_val, exc_tb):
        flock(self.fd, LOCK_UN)


def update_problem(problem):
    lock_path = os.path.join(LOCK_DIR, problem + '.lock')
    if not os.path.exists(lock_path):
        subprocess.run(['git', 'clone', REPO_URL + problem], cwd=PROBLEM_DIR)
        with open(lock_path, 'w') as f:
            pass
    with open(lock_path) as f:
        with Flock(f):
            subprocess.run(['git', 'pull'], cwd=os.path.join(PROBLEM_DIR, problem))
            return build_problem(problem)


def del_problem(problem):
    lock_path = os.path.join(LOCK_DIR, problem + '.lock')
    if not os.path.exists(lock_path):
        return
    with open(lock_path) as f:
        with Flock(f):
            shutil.rmtree(os.path.join(PROBLEM_DIR, problem))
    os.unlink(lock_path)


class InvokerWatchdog(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/UpdateProblem':
            problem = self.headers.get('problem')
            if problem:
                res = update_problem(problem) or ''
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(res.encode())
                return

        if self.path == '/DelProblem':
            problem = self.headers.get('problem')
            if problem:
                del_problem(problem)
                self.send_response(204)
                self.end_headers()
                return

        self.send_response(404)
        self.end_headers()
