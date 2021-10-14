""" Plain authorization using only password stored in the users database. """

from typing import *
from ...models import User
from ..tools import *


__version__ = 1


async def authenticate(username: str, password: str) -> Optional[User]:
    if password == '':
        return None
    user: Optional[User] = await User.first(login=username)
    if user is None:
        return None
    if user.secret == '':
        return None
    if not test_password(password, user.secret):
        return None
    return user

