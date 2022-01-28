"""
Provides API for the corresponding AAA ORM classes.
"""

from typing import *
from sqlalchemy.exc import IntegrityError
from ...api import register, ModelAPI
from ...aaa.tools import hash_password
from ...models import User, Role, SessionLog
from ...l10n import gettext
from ...ds import db
from ... import exceptions
from ..const.aaa import PERMISSION_ADMINUSERSROLES


@register
class User(ModelAPI):
    """
    The API class handling the systemUser model
    (:py:class:`~wefram.models.User` class).
    """

    model = User
    requires = PERMISSION_ADMINUSERSROLES

    @staticmethod
    async def encode_value(key: str, s: Any) -> Any:
        """ Handles the model's attribute's values assignment. Used to handle the
        password hashing and dropping mechanics.
        """

        if key == 'secret':
            if s is None:
                return ''
            return hash_password(s) if s else ...

        return s

    @staticmethod
    async def decode_value(key: str, s: Any) -> Any:
        """ Handles the model's attribute's value reading for the API response.
        Exclude the 'secret' column from being returning to the frontend.
        """

        if key == 'secret':
            return None

        return s

    async def delete(self, *keys: Union[str, int]) -> None:
        """ Removes the user(s) using the User's remove method. This is important
        to ovirride the default behaviour with the correspodning
        :py:meth:`~wefram.models.User.remove` method.
        """

        user_ids: List[str] = [self.key, ] if not keys else keys
        users: List[User] = await User.fetch(*user_ids)
        [(await user.remove()) for user in users]

        try:
            await db.flush()

        except IntegrityError:
            raise exceptions.DatabaseIntegrityError(
                gettext(
                    "Cannot delete user(s) due to the database conflict. Please try again.",
                    'wefram.aaa'
                )
            )


@register
class Role(ModelAPI):
    """
    The API class handling the systemRole model
    (:py:class:`~wefram.models.Role` class).
    """

    model = Role
    requires = PERMISSION_ADMINUSERSROLES


@register
class SessionLog(ModelAPI):
    """
    The API class handling the systemSessionLog model
    (:py:class:`~wefram.models.SessionLog` class). Take attention
    that this API class declines anything but reading - declining
    creating, deletion and updating.
    """

    model = SessionLog
    requires = PERMISSION_ADMINUSERSROLES
    allow_create = False
    allow_delete = False
    allow_update = False

