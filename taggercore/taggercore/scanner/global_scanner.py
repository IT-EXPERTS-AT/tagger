#
# Copyright (c) 2020 it-eXperts IT-Dienstleistungs GmbH.
#
# This file is part of tagger
# (see TBD).
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

import skew

from taggercore.model import Resource
from taggercore.scanner import create_resource, sort_resources

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
GLOBAL_SERVICES = ["route53", "cloudfront", "iam"]


class GlobalScanner:
    @staticmethod
    def scan(resource_types_to_exclude: List[str]) -> List[Resource]:
        all_scanned_resources = []
        for service in GLOBAL_SERVICES:
            service_uri = "arn:aws:" + service + ":*:*:*/*"
            resources = skew.scan(service_uri)
            for resource in resources:
                if resource.resourcetype in resource_types_to_exclude:
                    continue
                else:
                    all_scanned_resources.append(create_resource(resource))
        logger.info("Scanning completed for global services")
        return sort_resources(all_scanned_resources)
