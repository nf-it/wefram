""" Active Directory authentication backend """

from typing import *
import socket
import ldap3
from ... import ds, logger, api
from ...models import User
from ...private.const.aaa import PERMISSION_ADMINUSERSROLES


__all__ = [
    'ActiveDirectoryDomain',
    'authenticate'
]


class ActiveDirectoryDomain(ds.Model):
    """ The single Active Directory domain specification, describing how to connect
    and authenticate within the given domain.
    """

    id = ds.UUIDPrimaryKey()
    enabled = ds.Column(ds.Boolean(), nullable=False, default=True)
    sort = ds.Column(ds.Integer(), nullable=False, default=0)
    name = ds.Column(ds.Caption(), nullable=False, default='')
    domain = ds.Column(ds.String(), nullable=False, default='')
    server = ds.Column(ds.String(), nullable=False, default='')

    class Meta:
        order = ['sort', 'name']

    @property
    def use_ssl(self) -> bool:
        """ Since last versions of Active Directory REQUIRES ssl to be used -
        always return 'True' to enable SSL support.
        """
        return True

    @property
    def server_port(self) -> int:
        """ Returns 389 default port for non-SSL connection and 636 for the
        SSL one.
        """
        return 389 if not self.use_ssl else 636

    async def try_on_active_directory(self, username: str, password: str) -> bool:
        """ Tries to authenticate the given FQ user@domain with given password
        within this very domain.

        :param username: (str) the username: login@domain
        :param password: (str) the entered by the user password about to be tried

        :returns: True if succeeded to authenticated, False otherwise.
        """

        host_to_resolve: str = self.server or self.domain
        try:
            server_ip: str = socket.gethostbyname(host_to_resolve)
            logger.debug(
                f"resolved Active Directory server '{host_to_resolve}' to IP: {server_ip}",
                'aaa backend [ad]'
            )
        except socket.gaierror:
            logger.error(
                f"failed to resolve Active Directory server name: {host_to_resolve}",
                'aaa backend [ad]'
            )
            return False
        logger.debug(
            f"trying to authenticate: {username}",
            'aaa backend [ad]'
        )
        server: ldap3.Server = ldap3.Server(
            host=server_ip,
            port=int(self.server_port),
            use_ssl=bool(self.use_ssl),
            get_info=ldap3.ALL,
            mode=ldap3.IP_SYSTEM_DEFAULT
        )
        conn: ldap3.Connection = ldap3.Connection(server, user=username, password=password)
        succeed: bool = conn.bind()
        conn.unbind()
        return succeed

    async def authenticate(self, username: str, password: str) -> bool:
        """ Tries to authenticate within this Active Directory domain, resuling with system
        User if succeed, or None otherwise.
        The username may be given both as FQ record (login@domain) and as login only, and
        the this domain will be appended automatically then.

        :param username: (str) the username
        :param password: (str) he entered by the user password about to be tried

        :returns: True if succeed, False otherwise
        """

        username: str
        domain: str
        username, domain = username.split('@', 1) if '@' in username else [username, self.domain]
        if domain != self.domain:
            return False
        login: str = '@'.join([username, domain])

        succeed: bool = await self.try_on_active_directory(login, password)
        if not succeed:
            logger.debug(
                f"credentials failed for '{login}'",
                'aaa backend [ad]'
            )
            return False
        logger.debug(
            f"successfully authenticated within '{self.domain}' for '{username}'",
            'aaa backend [ad]'
        )
        return True

    @classmethod
    async def all_enabled(cls) -> List['ActiveDirectoryDomain']:
        return await cls.all(enabled=True, order=['sort', 'name'])


@api.register
class ActiveDirectoryDomainAPI(api.ModelAPI):
    """ The API mapper for the ActiveDirectoryDomain ORM class. """

    name = 'ActiveDirectoryDomain'
    model = ActiveDirectoryDomain
    requires = PERMISSION_ADMINUSERSROLES


async def authenticate(username: str, password: str) -> Optional[User]:
    """ Using all enabled Active Directory domains in the order they sorted using
    the 'sort' attribute, try to authenticate the given user using given username
    and password. The first successful domain will be mapped to the corresponding
    system User.

    :param username: (str) the username, with or without domain part
    :param password: (str) the plain password beign given by the user

    :returns: User object if succeed, None otherwise
    """

    auth_username: str
    auth_domain: Optional[str]
    auth_username, auth_domain = username.split('@', 1) if '@' in username else [username, None]

    domains: List[ActiveDirectoryDomain] = await ActiveDirectoryDomain.all_enabled() \
        if not auth_domain \
        else await ActiveDirectoryDomain.all(domain=auth_domain, enabled=True)
    if not domains:

        return None

    conforming_logins: List[str] = [('@'.join([auth_username, d.domain])) for d in domains]
    conforming_users: Dict[str, User] = {
        u.login: u for u in
        await User.all(User.login.in_(conforming_logins), User.locked.is_(False))
    }
    if not conforming_users:
        return None

    for domain in domains:
        login: str = '@'.join([auth_username, domain.domain])
        user: Optional[User] = conforming_users.get(login, None)
        if user is None:
            continue
        if not await domain.authenticate(login, password):
            continue
        logger.debug(
            f"successfully authenticated user with id='{user.id}'",
            'aaa backend [ad]'
        )
        return user
    return None

