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
from typing import List

from taggercore.tagger import REG_RES_TYPE_NOT_TAGGABLE, REG_RES_TYPE_NOT_SUPPORTED
from taggercore.tagger import GLOBAL_RES_TYPE_NOT_TAGGABLE
from taggercore.model import Tag, ResourceWithTagDiffs
from taggercore.scanner import RegionScanner, GlobalScanner


def scan_and_compare_resources(region: str, tags: List[Tag]) -> List[ResourceWithTagDiffs]:
    """ Compares resources tags to given :param tags and creates a list of diffs

    Scans resources in given :param region and global resources.
    Resources which are not taggable or currently not supported in the tagger classes are NOT returned.
    :param region: AWS region code (https://docs.aws.amazon.com/general/latest/gr/rande.html for a full list)
    :param tags: tags to compare the resource tags with

    :return resources with tag comparison result
    """
    resources = RegionScanner(region).scan(
        REG_RES_TYPE_NOT_SUPPORTED + REG_RES_TYPE_NOT_TAGGABLE
    ) + GlobalScanner().scan(GLOBAL_RES_TYPE_NOT_TAGGABLE)
    resources_with_diffs = []
    for resource in resources:
        resources_with_diffs.append(
            ResourceWithTagDiffs(resource, resource.compare_tags(tags))
        )
    return resources_with_diffs
