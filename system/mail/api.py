from .. import api
from . import models, const


@api.register
class MailAccount(api.ModelAPI):
    model = models.MailAccount
    requires = const.PERMISSION

