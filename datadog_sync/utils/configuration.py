class Configuration(object):
    def __init__(self, logger=None, source_client=None, destination_client=None, resources=None, _filter=None):
        self.logger = logger
        self.source_client = source_client
        self.destination_client = destination_client
        self.resources = resources
        self.filter = _filter
