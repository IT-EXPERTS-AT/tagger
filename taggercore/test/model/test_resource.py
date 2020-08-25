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
from taggercore.model import TagDiff, Tag, Resource, TagDiffType


class TestResource:
    def test_tag_comparison(self):
        expected = [
            TagDiff(
                Tag("Project", "Super1"),
                Tag("Project", "Super1"),
                TagDiffType["EXISTING"],
            ),
            TagDiff(
                Tag("Owner", "Owner1"), Tag("Owner", "Owner2"), TagDiffType["NEW_VALUE"]
            ),
            TagDiff(
                Tag(None, None), Tag("Department", "Marketing"), TagDiffType["NEW"]
            ),
            TagDiff(
                Tag("Created", "Yesterday"),
                Tag(None, None),
                TagDiffType["EXISTING_NOT_IN_SCHEMA"],
            ),
        ]

        actual = Resource(
            "arn:aws:ec2:eu-west-1:111111111111:network-acl/acl-abc",
            "acl-abc",
            "network-acl",
            [
                Tag("Project", "Super1"),
                Tag("Owner", "Owner1"),
                Tag("Created", "Yesterday"),
            ],
        ).compare_tags(
            [
                Tag("Project", "Super1"),
                Tag("Owner", "Owner2"),
                Tag("Department", "Marketing"),
            ]
        )

        assert len(actual) == len(expected)
        assert (
            next(diff for diff in actual if diff.diff_type == TagDiffType.EXISTING)
            == expected[0]
        )
        assert (
            next(diff for diff in actual if diff.diff_type == TagDiffType.NEW_VALUE)
            == expected[1]
        )
        assert (
            next(diff for diff in actual if diff.diff_type == TagDiffType.NEW)
            == expected[2]
        )
        assert (
            next(
                diff
                for diff in actual
                if diff.diff_type == TagDiffType.EXISTING_NOT_IN_SCHEMA
            )
            == expected[3]
        )
