import sys
import traceback


class GridMarketsError(Exception):
    """Utility class to define all API errors/exceptions"""

    def __init__(self, message=None, http_status=None):
        super(GridMarketsError, self).__init__(message)

        self._message = message
        self._http_status = http_status

        try:
            self.traceback = traceback.extract_tb(sys.exc_info()[2])

        except AttributeError:
            self.traceback = None
            pass

    def __str__(self):
        msg = self._message or '<empty message>'

        return msg

    @property
    def user_message(self):
        return self._message

    def __repr__(self):
        return "%s(message=%r, http_status=%r)" % (
            self.__class__.__name__,
            self._message,
            self._http_status)


class AuthenticationError(GridMarketsError):
    def __init__(self, message=None, http_status=None):
        super(AuthenticationError, self).__init__(message, http_status)


class APIError(GridMarketsError):
    pass


class InsufficientCreditsError(GridMarketsError):
    def __init__(self, message=None):
        super(InsufficientCreditsError, self).__init__(message)


class InvalidRequestError(GridMarketsError):
    def __init__(self, message=None, errors=None):
        super(InvalidRequestError, self).__init__(message)

        self.errors = errors if errors else dict()
