"""
Provides ORM model for the mailing facility of the Wefram.
"""

from .. import ds


class MailAccount(ds.Model):
    """
    Mail account model defining both data for sending & for receiving mail from
    the server.
    """

    id = ds.UUIDPrimaryKey()
    """ The ``id`` of the account with the ``uuid`` type. """

    name = ds.Column(ds.Caption(), nullable=False, default='')
    """ The human reabable name of the account (used in select for other logics). """

    snd_host = ds.Column(ds.String(), nullable=False, default='')
    """ The hostname of the SMTP server. """

    snd_port = ds.Column(ds.Integer(), nullable=False, default=0)
    """ Optional SMTP port number. """

    rcv_host = ds.Column(ds.String(), nullable=False, default='')
    """ The hostname of the IMAP/POP3 server. """

    rcv_port = ds.Column(ds.Integer(), nullable=False, default=0)
    """ Optional POP3/IMAP port. """

    use_imap = ds.Column(ds.Boolean(), nullable=False, default=True)
    """ Will'be used IMAP protocol if True, POP3 otherwise. """

    use_tls = ds.Column(ds.Boolean(), nullable=False, default=True)
    """ Will'be user TLS (encryption) if True. """

    username = ds.Column(ds.String(), nullable=False, default='')
    """ The username about to be used both for sending and receiving the mail. """

    password = ds.Column(ds.String(), nullable=False, default='')
    """ The corresponding user's password. """

    class Meta:
        order = ['name']
        exclude = ['password']
        findable = ['name', 'username', 'snd_host', 'rcv_host']

