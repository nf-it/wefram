import uuid
import hashlib
from .. import config


__all__ = [
    'random_token',
    'hash_password',
    'test_password'
]


def random_token(strong: bool = False) -> str:
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
    return hashlib.sha256(str(plain + config.AUTH['salt']).encode('utf-8')).hexdigest().lower()


def test_password(requested: str, hashed: str) -> bool:
    return hash_password(requested).lower() == hashed.lower()

