from datadog_sync.utils.base_resource import BaseResource


RESOURCE_TYPE = "integration_aws"


class IntegrationAws(BaseResource):
    def __init__(self, ctx):
        super().__init__(ctx, RESOURCE_TYPE)
