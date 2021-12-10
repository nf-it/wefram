from typing import *
import os
import random
from .. import ds, aaa, logger, config
from ..models import User, Role
from .routines import *


__all__ = [
    'build'
]


DEMO_AVATARS: List[str] = os.listdir(os.path.join(config.CORE_ROOT, 'assets', 'dist', 'demo', 'avatars'))


async def make_random_user() -> User:
    first_name: str
    middle_name: str
    last_name: str
    gender: str
    first_name, middle_name, last_name, gender = make_random_fullname()

    avatar: Optional[str] = f"/system/demo/avatars/{random.choice(DEMO_AVATARS)}" \
        if random.random() > .3 \
        else None
    login: str = ('.'.join([last_name, ''.join([s[0] for s in (first_name, middle_name) if s])])).lower()

    return User(
        login=login,
        secret=aaa.hash_password(make_random_password()),
        locked=False,
        available=True,
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        avatar=avatar
    )


async def make_random_users(qty: int) -> None:
    logins: List[str] = []
    users: List[User] = []

    n: int = 0
    while n < qty:
        user: User = await make_random_user()
        if user.login in logins:
            continue
        n += 1
        logins.append(user.login)
        users.append(user)
        logger.info(
            f"created new demo user: {user.display_name} [{user.login}]"
        )

    [ds.db.add(o) for o in users]


async def build() -> None:
    await make_random_users(100)

