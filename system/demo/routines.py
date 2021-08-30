from typing import *
import random
import os
import datetime
import string


__all__ = [
    'namefile_path',
    'get_random_name',
    'make_random_fullname',
    'make_random_password',
    'make_random_birthday',
    'make_random_phonenum'
]


def namefile_path(nametype: str) -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets', nametype))


def get_random_name(filename: str) -> Optional[str]:
    result: Optional[str] = None
    while result is None:
        selected: float = random.random() * 90
        with open(filename) as name_file:
            for line in name_file:
                name, _, cummulative, _ = line.split()
                if float(cummulative) <= selected:
                    continue
                result = name.capitalize()
                break
    return result


def make_random_fullname() -> Tuple[str, str, str, str]:
    gender: str = random.choice(['male', 'female'])
    first_name: str = get_random_name(namefile_path('names.%s.lst' % gender))
    middle_name: str = '' \
        if bool(random.getrandbits(1)) \
        else get_random_name(namefile_path('names.%s.lst' % gender))
    last_name: str = get_random_name(namefile_path('surnames.lst'))
    return first_name, middle_name, last_name, gender


def make_random_password() -> str:
    return ''.join(random.sample(string.ascii_lowercase + string.ascii_uppercase + string.digits, 16))


def make_random_birthday() -> datetime.date:
    year: int = random.randrange(1960, 2000)
    month: int = random.randrange(1, 12)
    day: int = random.randrange(1, 28)
    return datetime.date(year, month, day)


def make_random_phonenum() -> str:
    return "+79" + "".join([str(random.randrange(0, 9)) for x in "111111111"])
