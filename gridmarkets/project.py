from __future__ import absolute_import
from builtins import str
from builtins import object
import datetime
import json
import os
from .watch_file import WatchFile


class Project(object):
    """Class to represent the project being submitted to Envoy service"""

    def __init__(self, project_folder, name='', **params):
        self.local_root = os.path.abspath(project_folder)
        self.name = name if name else os.path.split(self.local_root)[-1]
        self.remote_root = "/{0}".format(self.name)
        self.params = params if params else dict()
        self.timestamp = datetime.datetime.now()
        self.remote_output_folder_name = str(self.timestamp).replace(
            ' ', '_').replace(':', '-').replace('.', '_')
        self.remote_output_folder = "{0}/render_results/{1}".format(self.remote_root, self.remote_output_folder_name)
        self.jobs = list()
        self.files = list()
        self.watch_files = list()
        self.skip_upload = False 
        self.skip_auto_download = False

        # define default watch files
        download_path = os.path.join(self.local_root, 'gm_results')
        download_pattern = "{0}/.+".format(self.remote_output_folder)
        self.watch_files_default = WatchFile(download_pattern, download_path)

    def  _is_in_directory(self, path, parent_dir):
        return os.path.commonprefix([path, parent_dir]) == parent_dir

    def _rel_path(self, path, parent_dir):
        return os.path.relpath(path, os.path.dirname(parent_dir))

    def _add_folder(self, path):
        if not os.path.isabs(path):
            path = os.path.join(self.local_root, path)

        if os.path.isdir(path) and self._is_in_directory(path, self.local_root):
            for dir_name, _, dir_files in os.walk(path):
                for dir_file in dir_files:
                    src_file = os.path.join(dir_name, dir_file)
                    src_file = os.path.relpath(src_file, self.local_root)
                    src_file = src_file.replace("\\", "/")
                    self.files.append(src_file)

    def add_jobs(self, *jobs):
        for j in jobs:
            j.project = self

        self.jobs.extend(jobs)

    def add_files(self, *args):
        for f in args:
            if not os.path.isabs(f):
                f = os.path.join(self.local_root, f)

            if os.path.isfile(f) and self._is_in_directory(f, self.local_root):
                src_file = os.path.relpath(f, self.local_root)
                src_file = src_file.replace("\\", "/")
                self.files.append(src_file)

    def add_folders(self, *args):
        for folder in args:
            self._add_folder(folder)

    def add_watch_files(self, *watch_files):
        self.watch_files.extend(watch_files)

    def validate(self):
        return True

    @property
    def serialize(self):
        data = dict()
        data['project_request'] = dict()
        data['project_files'] = dict()
        data['watch_files'] = dict()

        data['project_request']['name'] = '{0} {1}'.format(
            self.name, self.timestamp.strftime("%Y-%b-%d %H:%M:%S %p"))

        data['project_request']['params'] = self.params
        data['project_request']['jobs'] = list()

        for j in self.jobs:
            data['project_request']['jobs'].append(j.serialize)

        data['project_files']['localRoot'] = self.local_root
        data['project_files']['remoteRoot'] = self.remote_root
        data['project_files']['files'] = list()

        for f in self.files:
            data['project_files']['files'].append(f)

        if self.skip_upload:
            data['skip_upload'] = self.skip_upload

        if not self.skip_auto_download:
            watch_files = list()
            watch_files.extend(self.watch_files)
            
            if not watch_files:
                watch_files.append(self.watch_files_default)

            for item in watch_files:
                data['watch_files'].update(item.serialize)

        return data

    @property
    def upload_serialize(self):
        data = dict()
        data['upload'] = list()
        item = dict()
        item['localRoot'] = self.local_root
        item['remoteRoot'] = self.remote_root
        item['files'] = list()

        for f in self.files:
            item['files'].append(f)

        data['upload'].append(item)

        return data
