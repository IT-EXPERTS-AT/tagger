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

from .resource import Resource
from .tag_diff_type import TagDiffType
from .tag_diff import TagDiff


class ResourceWithTagDiffs(dict):
    def __init__(self, resource: Resource, tag_diffs: List[TagDiff]) -> None:
        self._resource = resource
        self._tag_diffs = tag_diffs
        super().__init__(
            resource=resource, tag_diffs=tag_diffs, properly_tagged=self.properly_tagged
        )

    @property
    def service(self):
        return self._resource.service

    @property
    def region(self):
        return self._resource.region

    @property
    def arn(self):
        return self._resource.arn

    @property
    def type(self):
        return self._resource.resource_type

    @property
    def properly_tagged(self) -> bool:
        return len(
            [
                diff
                for diff in self._tag_diffs
                if self.diff_type_is_proper(diff.diff_type)
            ]
        ) == len(self._tag_diffs)

    @staticmethod
    def diff_type_is_proper(diff_type: TagDiffType) -> bool:
        return (
            diff_type == TagDiffType.EXISTING
            or diff_type == TagDiffType.EXISTING_NOT_IN_SCHEMA
        )
