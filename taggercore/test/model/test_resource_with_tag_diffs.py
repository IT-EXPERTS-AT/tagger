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
from taggercore.model import ResourceWithTagDiffs, Tag, TagDiffType, TagDiff, Resource

diff_for_improperly_tagged_resource = [
    TagDiff(
        Tag("Project", "Super1"), Tag("Project", "Super1"), TagDiffType["EXISTING"]
    ),
    TagDiff(Tag("Owner", "Owner1"), Tag("Owner", "Owner2"), TagDiffType["NEW_VALUE"]),
    TagDiff(Tag(None, None), Tag("Department", "Marketing"), TagDiffType["NEW"]),
]

diff_for_properly_tagged_resource = [
    TagDiff(
        Tag("Project", "Super1"), Tag("Project", "Super1"), TagDiffType["EXISTING"]
    ),
    TagDiff(
        Tag("Created", "Yesterday"),
        Tag(None, None),
        TagDiffType["EXISTING_NOT_IN_SCHEMA"],
    ),
]

tags = [Tag("Project", "Super1"), Tag("Owner", "Owner1"), Tag("Created", "Yesterday")]


class TestResourceWithTagDiffs:
    def test_resource_is_tagged_improperly(self):
        resource_improperly_tagged = ResourceWithTagDiffs(
            Resource(
                "arn:aws:sqs:eu-central-1:111111111111:someq", "someq", "queue", tags
            ),
            diff_for_improperly_tagged_resource,
        )

        assert resource_improperly_tagged.properly_tagged is False

    def test_resource_is_tagged_properly(self):
        resource_properly_tagged = ResourceWithTagDiffs(
            Resource(
                "arn:aws:sqs:eu-central-1:111111111111:someq", "someq", "queue", tags
            ),
            diff_for_properly_tagged_resource,
        )

        assert resource_properly_tagged.properly_tagged is True

    def test_resource_properties(self):
        resource = ResourceWithTagDiffs(
            Resource(
                "arn:aws:sqs:eu-central-1:111111111111:someq", "someq", "queue", tags
            ),
            diff_for_properly_tagged_resource,
        )

        assert resource.region == "eu-central-1"
        assert resource.type == "queue"
        assert resource.service == "sqs"
        assert resource.arn == "arn:aws:sqs:eu-central-1:111111111111:someq"
