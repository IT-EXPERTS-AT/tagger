#
# Copyright (c) 2020 it-eXperts IT-Dienstleistungs GmbH.
#
# This file is part of tagger
# (see https://github.com/IT-EXPERTS-AT/tagger).
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
import logging
from typing import List

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from taggercore.model import TaggingResult, Tag, Resource
from taggercore.tagger import ServiceTagger

logger = logging.getLogger(__name__)


class IamTagger(ServiceTagger):
    """ Tags IAM roles and users.

    Roles and users cannot be tagged via Resource Groups Tagging API.
    They need to be tagged directly via the IAM client.

    """

    def tag_resources(self):
        return self._tag_all()

    def __init__(self, resources: List[Resource], tags: List[Tag]):
        super().__init__(resources, tags)
        self._users = [
            resource for resource in resources if resource.resource_type == "user"
        ]
        self._roles = [
            resource for resource in resources if resource.resource_type == "role"
        ]
        self._iam_client = self._init_client()

    def _tag_all(self) -> List[TaggingResult]:
        users_result = self._tag_users()
        roles_result = self._tag_roles()
        self._log_tagging_result(users_result, roles_result)
        return [users_result, roles_result]

    @staticmethod
    def _log_tagging_result(
        user_result: TaggingResult, roles_result: TaggingResult
    ) -> None:
        logger.info(
            "Tagged {} users and {} roles successfully".format(
                len(user_result.successful_arns), len(roles_result.successful_arns)
            )
        )
        logger.info(
            "Failed to tag {} users and {} roles".format(
                len(user_result.failed_arns), len(roles_result.failed_arns)
            )
        )

    def _tag_users(self) -> TaggingResult:
        tagging_result = TaggingResult([], {})
        for resource in self._users:
            try:
                self._iam_client.tag_user(
                    UserName=resource.kwargs.get("name"), Tags=self._extract_tags()
                )
                tagging_result.successful_arns.append(resource.arn)
            except ClientError as error:
                tagging_result.failed_arns[resource.arn] = error.response["Error"][
                    "Message"
                ]
        return tagging_result

    def _tag_roles(self) -> TaggingResult:
        tagging_result = TaggingResult([], {})
        for resource in self._roles:
            try:
                self._iam_client.tag_role(
                    RoleName=resource.kwargs.get("name"), Tags=self._extract_tags()
                )
                tagging_result.successful_arns.append(resource.arn)
            except ClientError as error:
                tagging_result.failed_arns[resource.arn] = error.response["Error"][
                    "Message"
                ]
        return tagging_result

    def _extract_tags(self):
        return [{"Key": tag.key, "Value": tag.value} for tag in self._tags]

    def _init_client(self) -> BaseClient:
        return self.session.client("iam")
