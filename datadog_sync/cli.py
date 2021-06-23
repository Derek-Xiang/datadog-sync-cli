from click import pass_context, group, option

import datadog_sync.constants as constants
from datadog_sync.commands import ALL_COMMANDS
from datadog_sync.models import (
    Roles,
    Users,
    Monitors,
    Dashboards,
    DashboardLists,
    Downtimes,
    SyntheticsPrivateLocations,
    SyntheticsTests,
    SyntheticsGlobalVariables,
    ServiceLevelObjectives,
    LogsCustomPipelines,
    IntegrationsAWS,
)
from datadog_sync.utils.custom_client import CustomClient
from datadog_sync.utils.configuration import Configuration
from datadog_sync.utils.log import Log


@group()
@option(
    "--source-api-key",
    envvar=constants.DD_SOURCE_API_KEY,
    required=True,
    help="Datadog source organization API key.",
)
@option(
    "--source-app-key",
    envvar=constants.DD_SOURCE_APP_KEY,
    required=True,
    help="Datadog source organization APP key.",
)
@option(
    "--source-api-url",
    envvar=constants.DD_SOURCE_API_URL,
    required=False,
    help="Datadog source organization API url.",
)
@option(
    "--destination-api-key",
    envvar=constants.DD_DESTINATION_API_KEY,
    required=True,
    help="Datadog destination organization API key.",
)
@option(
    "--destination-app-key",
    envvar=constants.DD_DESTINATION_APP_KEY,
    required=True,
    help="Datadog destination organization APP key.",
)
@option(
    "--destination-api-url",
    envvar=constants.DD_DESTINATION_API_URL,
    required=False,
    help="Datadog destination organization API url.",
)
@option(
    "--http-client-retry-timeout",
    envvar=constants.DD_HTTP_CLIENT_RETRY_TIMEOUT,
    required=False,
    type=int,
    default=60,
    help="The HTTP request retry timeout period. Defaults to 60s",
)
@option(
    "--resources",
    required=False,
    help="Optional comma separated list of resource to import. All supported resources are imported by default.",
)
@option(
    "--verbose",
    "-v",
    required=False,
    is_flag=True,
    help="Enable verbose logging.",
)
@pass_context
def cli(ctx, **kwargs):
    """Initialize cli"""
    ctx.ensure_object(dict)

    # configure logger
    logger = Log(kwargs.get("verbose"))

    source_api_url = kwargs.get("source_api_url")
    destination_api_url = kwargs.get("destination_api_url")

    # Initialize the datadog API Clients
    source_auth = {
        "apiKeyAuth": kwargs.get("source_api_key"),
        "appKeyAuth": kwargs.get("source_app_key"),
    }
    destination_auth = {
        "apiKeyAuth": kwargs.get("destination_api_key"),
        "appKeyAuth": kwargs.get("destination_app_key"),
    }
    retry_timeout = kwargs.get("http_client_retry_timeout")

    source_client = CustomClient(source_api_url, source_auth, retry_timeout)
    destination_client = CustomClient(destination_api_url, destination_auth, retry_timeout)

    # Initialize Configuration
    config = Configuration(logger=logger, source_client=source_client, destination_client=destination_client)
    ctx.obj["config"] = config

    # Initialize resources
    config.resources = get_resources(config, kwargs.get("resources"))


def get_resources(cfg, resources_arg):
    """Returns list of Resources. Order of resources applied are based on the list returned"""
    resources = [
        # Roles(cfg),
        # Users(cfg),
        SyntheticsPrivateLocations(cfg),
        SyntheticsTests(cfg),
        SyntheticsGlobalVariables(cfg),
        Monitors(cfg),
        Downtimes(cfg),
        Dashboards(cfg),
        DashboardLists(cfg),
        ServiceLevelObjectives(cfg),
        LogsCustomPipelines(cfg),
        # IntegrationsAWS(cfg),
    ]

    if resources_arg:
        new_resources = []
        resources_arg_list = resources_arg.split(",")
        for resource in resources:
            if resource.resource_type in resources_arg_list:
                new_resources.append(resource)
        return new_resources

    return resources


# Register all click sub-commands
for command in ALL_COMMANDS:
    cli.add_command(command)
