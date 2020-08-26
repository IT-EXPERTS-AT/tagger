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

from .tag import Tag
from .tag_diff import TagDiff
from .tag_diff_type import TagDiffType


class Resource(dict):
    def __init__(
        self, arn: str, id: str, resource_type: str, current_tags: List[Tag], **kwargs
    ):
        self._arn = arn
        self._id = id
        splitted_arn = arn.split(":")
        self._service = splitted_arn[2]
        self._region = splitted_arn[3]
        self._resource_type = resource_type
        self._current_tags = current_tags
        self._kwargs = kwargs
        super().__init__(
            self,
            arn=self.arn,
            id=self.id,
            region=self.region,
            service=self.service,
            resource_type=self.resource_type,
            current_tags=self.current_tags,
            name=self._kwargs.get("name"),
        )

    def __repr__(self):
        return f"[Arn {self.arn}, Tags: {len(self._current_tags)}]"

    def __eq__(self, other):
        return self._arn == other.arn

    def __key(self):
        return self.arn

    def __hash__(self):
        return hash(self.__key())

    @property
    def service(self):
        return self._service

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, region):
        self._region = region

    @property
    def resource_type(self):
        return self._resource_type

    @property
    def arn(self):
        return self._arn

    @arn.setter
    def arn(self, arn):
        self._arn = arn

    @property
    def id(self):
        return self._id

    @property
    def current_tags(self):
        return self._current_tags

    @property
    def kwargs(self):
        return self._kwargs

    def compare_tags(self, new_tags: List[Tag]) -> List[TagDiff]:
        diffs = []
        for tag in new_tags:
            if tag in self._current_tags:
                diffs.append(TagDiff(tag, tag, TagDiffType["EXISTING"]))
            else:
                if tag.key in [tag.key for tag in self._current_tags]:
                    diffs.append(
                        TagDiff(
                            next(t for t in self._current_tags if t.key == tag.key),
                            tag,
                            TagDiffType["NEW_VALUE"],
                        )
                    )
                else:
                    diffs.append(TagDiff(Tag(None, None), tag, TagDiffType["NEW"]))

        for tag in self._current_tags:
            if tag.key not in [tag.key for tag in new_tags]:
                diffs.append(
                    TagDiff(tag, Tag(None, None), TagDiffType["EXISTING_NOT_IN_SCHEMA"])
                )

        return diffs
