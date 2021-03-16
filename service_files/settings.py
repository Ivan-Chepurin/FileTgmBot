import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES_DIR = 'files'

TOKEN = "1075866482:AAGlS0Qp8SZlKX3ELezTR9cIg4ank58uy7k"

STATES = {
    'ban': 0,
    'input': 1,
    'registration': 2,
    'authorization': 3,
    'choice_actions': 4,
    'send_file': 5,
    'download_file': 6,
}
