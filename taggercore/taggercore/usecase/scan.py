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
from typing import List, Dict

from taggercore.model import Resource
from taggercore.scanner import RegionScanner, GlobalScanner
from taggercore.tagger import (
    GLOBAL_RES_TYPE_NOT_TAGGABLE,
    REG_RES_TYPE_NOT_TAGGABLE,
    REG_RES_TYPE_NOT_SUPPORTED,
)


def scan_region(region: str) -> List[Resource]:
    """ Scans resources in given :param region

    :param region: AWS region code (https://docs.aws.amazon.com/general/latest/gr/rande.html for a full list)
    :return: resources found in given :param region
    """
    return RegionScanner(region).scan(
        REG_RES_TYPE_NOT_TAGGABLE + REG_RES_TYPE_NOT_SUPPORTED
    )


def scan_global() -> List[Resource]:
    return GlobalScanner().scan(GLOBAL_RES_TYPE_NOT_TAGGABLE)


def scan_region_and_global(region: str) -> Dict[str, List[Resource]]:
    return {region: scan_region(region), "global": scan_global()}
