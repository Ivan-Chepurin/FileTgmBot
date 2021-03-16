import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES_DIR = 'files'

TOKEN = "<TOKEN>"

STATES = {
    'ban': 0,
    'input': 1,
    'registration': 2,
    'authorization': 3,
    'choice_actions': 4,
    'send_file': 5,
    'download_file': 6,
}
