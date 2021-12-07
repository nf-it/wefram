

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


class ApiError(BaseException):
    def __init__(self, http_code: int = 400, details: str = "API error"):
        self.status_code: int = http_code
        self.details: str = details


class ObjectNotFoundError(BaseException):
    def __init__(self, details: str = None):
        from .l10n import gettext
        self.details: str = details or gettext("The specified object was not found", 'system.messages')


class DatabaseError(BaseException):
    def __init__(self, http_code: int = 400, details: str = "Database error"):
        self.status_code: int = http_code
        self.details: str = details


class DatabaseIntegrityError(DatabaseError):
    def __init__(self, details: str = None) -> None:
        from .l10n import gettext
        super().__init__(
            409,
            details or gettext(
                "Changes cannot be made because they conflict with other existing properties or objects.",
                'system.messages'
            )
        )

