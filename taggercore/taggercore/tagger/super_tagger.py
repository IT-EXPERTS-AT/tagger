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
from functools import reduce
from typing import List, Tuple

from taggercore.model import Resource, Tag, TaggingResult
from taggercore.tagger import GlobalTagger, IamTagger, RegionTagger, ServiceTagger

logger = logging.getLogger(__name__)
# Provides mapping between resource service and tagger class
SERVICE_TAGGER = {"iam": IamTagger}

GLOBAL_RES_TYPE_NOT_TAGGABLE = ["policy"]
REG_RES_TYPE_NOT_TAGGABLE = [
    "autoScalingGroup",
    "launchConfiguration",
    "subscription",
    "subnet-group",
]
# Cloudformation stack and Elasticbeanstalk environment currently not supported
REG_RES_TYPE_NOT_SUPPORTED = ["stack", "environment"]


class SuperTagger:
    """ Delegates tagging to service, global and region tagger objects

    SuperTagger takes care of splitting resources into sublist which are then passed on to the fitting tagger class

    """

    def __init__(self, resources: List[Resource], tags: List[Tag]):
        self._resources = resources
        self._tags = tags
        (
            service_tagger_res,
            regional_res,
            global_res,
        ) = self._split_resources_for_taggers(resources)
        self._service_taggers = self._init_service_taggers(service_tagger_res)
        self._region_taggers = self._init_region_taggers(regional_res)
        self._global_tagger = self._init_global_tagger(global_res)

    @staticmethod
    def _split_resources_for_taggers(
        resources: List[Resource],
    ) -> Tuple[List[Resource], List[Resource], List[Resource]]:
        service_tagger_res = []
        regional_res = []
        global_res = []
        for resource in resources:
            if resource.service in SERVICE_TAGGER.keys():
                service_tagger_res.append(resource)
            elif resource.region:
                regional_res.append(resource)
            else:
                global_res.append(resource)

        return service_tagger_res, regional_res, global_res

    def _init_service_taggers(self, resources: List[Resource]) -> List[ServiceTagger]:
        service_tagger_dict = {}
        for resource in resources:
            service_tagger_dict.setdefault(resource.service, []).append(resource)
        service_taggers = []
        for service, resources in service_tagger_dict.items():
            service_taggers.append(
                SERVICE_TAGGER.get(service)(tags=self._tags, resources=resources)
            )
        return service_taggers

    def _init_region_taggers(self, resources: List[Resource]) -> List[RegionTagger]:
        grouped_by_region = {}
        for resource in resources:
            grouped_by_region.setdefault(resource.region, []).append(resource)
        region_taggers = []
        for region, resources in grouped_by_region.items():
            region_taggers.append(RegionTagger(self._tags, resources, region))
        return region_taggers

    def _init_global_tagger(self, global_resources: List[Resource]) -> GlobalTagger:
        return GlobalTagger(self._tags, global_resources)

    @property
    def region_taggers(self):
        return self._region_taggers

    @property
    def service_taggers(self):
        return self._service_taggers

    @property
    def global_tagger(self):
        return self._global_tagger

    def tag_regions(self):
        region_results = []
        for tagger in self._region_taggers:
            region_results.append(tagger.tag_all())
        return self.__reduce_to_single_result(region_results)

    def tag_non_regional_resources(self):
        non_regional_result = []
        for tagger in self._service_taggers:
            non_regional_result.append(tagger.tag_resources())
        global_result = self._global_tagger.tag_all()
        non_regional_result.append(global_result)
        return self.__reduce_to_single_result(non_regional_result)

    def tag_all(self):
        regional_results = self.tag_regions()
        non_regional_results = self.tag_non_regional_resources()
        return TaggingResult(
            non_regional_results.successful_arns + regional_results.successful_arns,
            {**non_regional_results.failed_arns, **regional_results.failed_arns},
        )

    @staticmethod
    def __reduce_to_single_result(
        tagging_results: List[List[TaggingResult]],
    ) -> TaggingResult:
        if not tagging_results:
            return TaggingResult([], {})
        else:
            flatted_results = [
                tagging_result
                for sublist in tagging_results
                for tagging_result in sublist
            ]
            return reduce(
                lambda t1, t2: TaggingResult(
                    t1.successful_arns + t2.successful_arns,
                    {**t1.failed_arns, **t2.failed_arns},
                ),
                flatted_results,
            )
