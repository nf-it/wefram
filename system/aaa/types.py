from typing import *
import datetime


__all__ = [
    'IPermissions',
    'IJwtToken',
    'ISessionUser',
    'ISession',
    'ICachedSession',
    'ISessionUserResponse',
    'IAuthorizationResponse',
]


IPermissions = List[str]


class IJwtToken(TypedDict):
    user: str
    sess: str
    iat: datetime.datetime
    exp: datetime.datetime
    sub: str
    aud: str


class ISessionUser(TypedDict):
    id: str
    login: str
    first_name: str
    middle_name: str
    last_name: str
    display_name: str
    full_name: str
    locale: Optional[str]
    timezone: Optional[str]


class ISession(TypedDict):
    user: ISessionUser
    permissions: List[str]


class ICachedSession(ISession):
    token: str
    start_timestamp: str
    touch_timestamp: str


class ISessionUserResponse(TypedDict):
    id: str
    login: str
    firstName: str
    middleName: str
    lastName: str
    fullName: str
    displayName: str
    locale: Optional[str]
    timezone: Optional[str]


class IAuthorizationResponse(TypedDict):
    token: str
    refreshToken: str
    user: ISessionUserResponse
    expire: str
    permissions: IPermissions

