#! coding: utf-8

from faker import Faker

fake = Faker()


def time_serie_name():
    return fake.word()
