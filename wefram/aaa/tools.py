"""
Provides a set of AAA tools, primaryly used by the authorization, authentication and accounting.
"""

import uuid
import hashlib
from .. import config


__all__ = [
    'random_token',
    'hash_password',
    'test_password'
]


def random_token(strong: bool = False) -> str:
    """ Generate the random unique token. If the `strong` argument is set to True - then
    the resulting token length will be twice longer.
    """

    return ''.join([
        uuid.uuid4().hex,
        uuid.uuid4().hex,
        uuid.uuid4().hex,
        uuid.uuid4().hex
    ]) if strong else ''.join([
        uuid.uuid4().hex,
        uuid.uuid4().hex
    ])


def hash_password(plain: str) -> str:
    """ Hashes the given plain text password, returning its SHA2-256 hash. """

    return hashlib.sha256(str(plain + config.AUTH['salt']).encode('utf-8')).hexdigest().lower()


def test_password(requested: str, hashed: str) -> bool:
    """ Compares the requested plain text password with the hash, returning
    `True` if the plain password corresponds to the given hash. """

    return hash_password(requested).lower() == hashed.lower()

