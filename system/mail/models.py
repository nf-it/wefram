from .. import ds


class MailAccount(ds.Model):
    """ Mail account model defining both data for sending & for receiving mail from
    the server.

    Attributes:
        id: The UUID ID of the account
        name: The human reabable name of the account (used in select for other logics)
        snd_host: The hostname of the SMTP server
        snd_port: Optional SMTP port number
        rcv_host: The hostname of the IMAP/POP3 server
        rcv_port: Optional POP3/IMAP port
        use_imap: Will'be used IMAP protocol if True, POP3 otherwise
        use_tls: Will'be user TLS (encryption) if True
        username: The username about to be used both for sending and receiving the mail
        password: The corresponding user's password

    """

    id = ds.UUIDPrimaryKey()
    name = ds.Column(ds.Caption(), nullable=False, default='')
    snd_host = ds.Column(ds.String(), nullable=False, default='')
    snd_port = ds.Column(ds.Integer(), nullable=False, default=0)
    rcv_host = ds.Column(ds.String(), nullable=False, default='')
    rcv_port = ds.Column(ds.Integer(), nullable=False, default=0)
    use_imap = ds.Column(ds.Boolean(), nullable=False, default=True)
    use_tls = ds.Column(ds.Boolean(), nullable=False, default=True)
    username = ds.Column(ds.String(), nullable=False, default='')
    password = ds.Column(ds.String(), nullable=False, default='')

    class Meta:
        order = ['name']
        exclude = ['password']
        findable = ['name', 'username', 'snd_host', 'rcv_host']

