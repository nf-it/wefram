from .. import api
from ..const.mail import PERMISSION
from ... import models


@api.register
class MailAccount(api.ModelAPI):
    model = models.MailAccount
    requires = PERMISSION

