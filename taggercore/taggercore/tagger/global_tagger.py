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

from taggercore.model import Tag, Resource
from taggercore.tagger import AbstractResourceGroupApiTagger

MAX_ALLOWED_LENGTH_OF_ARN_LIST = 20

logger = logging.getLogger(__name__)


class GlobalTagger(AbstractResourceGroupApiTagger):
    """ Tags resources which use the global endpoint in 'us-east-1'

    """

    def __init__(self, tags: List[Tag], resources_to_tag: List[Resource]):
        super().__init__(tags, resources_to_tag)

    @property
    def tags(self):
        return self._tags

    @property
    def resources_to_tag(self):
        return self._resources_to_tag

    def init_client(self) -> BaseClient:
        return self.session.client("resourcegroupstaggingapi", region_name="us-east-1")
