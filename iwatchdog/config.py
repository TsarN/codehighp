import os

BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROBLEM_DIR = os.path.join(DATA_DIR, 'problems')
LOCK_DIR = '/tmp/codehighp_iwatchdog'

REPO_URL = 'git@git.tsarn.website:problems/'
