from builtins import str
from builtins import object
import uuid


class Job(object):
    """Class to represent the job part of project being submitted to Envoy service"""

    def __init__(self, name, app, app_version, operation, path, *plugins, **params):
        self.id = str(uuid.uuid4())
        self.name = name
        self.app = app
        self.app_version = app_version
        self.operation = operation
        self.path = path
        self.plugins = plugins if plugins else list()
        self.params = params if params else dict()
        self.dependencies = list()
        self.project = None

    def add_dependencies(self, *jobs):
        self.dependencies.extend(jobs)

    def validate(self):
        # TODO: implement functionality
        return True

    @property
    def serialize(self):
        job = dict()
        job['id'] = self.id
        job['name'] = self.name
        job['app'] = self.app
        job['app_version'] = self.app_version
        job['operation'] = self.operation
        job['path'] = self.path
        job['params'] = self.params
        job['params']['output_dir_name'] = self.project.remote_output_folder_name

        if 'output_upload' not in job['params']: 
            upload_pattern = '{0}/.+'.format(self.project.remote_output_folder)
            job['params']['output_upload'] = list()
            job['params']['output_upload'].append(upload_pattern)
            job['params']['output_upload'].append(upload_pattern.replace('/', '\\\\'))

        job['dependencies'] = [j.id for j in self.dependencies]

        if 'billing_meta' not in job['params']:
            job['params']['billing_meta'] = list()
            job['params']['billing_meta'].append(self.app)
            job['params']['billing_meta'].extend(self.plugins)

        return job
