from .logerr import console
from .logerr import generate_failure_dict
import random
import string
from sys import exit as kill

def generate_token(size=50, lowercase=False, uppercase=True, numbers=True):
    if not uppercase and not lowercase and not numbers:
        uppercase=True
        numbers=True

    pool = ""
    if uppercase:
        pool = pool + string.ascii_uppercase
    if lowercase:
        pool = pool + string.ascii_lowercase
    if numbers:
        pool = pool + string.digits

    if size <= 3:
        size = 5

    size = size - 1
    token = ""
    token = token.join(random.choice(pool) for _ in range(size))
    token = "R" + token
    return token

def token_deserialize(headers):
    try:
        bearer_header = headers['Authorization']
    except KeyError as error:
        return headers, True

    token = bearer_header.replace('Bearer ', '')
    return token.strip(), False
