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
from .tag import Tag
from .tag_diff_type import TagDiffType


class TagDiff(dict):
    def __init__(self, old_tag: Tag, new_tag: Tag, diff_type: TagDiffType):
        super().__init__(self, old_tag=old_tag, new_tag=new_tag, diff_type=diff_type)
        self._old_tag = old_tag
        self._new_tag = new_tag
        self._diff_type = diff_type

    def __repr__(self):
        return (
            f"{{Old: {self._old_tag}, New: {self._new_tag}, Type: {self._diff_type} }}"
        )

    def __eq__(self, other):
        return (
            self._old_tag == other.old_tag
            and self.new_tag == other.new_tag
            and self._diff_type == other.diff_type
        )

    def __key(self):
        return self._old_tag, self._new_tag, self._diff_type

    def __hash__(self):
        return hash(self.__key())

    @property
    def old_tag(self) -> Tag:
        return self._old_tag

    @property
    def new_tag(self) -> Tag:
        return self._new_tag

    @property
    def diff_type(self) -> TagDiffType:
        return self._diff_type
