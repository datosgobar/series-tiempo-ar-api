#!/usr/bin/env python
import string, random, argparse

parser = argparse.ArgumentParser()
parser.add_argument('file', type=argparse.FileType('w'), help='Where save secret key')

try:
    from django.core.management import utils
    key = utils.get_random_secret_key()
except:
    from django.utils.crypto import get_random_string

    def get_random_secret_key():
        """
        Return a 50 character random string usable as a SECRET_KEY setting value.
        """
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        return get_random_string(50, chars)

    key = get_random_secret_key()

args = parser.parse_args()

with args.file as a_file:
    a_file.write(key)
