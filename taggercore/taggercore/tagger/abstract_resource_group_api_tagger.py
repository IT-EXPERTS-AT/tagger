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
import logging, time
from abc import ABC, abstractmethod
from typing import List, Dict, Any

import boto3
from botocore.client import BaseClient

from taggercore.config import get_config, TaggercoreConfigError
from taggercore.model import Tag, Resource, TaggingResult

MAX_ALLOWED_LENGTH_OF_ARN_LIST = 20

logger = logging.getLogger(__name__)


class AbstractResourceGroupApiTagger(ABC):
    """ Groups shared functionality for tagging classes using the Resource Groups Tagging API

    Subclasses need to implement their own init_client method

    """

    def __init__(self, tags: List[Tag], resources_to_tag: List[Resource]):
        self._tags = tags
        self._resources_to_tag = resources_to_tag
        self._failed_arns = {}
        self._session = self.init_session()

    @property
    @abstractmethod
    def tags(self):
        pass

    @property
    @abstractmethod
    def resources_to_tag(self):
        pass

    @property
    def arns(self):
        return list(map(lambda resource: resource.arn, self._resources_to_tag))

    @abstractmethod
    def init_client(self) -> BaseClient:
        pass

    @property
    def session(self):
        return self._session

    def tag_all(self) -> List[TaggingResult]:
        self._reset_previous_result()
        client = self.init_client()
        arns_in_sublists = self.split_into_sublist()
        tagging_results = []
        for sublist in arns_in_sublists:
            tagging_results.append(self._tag_arn_list(client, sublist))

        return tagging_results

    def _reset_previous_result(self):
        self._failed_arns = {}

    def split_into_sublist(self) -> List[List[str]]:
        arns = self.arns
        if len(arns) < MAX_ALLOWED_LENGTH_OF_ARN_LIST:
            return [arns]
        else:
            return [
                arns[x : x + MAX_ALLOWED_LENGTH_OF_ARN_LIST]
                for x in range(0, len(arns), MAX_ALLOWED_LENGTH_OF_ARN_LIST)
            ]

    def _tag_arn_list(self, client: BaseClient, arn_list: List[str]):
        tags = {tag.key: tag.value for tag in self.tags}
        try:
            response = client.tag_resources(ResourceARNList=arn_list, Tags=tags)
        except client.exceptions.InvalidParameterException as parameter_exception:
            logger.error(parameter_exception)
            failed_arn = self._extract_arn_from_error(parameter_exception)
            logger.error(
                "Resource {} is not taggable via ResourceTaggingAPI, filtering and retrying without it".format(
                    failed_arn
                )
            )
            arn_list.remove(failed_arn)
            self._failed_arns[failed_arn] = parameter_exception
            self._tag_arn_list(client, arn_list)
            response = {}
        except client.exceptions.ThrottledException as throttled_exception:
            logger.error(throttled_exception)
            time.sleep(30)
            self._tag_arn_list(client, arn_list)
            response = {}
        except Exception as e:
            logger.error(e)
            response = {}
        return self._transform_response_to_tagging_result(arn_list, response)

    def _extract_arn_from_error(self, exception) -> str:
        return str(exception).split("operation: ")[1].split(" is")[0]

    def _transform_response_to_tagging_result(
        self, list_of_arns: List[str], response: Dict[Any, Any]
    ) -> TaggingResult:
        self._failed_arns = {
            **self._failed_arns,
            **self._extract_failed_resource_arns(
                response.get("FailedResourcesMap", {})
            ),
        }
        successful_arns = list(
            filter(lambda arn: arn not in self._failed_arns, list_of_arns)
        )
        return TaggingResult(successful_arns, self._failed_arns)

    @staticmethod
    def _extract_failed_resource_arns(
        failed_resources: Dict[str, Dict[str, Any]]
    ) -> Dict[str, str]:
        if failed_resources.keys():
            logger.error("Failed: {}".format(failed_resources))
        return {
            arn: error_dict.get("ErrorMessage", "")
            for arn, error_dict in failed_resources.items()
        }

    def init_session(self):
        credentials = get_config().credentials
        if credentials:
            return boto3.Session(**credentials)
        else:
            profile = get_config().profile
            if not profile:
                raise TaggercoreConfigError(
                    "No profile and no credentials found. Please set the configuration before using tagging classes"
                )
            return boto3.Session(profile_name=profile)
