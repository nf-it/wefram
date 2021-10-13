
class HTTPResponseError(BaseException):
    pass


class NotFoundResponse(HTTPResponseError):
    pass


class AAAError(BaseException):
    pass


class NotAuthenticated(AAAError):
    pass


class AccessDenied(AAAError):
    pass


class AuthenticationFailed(AAAError):
    pass
