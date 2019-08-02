from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import object
import urllib.request, urllib.parse, urllib.error
from . import errors
from .http_client import HttpClient
from .resolver import Resolver

API_BASE = "http://localhost:8090"


class EnvoyClient(object):
    """Client to access Envoy Service API"""

    def __init__(self, email=None, access_key=None, url=None):
        from . import version
        self.version = version.VERSION

        if not url:
            url = API_BASE

        self.url = url
        self.email = email
        self.access_key = access_key
        self.http_client = HttpClient()

    def _get_products(self):
        url = '{0}/products'.format(self.url)

        try:
            resp = self.http_client.request('get', url)
        except Exception as e:
            raise errors.APIError(e)
        else:
            if resp.status_code == 200:
                return resp.json()

            if resp.status_code == 404:
                raise errors.InvalidRequestError(
                    "404: {0} not found".format(url))

    def validate_auth(self):
        url = '{0}/auth'.format(self.url)

        post_data = {
            "Username": self.email,
            "AccessKey": self.access_key
        }

        headers = {'content-type': 'application/json'}

        try:
            resp = self.http_client.request('post', url, headers, post_data)
        except Exception as e:
            raise errors.APIError(e)
        else:
            if resp.status_code == 200:
                return True

            if resp.status_code == 401:
                raise errors.AuthenticationError(resp.text, resp.status_code)

            if resp.status_code == 404:
                raise errors.InvalidRequestError(
                    "404: {0} not found".format(url))

    def validate_credits(self):
        url = '{0}/credits-info'.format(self.url)

        credits_available = 0.0

        try:
            resp = self.http_client.request('get', url)
        except Exception as e:
            raise errors.APIError(e)
        else:
            if resp.status_code == 200:
                content = resp.json()
                credits_available = content.get('credits_available')

            if resp.status_code == 404:
                raise errors.InvalidRequestError(
                    "404: {0} not found".format(url))

            if credits_available <= 0.0:
                raise errors.InsufficientCreditsError(
                    "Insufficient credits balance")

    def get_product_resolver(self, type_labels=None):
        self.validate_auth()

        products = self._get_products()
        return Resolver(products)

    def upload_project_files(self, project):
        self.validate_auth()
        self.validate_credits()

        if not project:
            raise ValueError("project parameter is None")

        url = "{0}/upload".format(self.url)
        headers = {'content-type': 'application/json'}

        import json
        print(json.dumps(project.upload_serialize))

        try:
            resp = self.http_client.request(
                'post', url, headers, project.upload_serialize)
        except Exception as e:
            raise errors.APIError(e)
        else:
            print(resp.json())
            if resp.status_code == 200 and resp.json()['ID'] == project.name:
                return project.name
            else:
                raise errors.APIError('status code:{0}, msg:{1}'.format(
                    resp.status_code, resp.text))

    def submit_project(self, project, skip_upload=False, skip_auto_download=False):
        self.validate_auth()
        self.validate_credits()

        if not project:
            raise ValueError("project parameter is None")

        url = '{0}/project-submit'.format(self.url)

        headers = {'content-type': 'application/json'}

        project.skip_upload = skip_upload
        project.skip_auto_download = skip_auto_download

        try:
            resp = self.http_client.request(
                'post', url, headers, project.serialize)
        except errors.InsufficientCreditsError as e:
            raise e
        except Exception as e:
            raise errors.APIError(str(e))
        else:
            if resp.status_code == 201:
                return project.name

            if resp.status_code == 404:
                raise errors.InvalidRequestError(
                    "404: {0} not found".format(url))

            if resp.status_code == 400:
                raise errors.InvalidRequestError(
                    "Invalid request", resp.json())

            if resp.status_code in (500, 503):
                raise errors.APIError("{0} {1}".format(
                    resp.status_code, resp.text))

    def get_project_status(self, name):
        self.validate_auth()

        url = '{0}/project-status/{1}'.format(self.url, urllib.parse.quote(name))

        try:
            resp = self.http_client.request('get', url)
        except Exception as e:
            raise errors.APIError(e)
        else:
            if resp.status_code == 200:
                return resp.json()

            if resp.status_code == 404:
                raise errors.InvalidRequestError(
                    "404: {0} not found".format(url))
