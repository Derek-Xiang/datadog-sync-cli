# Unless explicitly stated otherwise all files in this repository are licensed
# under the 3-clause BSD style license (see LICENSE).
# This product includes software developed at Datadog (https://www.datadoghq.com/).
# Copyright 2019 Datadog, Inc.
from typing import Optional

from requests.exceptions import HTTPError

from datadog_sync.utils.base_resource import BaseResourceModel, ResourceConfig
from datadog_sync.utils.resource_utils import ResourceConnectionError


class SyntheticsTests(BaseResourceModel):
    resource_type = "synthetics_tests"
    resource_config = ResourceConfig(
        resource_connections={"synthetics_private_locations": ["locations"]},
        base_path="/api/v1/synthetics/tests",
        excluded_attributes=[
            "root['deleted_at']",
            "root['org_id']",
            "root['public_id']",
            "root['monitor_id']",
            "root['modified_at']",
            "root['created_at']",
        ],
        excluded_attributes_re=[
            "updatedAt",
            "notify_audit",
            "locked",
            "include_tags",
            "new_host_delay",
            "notify_no_data",
        ],
    )
    # Additional SyntheticsTests specific attributes

    def get_resources(self, client) -> list:
        try:
            resp = client.get(self.resource_config.base_path).json()
        except HTTPError as e:
            self.config.logger.error("error importing synthetics_tests: %s", e)
            return []

        return resp["tests"]

    def import_resource(self, resource) -> None:
        self.resource_config.source_resources[f"{resource['public_id']}#{resource['monitor_id']}"] = resource

    def pre_resource_action_hook(self, resource) -> None:
        pass

    def pre_apply_hook(self, resources) -> Optional[list]:
        pass

    def create_resource(self, _id, resource) -> None:
        destination_client = self.config.destination_client

        try:
            resp = destination_client.post(self.resource_config.base_path, resource).json()
        except HTTPError as e:
            self.config.logger.error("error creating synthetics_test: %s", e.response.text)
            return
        self.resource_config.destination_resources[_id] = resp

    def update_resource(self, _id, resource) -> None:
        destination_client = self.config.destination_client

        try:
            resp = destination_client.put(
                self.resource_config.base_path + f"/{self.resource_config.destination_resources[_id]['public_id']}",
                resource,
            ).json()
        except HTTPError as e:
            self.config.logger.error("error creating synthetics_test: %s", e.response.text)
            return
        self.resource_config.destination_resources[_id] = resp

    def connect_id(self, key, r_obj, resource_to_connect) -> None:
        pl = self.config.resources["synthetics_private_locations"]
        resources = self.config.resources[resource_to_connect].resource_config.destination_resources

        for i, _id in enumerate(r_obj[key]):
            if pl.pl_id_regex.match(_id):
                if _id in resources:
                    r_obj[key][i] = resources[_id]["id"]
                else:
                    raise ResourceConnectionError(resource_to_connect, _id=_id)
