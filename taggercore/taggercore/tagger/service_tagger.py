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
from abc import ABC, abstractmethod
from typing import List

import boto3

from taggercore.config import get_config, TaggercoreConfigError
from taggercore.model import Resource, Tag


class ServiceTagger(ABC):
    def __init__(self, resources: List[Resource], tags: List[Tag]):
        self._session = self.init_session()
        self._resources = resources
        self._tags = tags

    @property
    def session(self):
        return self._session

    @property
    def resources(self):
        return self._resources

    @abstractmethod
    def tag_resources(self):
        pass

    @staticmethod
    def init_session():
        """ Creates a boto3 Session which can then used by a subclass to create a boto3 Client
        :raises TaggercoreConfigError
        :return: a boto3 Session
        """
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
