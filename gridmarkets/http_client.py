from __future__ import absolute_import
from builtins import str
from builtins import object
import json
import textwrap
import threading
import requests
from . import errors


class HttpClient(object):
    def __init__(self, timeout=80, session=None, **kwargs):
        self._thread_local = threading.local()
        self._session = session
        self._timeout = timeout

    def request(self, method, url, headers=None, post_data=None):
        if getattr(self._thread_local, "session", None) is None:
            self._thread_local.session = self._session or requests.Session()

        try:
            response = self._thread_local.session.request(
                method,
                url,
                headers=headers,
                data=json.dumps(post_data) if post_data else None,
                timeout=self._timeout
            )
        except Exception as e:
            self._handle_request_error(e)
        else:
            return response

    def _handle_request_error(self, e):
        if isinstance(e, requests.exceptions.Timeout) or isinstance(
            e, requests.exceptions.ConnectionError
        ):
            msg = (
                "Unexpected error communicating with Envoy."
                "Please start Envoy and retry."
            )
            err = "%s: %s" % (type(e).__name__, str(e))
        # Catch remaining request exceptions
        elif isinstance(e, requests.exceptions.RequestException):
            msg = (
                "Unexpected error communicating with Envoy."
            )
            err = "%s: %s" % (type(e).__name__, str(e))
        else:
            msg = (
                "Unexpected error communicating with Envoy."
            )
            err = "A %s was raised" % (type(e).__name__,)
            if str(e):
                err += " with error message %s" % (str(e),)
            else:
                err += " with no error message"

        msg = textwrap.fill(msg) + "\n\n(Network error: %s)" % (err,)
        raise errors.APIError(msg)
