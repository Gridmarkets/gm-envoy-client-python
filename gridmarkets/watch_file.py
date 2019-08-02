from builtins import object


class WatchFile(object):
    def __init__(self, output_pattern, download_path):
        self.output_pattern = output_pattern
        self.download_path = download_path

    @property
    def serialize(self):
        return { self.output_pattern: self.download_path }
